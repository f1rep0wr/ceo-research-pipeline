"""Bank-specific CEO profile model and conversion utilities."""



from __future__ import annotations



import json
import re
from math import floor

from pathlib import Path

from typing import Any, Dict, List, Optional



from pydantic import BaseModel, create_model



try:

    from src.models.ceo_profile import CEOProfile  # type: ignore

except ModuleNotFoundError:  # pragma: no cover - fallback for isolated runs

    CEOProfile = None  # type: ignore



SCHEMA_PATH = Path(__file__).with_name("schema_map.json")

SCHEMA = json.loads(SCHEMA_PATH.read_text())

ORIGINAL_TO_INTERNAL: Dict[str, str] = SCHEMA["original_to_internal"]

INTERNAL_TO_ORIGINAL: Dict[str, str] = SCHEMA["internal_to_original"]

INTERNAL_FIELDS: List[str] = list(INTERNAL_TO_ORIGINAL.keys())





class _BankBaseModel(BaseModel):

    """Base config allowing optional fields."""



    class Config:

        arbitrary_types_allowed = True

        extra = "ignore"





additional_fields: Dict[str, Any] = {

    "confidence_score": (Optional[float], None),

    "data_completeness": (Optional[str], None),

}



BankCEOProfile = create_model(  # type: ignore[call-overload]

    "BankCEOProfile",

    __base=_BankBaseModel,

    **{field: (Optional[Any], None) for field in INTERNAL_FIELDS},

    **additional_fields,

)



CONFIDENCE_WARNING = "WARNING: confidence below 0.70 - review sources."





def original_headers() -> List[str]:

    """Return headers in project order."""



    return list(ORIGINAL_TO_INTERNAL.keys())





def _apply_confidence_warning(notes: Optional[str], confidence: Optional[float]) -> Optional[str]:
    if confidence is None:
        return notes
    try:
        value = float(confidence)
    except (TypeError, ValueError):
        return notes
    if value >= 0.7:
        return notes
    if not notes:
        return CONFIDENCE_WARNING
    if CONFIDENCE_WARNING.lower() in notes.lower():
        return notes
    return f"{notes} | {CONFIDENCE_WARNING}"




def _format_confidence_for_correction(score: Optional[float]) -> Optional[str]:
    """Convert confidence score to two-decimal string for correction."""
    if score is None:
        return None
    try:
        value = float(score)
    except (TypeError, ValueError):
        return None
    floored = floor(value * 100) / 100
    return f"{floored:.2f}"

def _assign_if_missing(storage: Dict[str, Any], key: str, value: Any) -> None:
    """Set field when the current value is effectively empty."""
    if value is None:
        return
    current = storage.get(key)
    if current is None:
        storage[key] = value
        return
    if isinstance(current, str) and current.strip() == "":
        storage[key] = value
        return
    if current in ("", [], {}):
        storage[key] = value


BOOLEAN_FIELDS = {
    "insider",
    "outsider",
    "was_ceo_of_other_firms",
    "was_other_executive_of_other_firms",
    "was_unattached_to_any",
    "president",
    "board_member",
    "chairman",
    "ceo_of_subsidiary",
    "other_executive",
    "board_member_only",
    "former_ceo",
    "former_other_executive",
    "as_executive",
    "from_early_career",
    "previous_ceo_experience",
    "career_timeline_verified",
    "succession_documentation",
    "interim_period",
    "departure_voluntary",
    "forced_out",
    "was_forced_out",
    "retired",
    "retirement_status",
    "no_real_job",
    "director_of_some_company",
    "became_ceo_through_merger",
    "interim_ceo",
    "interim_ceo_only",
    "ceo_of_other_firms",
    "other_executive_of_other_firms",
    "unattached_to_any",
    "current_ceo",
}

