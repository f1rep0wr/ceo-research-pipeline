"""Prompts tailored to the bank CEO project schema."""

from __future__ import annotations

from textwrap import indent
from typing import List

from src.prompts.ceo_research_prompts import CEOResearchPrompts

from .bank_ceo_profile import original_headers


def _format_field_list(fields: List[str]) -> str:
    formatted = "\n".join(f"- \"{field}\"" for field in fields)
    return indent(formatted, "    ")


class BankCEOProjectPrompts:
    """Light wrapper that augments existing prompts with schema guidance."""

    def __init__(self) -> None:
        self._base = CEOResearchPrompts()
        self._field_names = [name for name in original_headers()]

    def get_comprehensive_prompt(self, ceo_name: str, company_name: str) -> str:
        base = self._base.get_comprehensive_single_prompt(ceo_name, company_name)
        schema_section = (
            "\n\n---\n"
            "Return ONLY a JSON object using the following column names "
            "(case-sensitive). Use null when information cannot be verified.\n"
            f"Required keys include:\n{_format_field_list(self._field_names)}\n"
            "It is acceptable to leave keys as null when data is unavailable."
        )
        return base + schema_section


__all__ = ["BankCEOProjectPrompts"]
