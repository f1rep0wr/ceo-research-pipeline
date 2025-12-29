"""Utility helpers for the bank CEO project dataset."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from itertools import zip_longest
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from .bank_ceo_profile import BankCEOProfile, from_csv_row, to_csv_row


@dataclass
class ProjectDataset:
    categories: List[str]
    headers: List[str]
    keyids: List[int]
    _profiles: Dict[int, BankCEOProfile]

    def get_profile(self, keyid: int) -> BankCEOProfile:
        if keyid not in self._profiles:
            raise KeyError(f"KEYID {keyid} not found")
        return self._profiles[keyid]

    def update_profile(self, keyid: int, profile: BankCEOProfile) -> None:
        if keyid not in self._profiles:
            self.keyids.append(keyid)
        self._profiles[keyid] = profile

    def iter_profiles(self) -> Iterable[Tuple[int, BankCEOProfile]]:
        for keyid in self.keyids:
            yield keyid, self._profiles[keyid]


def load_project_dataset(path: Path) -> ProjectDataset:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        categories = next(reader)
        headers = next(reader)
        profiles: Dict[int, BankCEOProfile] = {}
        order: List[int] = []
        for row in reader:
            if not any(row):
                continue
            row_dict = {
                header: value
                for header, value in zip_longest(headers, row, fillvalue="")
            }
            keyid_raw = row_dict.get("KEYID")
            if not keyid_raw:
                continue
            try:
                keyid = int(keyid_raw)
            except ValueError:
                continue
            profile = from_csv_row(row_dict)
            profiles[keyid] = profile
            order.append(keyid)
    return ProjectDataset(categories=categories, headers=headers, keyids=order, _profiles=profiles)


def _format_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    return str(value)


def write_project_dataset(dataset: ProjectDataset, path: Path) -> None:
    rows: List[List[str]] = []
    for keyid in dataset.keyids:
        profile = dataset.get_profile(keyid)
        row_dict = to_csv_row(profile)
        row = [_format_value(row_dict.get(header)) for header in dataset.headers]
        rows.append(row)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(dataset.categories)
        writer.writerow(dataset.headers)
        writer.writerows(rows)



def apply_incremental_update(input_path: Path, output_path: Path, update: Tuple[int, BankCEOProfile]) -> None:
    """Persist a single profile update to the dataset CSV using simple upsert logic."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    source_path = output_path if output_path.exists() else input_path
    dataset = load_project_dataset(source_path)

    keyid, profile = update
    dataset.update_profile(keyid, profile)

    write_project_dataset(dataset, output_path)

__all__ = [
    "ProjectDataset",
    "load_project_dataset",
    "write_project_dataset",
    "apply_incremental_update",
]