def _to_year(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        lowered = stripped.lower()
        if lowered in {"now", "current", "incumbent"}:
            return None
        match = re.search(r"(19|20)\d{2}", stripped)
        if match:
            return int(match.group(0))
    return None

def _to_now_or_year(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"incumbent", "current", "ongoing", "present", "now"}:
            return "now"
    year = _to_year(value)
    if year is not None:
        return str(year)
    return None

def _normalize_boolean(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int, float)):
        return 1 if value else 0
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "":
            return None
        if lowered in {"true", "1", "yes", "y"}:
            return 1
        if lowered in {"false", "0", "no", "n"}:
            return 0
    return 1 if value else 0

def _finalize_profile(base_data: Dict[str, Any], ceo_data: Dict[str, Any]) -> None:
    # Normalize boolean fields
    for field in BOOLEAN_FIELDS:
        if field in base_data:
            normalized = _normalize_boolean(base_data[field])
            base_data[field] = normalized

    # KISS exclusivity for insider pre-CEO roles:
    # Ensure only the most recent internal role is marked true.
    insider_flag = _normalize_boolean(base_data.get("insider"))
    if insider_flag == 1:
        role_fields = [
            "president",
            "board_member",
            "chairman",
            "ceo_of_subsidiary",
            "other_executive",
        ]

        # Determine chosen role from last_position_before_ceo when available
        chosen = None
        last_pos_raw = base_data.get("last_position_before_ceo")
        last_pos = str(last_pos_raw).strip().lower() if isinstance(last_pos_raw, str) else ""

        # If flagged as board_member_only, prefer Board Member
        if _normalize_boolean(base_data.get("board_member_only")) == 1:
            chosen = "board_member"
            base_data["last_position_before_ceo"] = "Board Member"
        elif last_pos:
            if "board" in last_pos:
                chosen = "board_member"
                base_data["last_position_before_ceo"] = "Board Member"
            elif "president" in last_pos:
                chosen = "president"
                base_data["last_position_before_ceo"] = "President"
            elif "chair" in last_pos:
                chosen = "chairman"
                base_data["last_position_before_ceo"] = "Chairman"
            else:
                chosen = "other_executive"
        else:
            # Fallback to priority when last_position_before_ceo is missing
            priority = [
                "board_member",
                "president",
                "chairman",
                "other_executive",
                "ceo_of_subsidiary",
            ]
            for f in priority:
                if _normalize_boolean(base_data.get(f)) == 1:
                    chosen = f
                    break

        # Apply exclusivity (only chosen = 1, others = 0)
        if chosen:
            for f in role_fields:
                base_data[f] = 1 if f == chosen else 0
            # board_member_only should only remain if chosen is board_member
            base_data["board_member_only"] = 1 if chosen == "board_member" else 0
        else:
            for f in role_fields:
                base_data[f] = 0

    for field in BOOLEAN_FIELDS:
        value = base_data.get(field)
        if value == 0 or value == "0":
            base_data[field] = None

    # Derive year insider joined field
    if "year_insider_joined_firm" in base_data:
        year_value = _to_year(base_data.get("year_insider_joined_firm"))
        if year_value is not None:
            base_data["year_insider_joined_firm"] = str(year_value)
        else:
            derived = _to_year(ceo_data.get("year_insider_joined_firm"))
            if derived is not None:
                base_data["year_insider_joined_firm"] = str(derived)
            else:
                base_data["year_insider_joined_firm"] = None

    # begyr CEO
    begyr = base_data.get("begyr_ceo")
    begyr_year = _to_year(begyr)
    if begyr_year is None:
        begyr_year = _to_year(ceo_data.get("start_date")) or _to_year(ceo_data.get("appointment_date"))
    if begyr_year is not None:
        base_data["begyr_ceo"] = str(begyr_year)
    else:
        base_data["begyr_ceo"] = None

    # endyr CEO
    endyr = base_data.get("endyr_ceo")
    end_value = _to_now_or_year(endyr)
    if end_value is None:
        end_value = _to_now_or_year(ceo_data.get("departure_date"))
    if end_value is None and base_data.get("current_ceo") == 1:
        end_value = "now"
    base_data["endyr_ceo"] = end_value if end_value is None else str(end_value)

    # Ensure text fields remain strings
    text_fields = {
        "last_position_before_ceo",
        "previous_title",
        "previous_firm",
        "outsider_job_title",
        "outsider_firm",
        "notes_2",
        "job_title_in_next_company",
        "next_company",
    }
    for field in text_fields:
        value = base_data.get(field)
        if value is None:
            continue
        base_data[field] = str(value).strip()


