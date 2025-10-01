"""Quick sanity-check helper for the bank CEO project tooling."""

from __future__ import annotations

from pathlib import Path

from .data_utils import load_project_dataset


def main() -> None:
    dataset = load_project_dataset(Path("improvements/bank_ceo_project.csv"))
    sample = ", ".join(str(k) for k in dataset.keyids[:2]) or "(no sample)"
    print(f"Dataset rows: {len(dataset.keyids)}. Sample KEYIDs: {sample}.")


if __name__ == "__main__":
    main()
