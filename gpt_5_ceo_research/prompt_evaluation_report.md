# CEO Research Prompts Evaluation Report

## Executive Summary

This report evaluates the CEO research prompts against established best practices for LLM prompting. The prompts show strong adherence to many best practices but have opportunities for improvement in several areas.

**Overall Score: 7.5/10** - Good implementation with room for optimization

---

## Strengths (What's Working Well)

### 1. **Clear Role Definition** ✅
- Each prompt starts with explicit role setting: "You are a financial researcher..."
- Establishes expertise context for better responses

### 2. **Structured Output Format** ✅
- All prompts specify exact JSON structure with field names
- Clear data types and null handling ("string or null", "true/false/null")
- Consistent format across all stages

### 3. **Progressive Complexity** ✅
- Breaks complex research into 4 focused stages
- Each stage builds on previous information
- Avoids overwhelming the model with too many requirements at once

### 4. **Explicit Classification Rules** ✅
```python
# Good example from line 37-40:
CRITICAL CLASSIFICATION RULES:
- INSIDER: Worked at the company BEFORE becoming CEO (promoted from within)
- OUTSIDER: Hired as CEO from outside (first role at company was CEO)
- UNKNOWN: Cannot determine from available information
```

### 5. **Source Citation Requirements** ✅
- Strong emphasis on verifiable sources throughout
- Requires direct URLs for all facts
- Minimum source requirements (3-5 sources)

### 6. **Conditional Logic** ✅
- Different prompts for insider vs outsider CEOs
- Fallback prompt for unknown classification
- Smart routing based on initial classification

---

## Areas for Improvement

### 1. **Prompt Length** ⚠️
**Issue**: Some prompts are very long (comprehensive prompt is 65+ lines)
**Best Practice**: Keep prompts concise while maintaining clarity
**Recommendation**:
```python
# Instead of repeating instructions, use a base template:
BASE_REQUIREMENTS = """
- Use web search extensively
- Return ONLY valid JSON
- Include source_urls for all facts
"""

def get_prompt(stage, specific_requirements):
    return f"{specific_requirements}\n\n{BASE_REQUIREMENTS}"
```

### 2. **Redundant Instructions** ⚠️
**Issue**: Source requirements repeated in every prompt
**Impact**: Increases token usage and processing time
**Fix**: Create a shared source instruction block

### 3. **Few-Shot Examples Missing** ❌
**Issue**: No examples of correct output provided
**Best Practice**: Include 1-2 examples of ideal responses
**Recommendation**:
```python
EXAMPLE_OUTPUT = """
Example of correct JSON response:
{
    "ceo_name": "Jamie Dimon",
    "company_name": "JPMorgan Chase",
    "insider_outsider": "outsider",
    "source_urls": ["https://www.sec.gov/Archives/...", "https://www.jpmorganchase.com/..."]
    ...
}
"""
```

### 4. **Ambiguous Date Formats** ⚠️
**Issue**: Mixed date format requirements (MM/DD/YYYY vs YYYY)
**Fix**: Standardize to ISO format (YYYY-MM-DD) throughout

### 5. **Inconsistent Confidence Metrics** ⚠️
**Issue**: Different confidence fields across prompts
- `insider_outsider_confidence`: "HIGH/MEDIUM/LOW/CONFLICTING"
- `confidence_score`: "0.0 to 1.0"
**Recommendation**: Use consistent numeric scoring (0.0-1.0)

### 6. **Missing Error Handling Guidance** ❌
**Issue**: No instructions for handling API failures or missing data
**Add**:
```python
"If web search fails or returns no results:
- Mark field as null
- Set confidence_score to 0.1
- Note issue in 'notes' field"
```