def from_csv_row(row: Dict[str, Any]) -> BankCEOProfile:

    """Create profile from a project-format CSV row."""



    payload = {internal: row.get(original) for original, internal in ORIGINAL_TO_INTERNAL.items()}

    if "confidence_score" in row:

        try:

            payload["confidence_score"] = float(row["confidence_score"])

        except (TypeError, ValueError):

            payload["confidence_score"] = None

    if "data_completeness" in row:

        payload["data_completeness"] = row["data_completeness"]

    for field in BOOLEAN_FIELDS:
        value = payload.get(field)
        if value is not None:
            payload[field] = _normalize_boolean(value)

    return BankCEOProfile(**payload)





def to_csv_row(profile: BankCEOProfile) -> Dict[str, Any]:

    """Serialize profile to project CSV row ordering."""



    profile_dict = profile.model_dump()

    correction_value = _format_confidence_for_correction(profile_dict.get("confidence_score"))
    if correction_value is not None:
        profile_dict["correction"] = correction_value


    profile_dict["notes_2"] = _apply_confidence_warning(

        profile_dict.get("notes_2"), profile_dict.get("confidence_score")

    )

    return {original: profile_dict.get(internal) for original, internal in ORIGINAL_TO_INTERNAL.items()}





CEOPROFILE_TO_BANK_MAP: Dict[str, str] = {

    "ceo_title": "title",

    "year_insider_joined_firm": "year_insider_joined_firm",

    "last_position_before_ceo": "last_position_before_ceo",

    "outsider_job_title": "outsider_job_title",

    "outsider_firm": "outsider_firm",

    "previous_company": "previous_firm",

    "previous_position": "previous_title",

    "was_ceo_of_other_firms": "ceo_of_other_firms",

    "was_other_executive_of_other_firms": "other_executive_of_other_firms",

    "was_unattached_to_any": "unattached_to_any",

    "was_president": "president",

    "was_board_member": "board_member",

    "was_chairman": "chairman",

    "was_ceo_of_subsidiary": "ceo_of_subsidiary",

    "was_other_executive": "other_executive",

    "was_board_member_only": "board_member_only",

    "was_former_ceo": "former_ceo",

    "was_former_other_executive": "former_other_executive",

    "joined_as_executive": "as_executive",

    "joined_from_early_career": "from_early_career",

    "confidence_score": "confidence_score",

    "data_completeness": "data_completeness",

    "notes": "notes_2",
    "why_incorrect": "why_incorrect",

    "post_ceo_role": "job_title_in_next_company",
    "next_company": "next_company",
    "was_forced_out": "forced_out",
    "retirement_status": "retired",
    "no_real_job": "no_real_job",
    "director_of_some_company": "director_of_some_company",
}





