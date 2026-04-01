import os
import sys
from typing import Optional
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
# Constants — Indian Tax Rules (FY 2024-25)
# ---------------------------------------------------------------------------

TDS_RULES = {
    "rent": {
        "section": "194IB (Individual/HUF payer)",
        "threshold": 50_000,        # per month; treat input as monthly rent
        "rate_with_pan": 10.0,
        "rate_without_pan": 20.0,
        "note": "Applicable when monthly rent exceeds Rs 50,000",
    },
    "sell": {
        "section": "194IA (Immovable Property)",
        "threshold": 50_00_000,     # Rs 50 lakhs
        "rate_with_pan": 1.0,
        "rate_without_pan": 20.0,
        "note": "Applicable when sale consideration >= Rs 50 lakhs",
    },
    "purchase": {
        "section": "194Q (Purchase of Goods)",
        "threshold": 50_00_000,     # Rs 50 lakhs
        "rate_with_pan": 0.1,
        "rate_without_pan": 5.0,
        "note": "Applicable when purchase value exceeds Rs 50 lakhs",
    },
}

TCS_RULES = {
    "sell": {
        "section": "206C(1H) (Sale of Goods)",
        "threshold": 50_00_000,     # Rs 50 lakhs
        "rate_with_pan": 0.1,
        "rate_without_pan": 1.0,
        "note": "Seller collects TCS on sale of goods exceeding Rs 50 lakhs",
    },
    "purchase": {
        "section": "206C (Buyer bears TCS collected by seller)",
        "threshold": 0,
        "rate_with_pan": 0.0,       # Collected by seller; shown in buyer's 26AS
        "rate_without_pan": 0.0,
        "note": "TCS on purchases is collected by the seller and reflected in buyer's 26AS/AIS",
    },
    "rent": {
        "section": "N/A",
        "threshold": 0,
        "rate_with_pan": 0.0,
        "rate_without_pan": 0.0,
        "note": "TCS is not applicable on rent transactions",
    },
}


# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------

class TaxCalculationResult(BaseModel):
    transaction_type: str
    amount: float
    pan_available: bool

    tds_applicable: bool
    tds_section: str
    tds_rate: float
    tds_amount: float
    tds_note: str

    tcs_applicable: bool
    tcs_section: str
    tcs_rate: float
    tcs_amount: float
    tcs_note: str

    total_tax_deducted: float
    refund_eligible: bool
    refund_note: str

    ai_explanation: str


# ---------------------------------------------------------------------------
# Step 1: Calculate TDS
# ---------------------------------------------------------------------------

def calculate_tds(transaction_type: str, amount: float, pan_available: bool) -> dict:
    rule = TDS_RULES.get(transaction_type)
    if not rule:
        return {
            "applicable": False, "section": "N/A",
            "rate": 0.0, "amount": 0.0,
            "note": "Transaction type not recognised for TDS",
        }

    if amount <= rule["threshold"]:
        return {
            "applicable": False,
            "section": rule["section"],
            "rate": 0.0,
            "amount": 0.0,
            "note": f"Amount Rs {amount:,.2f} does not exceed TDS threshold "
                    f"of Rs {rule['threshold']:,.0f}. {rule['note']}",
        }

    rate = rule["rate_with_pan"] if pan_available else rule["rate_without_pan"]
    tds_amount = (rate / 100) * amount

    return {
        "applicable": True,
        "section": rule["section"],
        "rate": rate,
        "amount": round(tds_amount, 2),
        "note": rule["note"] + (" (Higher rate applied — PAN not available)" if not pan_available else ""),
    }


# ---------------------------------------------------------------------------
# Step 2: Calculate TCS
# ---------------------------------------------------------------------------