### 7. **Chain-of-Thought Not Leveraged** ❌
**Issue**: Direct to JSON output without reasoning steps
**Best Practice**: Use CoT for complex decisions
**Improvement**:
```python
"First, determine the classification:
1. Check if person worked at company before CEO role
2. If yes -> INSIDER, if no -> OUTSIDER
3. If uncertain -> UNKNOWN

Then, gather supporting evidence...
Finally, format as JSON:"
```

---

## Specific Prompt Analysis

### Basic Info Prompt (Lines 27-83)
**Strengths**: Clear classification rules, comprehensive field list
**Weaknesses**:
- Very long (56 lines)
- Repeats source requirements multiple times
- Could benefit from examples

### Career Details Prompts (Lines 86-280)
**Strengths**: Tailored to insider/outsider/unknown cases
**Weaknesses**:
- Complex boolean logic without examples
- Redundant field definitions across variants

### Comprehensive Single Prompt (Lines 327-398)
**Strengths**: Complete all-in-one option
**Weaknesses**:
- Too long (71 lines)
- Tries to do too much in one pass
- High cognitive load for model

---

## Recommendations

### 1. **Create Prompt Templates**
```python
class PromptTemplates:
    BASE_INSTRUCTION = "You are a financial researcher. Use web search extensively."
    SOURCE_REQUIREMENTS = "Include all source_urls..."
    JSON_FORMAT = "Return ONLY valid JSON..."

    @staticmethod
    def build_prompt(role, task, fields, examples=None):
        # Compose prompts from reusable components
        pass
```

### 2. **Add Progressive Reasoning**
```python
"Step 1: Identify classification
Step 2: Gather evidence
Step 3: Verify sources
Step 4: Format as JSON"
```

### 3. **Implement Prompt Validation**
```python
def validate_prompt_length(prompt: str, max_tokens: int = 2000):
    """Ensure prompts aren't too long"""
    if len(prompt.split()) > max_tokens:
        logger.warning(f"Prompt exceeds {max_tokens} tokens")
```

### 4. **Use Dynamic Field Selection**
```python
def get_required_fields(stage: str, classification: str):
    """Return only relevant fields for each stage/classification"""
    base_fields = ["ceo_name", "company_name", "source_urls"]
    if stage == "insider_career":
        return base_fields + ["last_position_before_ceo", "was_president", ...]
    # etc.
```

### 5. **Add Prompt Caching**
```python
@lru_cache(maxsize=128)
def get_cached_prompt(stage: str, ceo_name: str, company_name: str):
    """Cache frequently used prompts to reduce regeneration"""
    pass
```

---

## Best Practices Scorecard

| Practice | Score | Notes |
|----------|-------|-------|
| Clear Instructions | 9/10 | Very explicit, sometimes too verbose |
| Structured Output | 10/10 | Excellent JSON specification |
| Role Definition | 9/10 | Clear expert role established |
| Examples | 0/10 | No few-shot examples provided |
| Conciseness | 5/10 | Prompts are quite long |
| Error Handling | 3/10 | Limited guidance on failures |
| Progressive Complexity | 9/10 | Excellent stage-based approach |
| Source Attribution | 10/10 | Strong emphasis on citations |
| Consistency | 7/10 | Some inconsistencies in formats |
| Chain-of-Thought | 2/10 | Not leveraging CoT reasoning |

---

## Priority Improvements

1. **High Priority**:
   - Add 1-2 examples per prompt
   - Reduce redundancy with shared components
   - Standardize date and confidence formats

2. **Medium Priority**:
   - Implement chain-of-thought reasoning
   - Add error handling instructions
   - Create prompt templates

3. **Low Priority**:
   - Optimize token usage
   - Add prompt validation
   - Implement caching

---

## Conclusion

The CEO research prompts demonstrate solid prompt engineering fundamentals with excellent structure, clear requirements, and progressive complexity. The main opportunities for improvement center on reducing redundancy, adding examples, and leveraging chain-of-thought reasoning. With these enhancements, the system could achieve faster response times, better accuracy, and reduced token costs while maintaining high-quality research output.