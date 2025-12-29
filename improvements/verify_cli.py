"""Dataset verification CLI for the bank CEO project.
Supports three tiers: quick field checks, source fetch verification, and optional GPT-5 deep verification."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from . import data_utils
from .bank_ceo_profile import BankCEOProfile
from src.config.settings import Settings
from src.clients.gpt5_client import GPT5ResponsesClient
from src.utils.web_fetch import web_fetch_tool


# ------------------------
# Argument parsing helpers
# ------------------------

def _parse_keyids(keyid_arg: Optional[str]) -> Set[int]:
    if not keyid_arg:
        return set()
    values: Set[int] = set()
    for piece in keyid_arg.split(','):
        cleaned = piece.strip()
        if not cleaned:
            continue
        try:
            values.add(int(cleaned))
        except ValueError:
            raise ValueError(f"Invalid KEYID value: {cleaned}")
    return values


def _parse_keyid_range(range_arg: Optional[str]) -> Set[int]:
    if not range_arg:
        return set()
    bounds = range_arg.split('-')
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


# ------------------------
# Verification primitives
# ------------------------

async def _fetch_with_responses(
    client: Optional[GPT5ResponsesClient], url: str, ceo_name: str, company_name: str
) -> Optional[str]:
    if not client or not client.is_ready:
        return None

    prompt = (
        "You are verifying a research citation.\n"
        "Follow the exact URL below and provide a short, plain-text summary of facts you can confirm.\n"
        "If the page cannot be accessed, reply with ACCESS_FAILED.\n"
        f"URL: {url}\n"
        "Focus on whether the page references the executive or company.\n"
    )

    try:
        response = await client.create_response(
            prompt=prompt,
            reasoning_effort="low",
            tools=[{"type": "web_search"}],
            verbosity="low",
        )
        return _extract_text_from_response(response)
    except Exception:
        return None


def _extract_text_from_response(response) -> Optional[str]:
    try:
        if hasattr(response, "output") and response.output:
            for item in reversed(response.output):
                content = getattr(item, "content", None)
                if not content:
                    continue
                for piece in content:
                    text = getattr(piece, "text", None)
                    if text:
                        return text
        if hasattr(response, "output_text") and response.output_text:
            return response.output_text
    except Exception:
        pass
    return None


async def _verify_source_url(
    url: str,
    ceo_name: str,
    company_name: str,
    use_responses: bool,
    client: Optional[GPT5ResponsesClient],
) -> Dict[str, str]:
    result: Dict[str, str] = {
        "url": url,
        "status": "fetch_failed",
        "method": "http",
        "notes": "",
        "snippet": "",
    }

    tokens = [token for token in (ceo_name, company_name) if token]
    fetched_text = ""

    try:
        fetched_text = await web_fetch_tool(url)
        if fetched_text:
            result["method"] = "http/playwright"
    except Exception as exc:
        result["notes"] = f"Fetch error: {exc}"

    if not fetched_text and use_responses:
        responses_text = await _fetch_with_responses(client, url, ceo_name, company_name)
        if responses_text:
            fetched_text = responses_text
            result["method"] = "responses"

    if not fetched_text:
        if not result["notes"]:
            result["notes"] = "Unable to retrieve content"
        return result

    snippet = fetched_text.strip()
    if len(snippet) > 1200:
        snippet = snippet[:1200] + " ..."
    result["snippet"] = snippet
    lowered = fetched_text.lower()
    matches = {token: token.lower() in lowered for token in tokens}

    if tokens and all(matches.values()):
        result["status"] = "verified"
        result["notes"] = "All tokens present"
    elif tokens and any(matches.values()):
        present = [token for token, matched in matches.items() if matched]
        missing = [token for token, matched in matches.items() if not matched]
        result["status"] = "partial"
        result["notes"] = f"Tokens found: {', '.join(present)}; missing: {', '.join(missing)}"
    else:
        result["status"] = "not_found"
        result["notes"] = "No key tokens detected"

    return result


def _collect_source_urls(profile: BankCEOProfile, max_sources: int) -> List[str]:
    data = profile.model_dump()
    urls: List[str] = []

    # Standard source columns source1..sourceN
    for idx in range(1, max_sources + 1):
        value = data.get(f"source{idx}")
        if isinstance(value, str) and value.strip().lower().startswith("http"):
            urls.append(value.strip())

    # Additional list field if available
    extra = data.get("source_urls")
    if isinstance(extra, list):
        for entry in extra:
            if isinstance(entry, str) and entry.strip().lower().startswith("http"):
                urls.append(entry.strip())

    # Deduplicate preserving order
    seen = set()
    unique_urls: List[str] = []
    for url in urls:
        if url.lower() in seen:
            continue
        seen.add(url.lower())
        unique_urls.append(url)
    return unique_urls


def _basic_field_checks(profile: BankCEOProfile) -> List[str]:
    data = profile.model_dump()
    issues: List[str] = []

    ceo_name = (data.get("personname") or data.get("firstname") or "").strip()
    company = (data.get("companyname") or data.get("company_name_wrds_clean") or "").strip()
    if not ceo_name:
        issues.append("Missing personname/firstname")
    if not company:
        issues.append("Missing companyname/company_name_wrds_clean")

    insider_flag = data.get("insider")
    outsider_flag = data.get("outsider")
    if insider_flag in (1, "1", True) and outsider_flag in (1, "1", True):
        issues.append("Both insider and outsider flags are true")

    start = (data.get("startdateadjwrds") or data.get("startyearadj"))
    departure = (data.get("enddateadjwrds") or data.get("endyearadj"))
    if not start:
        issues.append("Missing start date/year")
    if not departure and data.get("currentflag") not in (1, "1", True):
        issues.append("Missing end date/year for non-current CEO")

    return issues


def _gather_tokens(profile: BankCEOProfile) -> Tuple[str, str]:
    data = profile.model_dump()
    ceo_name = (data.get("personname") or data.get("firstname") or "").strip()
    company = (data.get("companyname") or data.get("company_name_wrds_clean") or "").strip()
    return ceo_name, company

async def _run_deep_verification(
    client: GPT5ResponsesClient,
    profile: BankCEOProfile,
    source_results: List[Dict[str, str]],
    fields_to_check: List[str],
) -> Dict[str, str]:
    data = profile.model_dump()
    field_lines: List[str] = []
    for field in fields_to_check:
        value = data.get(field)
        if isinstance(value, list):
            cleaned = "; ".join(str(item) for item in value)
        else:
            cleaned = "" if value is None else str(value)
        field_lines.append(f"{field}: {cleaned}")

    snippets: List[str] = []
    for result in source_results:
        snippet = result.get("snippet", "")
        if not snippet:
            continue
        collapsed = " ".join(snippet.split())
        if len(collapsed) > 500:
            collapsed = collapsed[:500] + " ..."
        snippets.append(f"{result.get('url', 'unknown URL')} -> {collapsed}")
        if len(snippets) >= 5:
            break

    if not snippets:
        return {"status": "skipped", "reason": "No source text available for deep verification"}

    prompt = (
        "You are validating a bank CEO dataset row.\n"
        "Decide if the provided fields are supported by the source excerpts.\n"
        "Respond with one bullet per field using the format '- FIELD: SUPPORTED/UNSUPPORTED/UNKNOWN - justification'.\n"
        "\nFields:\n"
        + "\n".join(field_lines)
        + "\n\nSource excerpts:\n"
        + "\n".join(snippets)
    )

    try:
        response = await client.create_response(
            prompt=prompt,
            reasoning_effort="low",
            verbosity="low",
        )
        analysis = _extract_text_from_response(response)
        if not analysis:
            return {"status": "error", "reason": "Empty response from GPT-5"}
        return {"status": "completed", "analysis": analysis.strip()}
    except Exception as exc:
        return {"status": "error", "reason": f"GPT-5 call failed: {exc}"}


def _write_markdown_report(path: Path, reports: List[Dict[str, Any]], summary: Dict[str, int]) -> None:
    lines: List[str] = []
    lines.append("# Verification Report")
    lines.append(f"_Generated: {datetime.now(timezone.utc).isoformat()}Z_")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Profiles checked: {summary.get('profiles', 0)}")
    lines.append(f"- Field issues detected: {summary.get('field_issues', 0)}")
    lines.append(f"- Sources needing attention: {summary.get('source_flags', 0)}")
    if summary.get('deep_runs', 0):
        lines.append(f"- Deep verification runs: {summary.get('deep_runs', 0)}")
    lines.append("")

    for report in reports:
        lines.append(f"## {report['header']}")
        lines.append("")

        lines.append("### Field Issues")
        issues = report.get("field_issues", [])
        if issues:
            for item in issues:
                lines.append(f"- {item}")
        else:
            lines.append("- None")
        lines.append("")

        lines.append("### Source Checks")
        sources = report.get("source_results", [])
        if sources:
            lines.append("| URL | Status | Method | Notes |")
            lines.append("| --- | --- | --- | --- |")
            for res in sources:
                url = str(res.get("url", "")).replace("|", "\\|")
                status = res.get("status", "")
                method = res.get("method", "")
                notes = str(res.get("notes", "")).replace("|", "\\|")
                lines.append(f"| {url} | {status} | {method} | {notes} |")
        else:
            lines.append("No sources checked.")
        lines.append("")

        deep_result = report.get("deep_result")
        if deep_result:
            lines.append("### Deep Verification")
            status = deep_result.get("status", "unknown")
            lines.append(f"*Status*: {status}")
            analysis = deep_result.get("analysis")
            reason = deep_result.get("reason")
            if analysis:
                lines.append("")
                lines.append("```")
                lines.append(analysis.replace(chr(10), "\n"))
                lines.append("```")
            elif reason:
                lines.append(f"*Reason*: {reason}")
            lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ------------------------
# CLI Implementation
# ------------------------

def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify bank CEO dataset rows against their cited sources")
    parser.add_argument(
        "--input",
        default="improvements/bank_ceo_project_updated.csv",
        help="Path to the dataset CSV"
    )
    parser.add_argument(
        "--output-report",
        help="Optional Markdown file to write a detailed verification report"
    )
    parser.add_argument(
        "--keyid",
        help="Comma-separated KEYIDs to verify"
    )
    parser.add_argument(
        "--keyid-range",
        help="Inclusive KEYID range like 5000-5010"
    )
    parser.add_argument(
        "--max-sources",
        type=int,
        default=6,
        help="Maximum number of source columns (source1..sourceN) to check"
    )
    parser.add_argument(
        "--skip-sources",
        action="store_true",
        help="Skip fetching and verifying source URLs"
    )
    parser.add_argument(
        "--responses-fallback",
        action="store_true",
        help="Use GPT-5 Responses API when HTTP/Playwright fetch fails"
    )
    parser.add_argument(
        "--deep-verify",
        action="store_true",
        help="Run GPT-5 based deep verification on flagged rows"
    )
    parser.add_argument(
        "--fields",
        help="Comma-separated field names to confirm during deep verification"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of KEYIDs verified"
    )
    return parser


async def _run_verification(args: argparse.Namespace) -> int:
    csv_path = Path(args.input)
    if not csv_path.exists():
        print(f"Input CSV not found: {csv_path}")
        return 1

    dataset = data_utils.load_project_dataset(csv_path)
    explicit = _parse_keyids(args.keyid)
    ranged = _parse_keyid_range(args.keyid_range)
    targets = _determine_targets(dataset.keyids, explicit, ranged)

    if args.limit is not None:
        targets = targets[: args.limit]

    if not targets:
        print("No matching KEYIDs found for verification.")
        return 1

    fields_to_check: List[str] = []
    if args.fields:
        fields_to_check = [field.strip() for field in args.fields.split(',') if field.strip()]
    if not fields_to_check:
        fields_to_check = ["appointment_date", "insider", "outsider"]

    client: Optional[GPT5ResponsesClient] = None
    if args.responses_fallback or args.deep_verify:
        settings = Settings()
        client = GPT5ResponsesClient(settings)
        if not client.is_ready:
            print("[WARN] GPT-5 API key not available; OpenAI-based steps will be skipped.")
            client = None

    total_issues = 0
    total_unverified = 0
    deep_runs = 0
    reports: List[Dict[str, Any]] = []

    for keyid in targets:
        profile = dataset.get_profile(keyid)
        ceo_name, company = _gather_tokens(profile)
        header = f"KEYID {keyid} :: {ceo_name or 'UNKNOWN'} @ {company or 'UNKNOWN'}"
        print("=" * len(header))
        print(header)
        print("=" * len(header))

        profile_report: Dict[str, Any] = {
            "keyid": keyid,
            "header": header,
            "field_issues": [],
            "source_results": [],
            "deep_result": None,
        }
        reports.append(profile_report)

        issues = _basic_field_checks(profile)
        profile_report["field_issues"] = issues
        if issues:
            total_issues += len(issues)
            print("Field Issues:")
            for item in issues:
                print(f"  - {item}")
        else:
            print("Field Issues: none detected")

        source_results: List[Dict[str, str]] = []
        if args.skip_sources:
            print("Source verification skipped (flag set).")
        else:
            urls = _collect_source_urls(profile, args.max_sources)
            if not urls:
                print("No sources found for this record.")
            else:
                print("Source checks:")
                for url in urls:
                    result = await _verify_source_url(
                        url,
                        ceo_name,
                        company,
                        args.responses_fallback,
                        client,
                    )
                    source_results.append(result)
                    status = result.get("status", "unknown")
                    notes = result.get("notes", "")
                    method = result.get("method", "")
                    print(f"  - {url}")
                    print(f"      status: {status} via {method}")
                    if notes:
                        print(f"      notes: {notes}")
                    if status != "verified":
                        total_unverified += 1
        profile_report["source_results"] = source_results

        if args.deep_verify and not args.skip_sources:
            needs_deep = bool(issues) or any(r.get("status") != "verified" for r in source_results)
            if needs_deep:
                if client:
                    deep_result = await _run_deep_verification(
                        client,
                        profile,
                        source_results,
                        fields_to_check,
                    )
                else:
                    deep_result = {"status": "skipped", "reason": "GPT-5 client unavailable"}
                profile_report["deep_result"] = deep_result
                status = deep_result.get("status", "skipped")
                if status == "completed":
                    deep_runs += 1
                    print("Deep verification summary:")
                    analysis = deep_result.get("analysis", "")
                    if analysis:
                        print("    ---")
                    for line in analysis.splitlines():
                        print(f"    {line}")
                else:
                    reason = deep_result.get("reason", "no reason provided")
                    print(f"Deep verification {status}: {reason}")

        print()

    print("Summary:")
    print(f"  Profiles checked: {len(targets)}")
    print(f"  Field issues detected: {total_issues}")
    print(f"  Sources needing attention: {total_unverified}")
    if args.deep_verify:
        print(f"  Deep verification runs: {deep_runs}")

    if args.output_report:
        _write_markdown_report(
            Path(args.output_report),
            reports,
            {
                "profiles": len(targets),
                "field_issues": total_issues,
                "source_flags": total_unverified,
                "deep_runs": deep_runs,
            },
        )
        print(f"Report written to {args.output_report}")
    if client:
        await client.close()
    return 0 if total_unverified == 0 else 2

def main() -> None:
    parser = build_cli()
    args = parser.parse_args()
    try:
        exit_code = asyncio.run(_run_verification(args))
    except ValueError as exc:
        parser.error(str(exc))
        return
    except KeyboardInterrupt:
        print("Verification cancelled by user.")
        exit_code = 130
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