def calculate_tcs(transaction_type: str, amount: float, pan_available: bool) -> dict:
    rule = TCS_RULES.get(transaction_type)
    if not rule:
        return {
            "applicable": False, "section": "N/A",
            "rate": 0.0, "amount": 0.0,
            "note": "Transaction type not recognised for TCS",
        }

    # Purchase TCS is not computed here — it's the seller's responsibility
    if transaction_type == "purchase":
        return {
            "applicable": False,
            "section": rule["section"],
            "rate": 0.0,
            "amount": 0.0,
            "note": rule["note"],
        }

    if rule["threshold"] > 0 and amount <= rule["threshold"]:
        return {
            "applicable": False,
            "section": rule["section"],
            "rate": 0.0,
            "amount": 0.0,
            "note": f"Amount Rs {amount:,.2f} does not exceed TCS threshold "
                    f"of Rs {rule['threshold']:,.0f}. {rule['note']}",
        }

    if rule["rate_with_pan"] == 0.0:
        return {
            "applicable": False,
            "section": rule["section"],
            "rate": 0.0,
            "amount": 0.0,
            "note": rule["note"],
        }

    rate = rule["rate_with_pan"] if pan_available else rule["rate_without_pan"]
    tcs_amount = (rate / 100) * amount

    return {
        "applicable": True,
        "section": rule["section"],
        "rate": rate,
        "amount": round(tcs_amount, 2),
        "note": rule["note"] + (" (Higher rate applied — PAN not available)" if not pan_available else ""),
    }


# ---------------------------------------------------------------------------
# Step 3: Determine refund eligibility
# ---------------------------------------------------------------------------

def check_refund_eligibility(tds_amount: float, tcs_amount: float) -> tuple[bool, str]:
    total = tds_amount + tcs_amount
    if total <= 0:
        return (
            False,
            "No TDS/TCS is deducted on this transaction, so no refund entry will appear in ITR.",
        )
    return (
        True,
        f"Rs {total:,.2f} (TDS + TCS) will be reflected in Form 26AS / AIS. "
        "If your total tax liability for the year is less than the total TDS/TCS deducted, "
        "the excess will be refunded when you file your ITR.",
    )


# ---------------------------------------------------------------------------
# Step 4: AI Explanation
# ---------------------------------------------------------------------------

def get_ai_explanation(result: dict, model: str = "gpt-4o-mini") -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "(OpenAI API key not set — AI explanation skipped)"

    if openai is None:
        return "(openai package not installed — AI explanation skipped)"

    openai.api_key = api_key

    prompt = (
        "You are an Indian tax expert assistant. A user has made the following transaction:\n\n"
        f"  Transaction Type : {result['transaction_type'].upper()}\n"
        f"  Amount           : Rs {result['amount']:,.2f}\n"
        f"  PAN Available    : {'Yes' if result['pan_available'] else 'No'}\n\n"
        f"TDS Calculation:\n"
        f"  Applicable : {'Yes' if result['tds_applicable'] else 'No'}\n"
        f"  Section    : {result['tds_section']}\n"
        f"  Rate       : {result['tds_rate']}%\n"
        f"  Amount     : Rs {result['tds_amount']:,.2f}\n\n"
        f"TCS Calculation:\n"
        f"  Applicable : {'Yes' if result['tcs_applicable'] else 'No'}\n"
        f"  Section    : {result['tcs_section']}\n"
        f"  Rate       : {result['tcs_rate']}%\n"
        f"  Amount     : Rs {result['tcs_amount']:,.2f}\n\n"
        f"Refund Eligible: {'Yes' if result['refund_eligible'] else 'No'}\n\n"
        "In 3-4 plain-English sentences, explain:\n"
        "1. Why TDS/TCS is or is not applicable.\n"
        "2. What compliance action the user must take (e.g. deposit TDS, file TDS return).\n"
        "3. How TDS/TCS deducted will help in income tax refund calculation.\n"
        "Keep the explanation simple and practical for a non-expert user."
    )

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        return f"(AI explanation failed: {exc})"


# ---------------------------------------------------------------------------
# Step 5: Orchestrate
# ---------------------------------------------------------------------------