def from_ceo_profile(

    ceo_profile: CEOProfile,

    existing: Optional[BankCEOProfile] = None,

    overrides: Optional[Dict[str, Any]] = None,

) -> BankCEOProfile:

    """Build bank profile from existing CEOProfile, preserving existing values."""



    base_data = existing.model_dump() if existing is not None else {}

    if hasattr(ceo_profile, "model_dump"):

        ceo_data = ceo_profile.model_dump()

    else:  # pragma: no cover - defensive for mocked objects

        ceo_data = dict(ceo_profile.__dict__)



    for source, target in CEOPROFILE_TO_BANK_MAP.items():

        value = ceo_data.get(source)

        if value is None:

            continue

        _assign_if_missing(base_data, target, value)

    source_urls = ceo_data.get("source_urls")
    if isinstance(source_urls, str):
        source_urls = [source_urls]
    if isinstance(source_urls, list):
        cleaned_urls = [str(url).strip() for url in source_urls if str(url).strip()]
        for idx, url in enumerate(cleaned_urls[:6]):
            _assign_if_missing(base_data, f"source{idx + 1}", url)

    primary_sources = ceo_data.get("primary_sources")
    if isinstance(primary_sources, str):
        primary_sources = [primary_sources]
    if isinstance(primary_sources, list):
        cleaned_primary = [str(src).strip() for src in primary_sources if str(src).strip()]
        if cleaned_primary:
            primary_iter = iter(cleaned_primary)
            for idx in range(6):
                field = f"source{idx + 1}"
                current = base_data.get(field)
                if current is None or (isinstance(current, str) and current.strip() == ""):
                    try:
                        _assign_if_missing(base_data, field, next(primary_iter))
                    except StopIteration:
                        break



    name = ceo_data.get("ceo_name")

    if isinstance(name, str) and name.strip():

        _assign_if_missing(base_data, "personname", name)

        parts = name.strip().split()

        _assign_if_missing(base_data, "firstname", parts[0] if parts else name)

        if len(parts) > 1:

            _assign_if_missing(base_data, "lastname", " ".join(parts[1:]))



    company = ceo_data.get("company_name")

    if isinstance(company, str) and company.strip():

        _assign_if_missing(base_data, "companyname", company)

        _assign_if_missing(base_data, "company_name_wrds_clean", company.upper())



    insider_outsider = ceo_data.get("insider_outsider")

    if isinstance(insider_outsider, str):

        flag = insider_outsider.strip().lower()

        if flag == "insider":

            _assign_if_missing(base_data, "insider", 1)

            base_data['outsider'] = 0

        elif flag == "outsider":

            _assign_if_missing(base_data, "outsider", 1)

            base_data['insider'] = 0



    insider_flag = _normalize_boolean(base_data.get("insider"))
    prev_title = base_data.get("previous_title")
    prev_firm = base_data.get("previous_firm")

    prev_title_has_value = bool(isinstance(prev_title, str) and prev_title.strip())
    prev_firm_has_value = bool(isinstance(prev_firm, str) and prev_firm.strip())

    # KISS: For insiders, never keep external previous firm/title
    if insider_flag == 1:
        base_data["previous_title"] = None
        base_data["previous_firm"] = None
    else:
        # Defensive: if either missing or previous_firm equals current company, clear both
        company_val = base_data.get("companyname") or base_data.get("company_name_wrds_clean")
        def _canon(v):
            return str(v).strip().lower() if isinstance(v, str) else ""
        if (not (prev_title_has_value and prev_firm_has_value)) or (_canon(prev_firm) == _canon(company_val)):
            base_data["previous_title"] = None
            base_data["previous_firm"] = None

    last_position = base_data.get("last_position_before_ceo")
    if isinstance(last_position, str) and last_position.strip().lower() == "other executive":
        replacement = base_data.get("previous_title")
        if not (isinstance(replacement, str) and replacement.strip()):
            replacement = ceo_data.get("previous_position")
        if isinstance(replacement, str):
            replacement = replacement.strip()
        if replacement:
            base_data["last_position_before_ceo"] = replacement

    director_flag = base_data.get("director_of_some_company")
    next_title = base_data.get("job_title_in_next_company")
    next_company = base_data.get("next_company")

    has_director_flag = _normalize_boolean(director_flag) == 1
    has_post_ceo_details = bool((isinstance(next_title, str) and next_title.strip()) or (isinstance(next_company, str) and next_company.strip()))

    if has_director_flag and not has_post_ceo_details:
        base_data["director_of_some_company"] = None

    if overrides:

        for key, value in overrides.items():

            if value is not None:

                base_data[key] = value



    _finalize_profile(base_data, ceo_data)

    return BankCEOProfile(**base_data)





__all__ = [

    "BankCEOProfile",

    "CONFIDENCE_WARNING",

    "from_csv_row",

    "to_csv_row",

    "from_ceo_profile",

    "original_headers",

]
