"""Tests for batch export locking to ensure multi-run CLI safety."""

import asyncio
import csv
import logging
from pathlib import Path
from typing import List

import pytest

from batch_research_ceo import _export_to_batch_csv


class _StubProfile:
    """Small stand-in for the real CEO profile used in export tests."""

    def __init__(self, label: str) -> None:
        self._label = label

    def to_csv_row_with_separate_sources(self, max_sources: int = 30) -> dict:
        # Only the fields referenced by the exporter are required here.
        return {
            "personname": self._label,
            "companyname": f"TestCo {self._label}",
            "total_sources": 0,
        }

    def to_csv_rows_by_source(self) -> List[dict]:
        # The real object exposes this helper; the exporter may call it when verbose logging is enabled.
        return []


@pytest.mark.asyncio
async def test_export_uses_lock_for_concurrent_writes(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Ensure the async file lock serialises concurrent writes to one CSV."""

    logging.info("Starting concurrent export lock test")

    target_csv = tmp_path / "shared.csv"
    profiles = [_StubProfile(f"Profile {i}") for i in range(5)]

    caplog.set_level(logging.INFO)

    logging.info("Launching %s export tasks", len(profiles))

    # Kick off several export operations at once to simulate multiple CLI runs targeting the same output file.
    await asyncio.gather(*[
        _export_to_batch_csv(profile, target_csv, verbose=True)
        for profile in profiles
    ])

    logging.info("All export tasks have completed")

    assert target_csv.exists(), "expected export to create the CSV file"

    with target_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    logging.info("CSV now holds %s data rows", len(rows))

    assert len(rows) == len(profiles)
    assert {row["personname"] for row in rows} == {p._label for p in profiles}

    logging.info("Export lock test finished successfully")