"""CLI for updating the bank CEO project dataset."""

from __future__ import annotations

import argparse
import asyncio
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Iterable, List, Optional, Set, Tuple

from src.ceo_research_progressive import ProgressiveCEOResearcher  # type: ignore

from .bank_ceo_profile import BankCEOProfile, from_ceo_profile
from . import data_utils

DEFAULT_INPUT = "improvements/bank_ceo_project.csv"
DEFAULT_OUTPUT = "improvements/bank_ceo_project_updated.csv"

LOCK_TIMEOUT = 120.0
LOCK_POLL_INTERVAL = 0.25


@asynccontextmanager
async def _locked_dataset_file(target: Path, timeout: float = LOCK_TIMEOUT, poll: float = LOCK_POLL_INTERVAL):
    resolved = target.resolve(strict=False)
    if resolved.suffix:
        lock_path = resolved.with_suffix(resolved.suffix + '.lock')
    else:
        lock_path = resolved.with_name(resolved.name + '.lock')
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f'Timed out waiting for lock on {resolved}')
            await asyncio.sleep(poll)
    try:
        yield
    finally:
        try:
            os.remove(lock_path)
        except FileNotFoundError:
            pass


async def _apply_update_with_lock(
    *, input_path: Path, output_path: Path, update: Tuple[int, BankCEOProfile]
) -> None:
    """Write a single profile update while respecting the shared file lock."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    async with _locked_dataset_file(output_path):
        data_utils.apply_incremental_update(input_path, output_path, update)

    print(f'Updated dataset written to {output_path}')




def _parse_keyids(keyid_arg: Optional[str]) -> Set[int]:
    if not keyid_arg:
        return set()
    values: Set[int] = set()
    for piece in keyid_arg.split(","):
        piece = piece.strip()
        if not piece:
            continue
        try:
            values.add(int(piece))
        except ValueError:
            raise ValueError(f"Invalid KEYID value: {piece}") from None
    return values


def _parse_keyid_range(range_arg: Optional[str]) -> Set[int]:
    if not range_arg:
        return set()
    bounds = range_arg.split("-")
    if len(bounds) != 2:
        raise ValueError("--keyid-range expects START-END")
    start, end = bounds
    start = int(start.strip())
    end = int(end.strip())
    if start > end:
        start, end = end, start
    return set(range(start, end + 1))


def _determine_targets(all_ids: Iterable[int], explicit: Set[int], ranged: Set[int]) -> List[int]:
    if not explicit and not ranged:
        return list(all_ids)
    combined = explicit.union(ranged)
    return [keyid for keyid in all_ids if keyid in combined]


def _resolve_names(profile: BankCEOProfile) -> Optional[tuple[str, str]]:
    data = profile.model_dump()
    ceo_name = data.get("personname") or data.get("firstname")
    company_name = data.get("companyname") or data.get("company_name_wrds_clean")
    if not ceo_name or not company_name:
        return None
    return str(ceo_name), str(company_name)


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bank CEO project updater")
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        help=f"Input CSV file (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Output CSV file",
    )
    parser.add_argument(
        "--keyid",
        help="Comma-separated KEYID list (e.g., 5015,5018)",
    )
    parser.add_argument(
        "--keyid-range",
        help="Inclusive KEYID range (e.g., 5015-5018)",
    )
    parser.add_argument(
        "--reasoning",
        default="medium",
        choices=["minimal", "low", "medium", "high"],
        help="Reasoning effort for GPT-5",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List KEYIDs that would be processed without calling GPT",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=3,
        help="Number of records to process concurrently (default: 3)",
    )
    return parser


async def _run_update(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    output_path = Path(args.output)

    if args.input == DEFAULT_INPUT and output_path.exists():
        input_path = output_path

    dataset = data_utils.load_project_dataset(input_path)
    explicit = _parse_keyids(args.keyid)
    ranged = _parse_keyid_range(args.keyid_range)
    targets = _determine_targets(dataset.keyids, explicit, ranged)

    if not targets:
        print("No matching KEYIDs found.")
        return

    if args.dry_run:
        print(f"Matched {len(targets)} KEYIDs (dry-run).")
        return

    updated_ids: List[int] = []
    skipped: List[int] = []
    ds_lock = asyncio.Lock()

    async def worker(keyid: int) -> None:
        try:
            # Read current profile snapshot
            async with ds_lock:
                profile = dataset.get_profile(keyid)
            names = _resolve_names(profile)
            if not names:
                async with ds_lock:
                    skipped.append(keyid)
                return

            ceo_name, company_name = names

            # Create independent researcher per task for safety
            researcher = ProgressiveCEOResearcher()
            ceo_result = await researcher.research_ceo_progressive(
                ceo_name=ceo_name,
                company_name=company_name,
                reasoning_effort=args.reasoning,
            )
            updated = from_ceo_profile(ceo_result, existing=profile)

            # Update in-memory dataset under lock
            async with ds_lock:
                dataset.update_profile(keyid, updated)
                updated_ids.append(keyid)

            # Persist update with file-level lock
            await _apply_update_with_lock(
                input_path=input_path,
                output_path=output_path,
                update=(keyid, updated),
            )
        except Exception as exc:
            # Minimal error handling: skip on error
            async with ds_lock:
                skipped.append(keyid)

    # Concurrency-lite execution
    sem = asyncio.Semaphore(max(1, args.concurrency))

    async def limited(keyid: int):
        async with sem:
            await worker(keyid)

    tasks = [asyncio.create_task(limited(k)) for k in targets]
    await asyncio.gather(*tasks)

    if not updated_ids:
        if skipped:
            print(f"Skipped {len(skipped)} KEYIDs due to missing CEO/company name.")
        print("No updates were generated; nothing to write.")
        return


    summary_parts = [f"Updated {len(updated_ids)} record(s)."]
    if skipped:
        summary_parts.append(f"Skipped {len(skipped)} due to missing CEO/company name.")
    print(" ".join(summary_parts))


def main() -> None:
    parser = build_cli()
    args = parser.parse_args()
    try:
        asyncio.run(_run_update(args))
    except ValueError as exc:  # simple argument errors
        parser.error(str(exc))


if __name__ == "__main__":
    main()