def run(transaction_type: str, amount: float, pan_available: bool) -> TaxCalculationResult:
    transaction_type = transaction_type.lower().strip()

    if transaction_type not in ("rent", "sell", "purchase"):
        print(f"ERROR: Invalid transaction type '{transaction_type}'. Choose rent / sell / purchase.")
        sys.exit(1)

    tds = calculate_tds(transaction_type, amount, pan_available)
    tcs = calculate_tcs(transaction_type, amount, pan_available)
    refund_eligible, refund_note = check_refund_eligibility(tds["amount"], tcs["amount"])

    raw = {
        "transaction_type": transaction_type,
        "amount": amount,
        "pan_available": pan_available,
        "tds_applicable": tds["applicable"],
        "tds_section": tds["section"],
        "tds_rate": tds["rate"],
        "tds_amount": tds["amount"],
        "tds_note": tds["note"],
        "tcs_applicable": tcs["applicable"],
        "tcs_section": tcs["section"],
        "tcs_rate": tcs["rate"],
        "tcs_amount": tcs["amount"],
        "tcs_note": tcs["note"],
        "total_tax_deducted": round(tds["amount"] + tcs["amount"], 2),
        "refund_eligible": refund_eligible,
        "refund_note": refund_note,
        "ai_explanation": "",
    }

    raw["ai_explanation"] = get_ai_explanation(raw)

    result = TaxCalculationResult(**raw)
    display(result)
    return result


# ---------------------------------------------------------------------------
# Step 6: Display
# ---------------------------------------------------------------------------

def display(r: TaxCalculationResult):
    sep = "=" * 60

    print()
    print(sep)
    print("  TDS / TCS CALCULATOR — INDIA (FY 2024-25)")
    print(sep)
    print(f"  Transaction Type : {r.transaction_type.upper()}")
    print(f"  Amount           : Rs {r.amount:>15,.2f}")
    print(f"  PAN Available    : {'Yes' if r.pan_available else 'No (Higher rate applied)'}")

    print()
    print("─" * 60)
    print("  TDS (Tax Deducted at Source)")
    print("─" * 60)
    print(f"  Applicable : {'YES' if r.tds_applicable else 'NO'}")
    print(f"  Section    : {r.tds_section}")
    if r.tds_applicable:
        print(f"  Rate       : {r.tds_rate}%")
        print(f"  TDS Amount : Rs {r.tds_amount:>12,.2f}")
    print(f"  Note       : {r.tds_note}")

    print()
    print("─" * 60)
    print("  TCS (Tax Collected at Source)")
    print("─" * 60)
    print(f"  Applicable : {'YES' if r.tcs_applicable else 'NO'}")
    print(f"  Section    : {r.tcs_section}")
    if r.tcs_applicable:
        print(f"  Rate       : {r.tcs_rate}%")
        print(f"  TCS Amount : Rs {r.tcs_amount:>12,.2f}")
    print(f"  Note       : {r.tcs_note}")

    print()
    print("─" * 60)
    print("  Total Tax Deducted / Collected")
    print("─" * 60)
    print(f"  TDS        : Rs {r.tds_amount:>12,.2f}")
    print(f"  TCS        : Rs {r.tcs_amount:>12,.2f}")
    print(f"  TOTAL      : Rs {r.total_tax_deducted:>12,.2f}")

    print()
    print("─" * 60)
    print("  Refund Calculation")
    print("─" * 60)
    print(f"  Appears in Refund : {'YES' if r.refund_eligible else 'NO'}")
    print(f"  {r.refund_note}")

    print()
    print("─" * 60)
    print("  AI Explanation")
    print("─" * 60)
    for line in r.ai_explanation.splitlines():
        print(f"  {line}")

    print()
    print(sep)


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def parse_amount(value: str) -> float:
    try:
        return float(value.replace(",", "").replace("₹", "").replace("Rs", "").strip())
    except ValueError:
        print(f"ERROR: Invalid amount '{value}'. Please enter a numeric value.")
        sys.exit(1)


def parse_pan(value: str) -> bool:
    return value.strip().lower() in ("yes", "y", "true", "1")


if __name__ == "__main__":
    if len(sys.argv) == 4:
        # Command-line mode: python tds_tcs_calculator.py <type> <amount> <pan_yes_no>
        t_type = sys.argv[1]
        t_amount = parse_amount(sys.argv[2])
        t_pan = parse_pan(sys.argv[3])
    else:
        # Interactive mode
        print("=" * 60)
        print("  TDS / TCS Calculator — Interactive Mode")
        print("=" * 60)
        print()
        print("  Transaction Types: rent | sell | purchase")
        print()
        t_type = input("  Enter transaction type (rent/sell/purchase): ").strip()
        t_amount = parse_amount(input("  Enter transaction amount (Rs): ").strip())
        pan_input = input("  PAN available? (yes/no): ").strip()
        t_pan = parse_pan(pan_input)

    run(t_type, t_amount, t_pan)
