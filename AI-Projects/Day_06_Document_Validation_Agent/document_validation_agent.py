import os
import sys
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel

try:
    import openai
except ImportError:
    openai = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------

class ValidationResult(BaseModel):
    document_type: str
    is_valid: bool
    missing_fields: list[str]
    format_errors: list[str]
    data_mismatches: list[str]
    summary: str


# ---------------------------------------------------------------------------
# Step 1: Load document
# ---------------------------------------------------------------------------

def load_document(file_path: str) -> str:
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"Document file not found: {file_path}")
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Step 2: Call LLM
# ---------------------------------------------------------------------------

def llm_validate_document(document_text: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment")

    if openai is None:
        raise RuntimeError("openai package is not installed. run pip install -r requirements.txt")

    openai.api_key = api_key

    prompt = (
        "You are a document validation expert for Indian tax and financial documents.\n"
        "Analyze the document below and validate it thoroughly.\n\n"
        "Supported document types:\n"
        "  - Form 16 (TDS certificate issued by employer)\n"
        "  - AIS (Annual Information Statement from Income Tax portal)\n"
        "  - Bank Statement\n\n"
        "Check for the following issues:\n"
        "  1. MISSING FIELDS: Required fields that are absent or blank\n"
        "     - Form 16: PAN, TAN, Employee name, Employer name, Assessment Year, "
        "Gross Salary, Tax Deducted, Certificate Number\n"
        "     - AIS: PAN, Name, FY, Income sources, TDS entries\n"
        "     - Bank Statement: Account number, IFSC, Account holder name, "
        "Period (from-to dates), Opening balance, Closing balance\n"
        "  2. FORMAT ERRORS: Values in wrong format (e.g. PAN not 10 chars, "
        "date not DD/MM/YYYY, amounts with invalid symbols)\n"
        "  3. DATA MISMATCHES: Internal inconsistencies (e.g. total tax deducted "
        "does not match sum of monthly deductions, closing balance does not match "
        "calculated balance, AY mismatch between Part A and Part B of Form 16)\n\n"
        "Document text:\n"
        "---\n"
        + document_text
        + "\n---\n\n"
        "Return ONLY a JSON object with these exact keys:\n"
        "  document_type   : one of 'Form 16', 'AIS', 'Bank Statement', or 'Unknown'\n"
        "  is_valid        : true if no issues found, else false\n"
        "  missing_fields  : list of strings describing each missing field\n"
        "  format_errors   : list of strings describing each format error\n"
        "  data_mismatches : list of strings describing each data mismatch\n"
        "  summary         : 1-2 sentence plain-English verdict\n"
    )

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
        temperature=0.2,
    )

    text = response.choices[0].message.content.strip()
    return {"raw": text}


# ---------------------------------------------------------------------------
# Step 3: Parse LLM output
# ---------------------------------------------------------------------------

def parse_llm_output(raw: str) -> ValidationResult:
    import json
    import re

    # Strip markdown code fences if present
    clean = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()

    try:
        data = json.loads(clean)
        return ValidationResult(
            document_type=data.get("document_type", "Unknown"),
            is_valid=bool(data.get("is_valid", False)),
            missing_fields=data.get("missing_fields", []),
            format_errors=data.get("format_errors", []),
            data_mismatches=data.get("data_mismatches", []),
            summary=data.get("summary", raw[:200].strip()),
        )
    except (json.JSONDecodeError, KeyError):
        pass

    # Fallback: line-by-line parsing
    document_type = "Unknown"
    is_valid = False
    missing_fields: list[str] = []
    format_errors: list[str] = []
    data_mismatches: list[str] = []
    summary = ""

    lines = raw.splitlines()
    mode = None
    for line in lines:
        l = line.strip()
        if not l:
            continue
        low = l.lower()

        if low.startswith("document_type") or low.startswith("document type"):
            document_type = l.split(":", 1)[-1].strip().strip('"').strip("'")
            mode = None
            continue
        if low.startswith("is_valid") or low.startswith("is valid"):
            val = l.split(":", 1)[-1].strip().lower()
            is_valid = val in ("true", "yes", "1")
            mode = None
            continue
        if low.startswith("missing_fields") or low.startswith("missing fields"):
            mode = "missing"
            continue
        if low.startswith("format_errors") or low.startswith("format errors"):
            mode = "format"
            continue
        if low.startswith("data_mismatches") or low.startswith("data mismatches"):
            mode = "mismatch"
            continue
        if low.startswith("summary"):
            mode = "summary"
            content = l.split(":", 1)[-1].strip()
            if content:
                summary += " " + content
            continue

        if mode == "missing":
            missing_fields.append(l.lstrip("- ").strip())
        elif mode == "format":
            format_errors.append(l.lstrip("- ").strip())
        elif mode == "mismatch":
            data_mismatches.append(l.lstrip("- ").strip())
        elif mode == "summary":
            summary += " " + l

    if not summary:
        summary = raw[:200].strip()

    return ValidationResult(
        document_type=document_type,
        is_valid=is_valid,
        missing_fields=missing_fields,
        format_errors=format_errors,
        data_mismatches=data_mismatches,
        summary=summary.strip(),
    )


# ---------------------------------------------------------------------------
# Step 4: Orchestrate & display
# ---------------------------------------------------------------------------

def run(file_path: str):
    print(f"\nLoading document: {file_path}")
    document_text = load_document(file_path)

    print("Validating document with AI...")
    llm_result = llm_validate_document(document_text)
    result = parse_llm_output(llm_result.get("raw", ""))

    status_icon = "PASSED" if result.is_valid else "FAILED"

    print("\n" + "=" * 55)
    print(f"  DOCUMENT VALIDATION REPORT  [{status_icon}]")
    print("=" * 55)

    print(f"\nDocument Type : {result.document_type}")
    print(f"Valid         : {'Yes' if result.is_valid else 'No'}")

    print("\n--- Missing Fields ---")
    if result.missing_fields:
        for item in result.missing_fields:
            print(f"  * {item}")
    else:
        print("  (none)")

    print("\n--- Format Errors ---")
    if result.format_errors:
        for item in result.format_errors:
            print(f"  * {item}")
    else:
        print("  (none)")

    print("\n--- Data Mismatches ---")
    if result.data_mismatches:
        for item in result.data_mismatches:
            print(f"  * {item}")
    else:
        print("  (none)")

    print("\n--- Summary ---")
    print(f"  {result.summary}")
    print("=" * 55)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python document_validation_agent.py <document-file>")
        print()
        print("Examples:")
        print("  python document_validation_agent.py sample_data/form16_sample.txt")
        print("  python document_validation_agent.py sample_data/ais_sample.txt")
        print("  python document_validation_agent.py sample_data/bank_statement_sample.txt")
        sys.exit(1)
    run(sys.argv[1])
