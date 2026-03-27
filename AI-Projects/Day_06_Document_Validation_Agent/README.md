# Day 6 — Document Validation Agent

An AI agent that validates Indian tax and financial documents by detecting missing fields, format errors, and data mismatches.

## Supported Documents

| Document | Description |
|---|---|
| **Form 16** | TDS certificate issued by employer (Part A & Part B) |
| **AIS** | Annual Information Statement from Income Tax portal |
| **Bank Statement** | Any bank account statement |

## What the Agent Detects

- **Missing Fields** — Required fields that are absent or left blank
- **Format Errors** — Values in wrong format (invalid PAN, wrong date format, bad amounts)
- **Data Mismatches** — Internal inconsistencies (totals not matching, balance discrepancies, AY conflicts)

## Setup

1. Clone / download this project.

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.example .env
   # Edit .env and set OPENAI_API_KEY=sk-...
   ```

## Usage

```bash
python document_validation_agent.py <document-file>
```

### Examples

```bash
python document_validation_agent.py sample_data/form16_sample.txt
python document_validation_agent.py sample_data/ais_sample.txt
python document_validation_agent.py sample_data/bank_statement_sample.txt
```

## Sample Output

```
Loading document: sample_data/bank_statement_sample.txt
Validating document with AI...

=======================================================
  DOCUMENT VALIDATION REPORT  [FAILED]
=======================================================

Document Type : Bank Statement
Valid         : No

--- Missing Fields ---
  (none)

--- Format Errors ---
  (none)

--- Data Mismatches ---
  * Closing balance (Rs. 1,05,340) does not match last running balance (Rs. 98,740). Difference: Rs. 6,600.

--- Summary ---
  The bank statement has a closing balance discrepancy of Rs. 6,600 suggesting missing transactions.
=======================================================
```

## Project Structure

```
Day_06_Document_Validation_Agent/
├── document_validation_agent.py   # Main agent script
├── requirements.txt
├── .env.example
├── README.md
└── sample_data/
    ├── form16_sample.txt          # Sample Form 16 with mismatch
    ├── ais_sample.txt             # Sample AIS (clean)
    └── bank_statement_sample.txt  # Sample bank statement with balance error
```
