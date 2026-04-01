# Day 7 — TDS / TCS Calculator Agent

An AI-powered Python agent that calculates TDS (Tax Deducted at Source) and TCS (Tax Collected at Source) for Indian transactions, and indicates whether the deducted amount will appear in your income tax refund.

## Supported Transaction Types

| Type | TDS Section | TCS Section | Threshold |
|---|---|---|---|
| **Rent** | 194IB | N/A | > Rs 50,000/month |
| **Sell** (property/goods) | 194IA | 206C(1H) | >= Rs 50 lakhs |
| **Purchase** (goods) | 194Q | 206C (seller) | > Rs 50 lakhs |

## TDS Rates

| Transaction | With PAN | Without PAN |
|---|---|---|
| Rent (194IB) | 10% | 20% |
| Sell — Property (194IA) | 1% | 20% |
| Purchase (194Q) | 0.1% | 5% |

## TCS Rates

| Transaction | With PAN | Without PAN |
|---|---|---|
| Sell — Goods (206C(1H)) | 0.1% | 1% |

## What the Agent Calculates

1. **TDS Amount** — deducted from the transaction at applicable rate
2. **TCS Amount** — collected on sale transactions above threshold
3. **Total Tax Deducted** — TDS + TCS combined
4. **Refund Eligibility** — whether TDS/TCS will appear in Form 26AS/AIS for ITR refund claim
5. **AI Explanation** — plain-English guidance on compliance and refund impact

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key in a `.env` file:
   ```
   OPENAI_API_KEY=sk-...
   ```

## Usage

### Interactive Mode
```bash
python tds_tcs_calculator.py
```

### Command-Line Mode
```bash
python tds_tcs_calculator.py <type> <amount> <pan_yes_no>
```

### Examples
```bash
# Rent payment of Rs 75,000/month with PAN
python tds_tcs_calculator.py rent 75000 yes

# Sale of property for Rs 80 lakhs with PAN
python tds_tcs_calculator.py sell 8000000 yes

# Purchase without PAN
python tds_tcs_calculator.py purchase 6000000 no
```

## Sample Output

```
============================================================
  TDS / TCS CALCULATOR — INDIA (FY 2024-25)
============================================================
  Transaction Type : SELL
  Amount           : Rs   80,00,000.00
  PAN Available    : Yes

────────────────────────────────────────────────────────────
  TDS (Tax Deducted at Source)
────────────────────────────────────────────────────────────
  Applicable : YES
  Section    : 194IA (Immovable Property)
  Rate       : 1.0%
  TDS Amount : Rs     80,000.00
  Note       : Applicable when sale consideration >= Rs 50 lakhs

────────────────────────────────────────────────────────────
  TCS (Tax Collected at Source)
────────────────────────────────────────────────────────────
  Applicable : YES
  Section    : 206C(1H) (Sale of Goods)
  Rate       : 0.1%
  TCS Amount : Rs      8,000.00
  Note       : Seller collects TCS on sale of goods exceeding Rs 50 lakhs

────────────────────────────────────────────────────────────
  Total Tax Deducted / Collected
────────────────────────────────────────────────────────────
  TDS        : Rs     80,000.00
  TCS        : Rs      8,000.00
  TOTAL      : Rs     88,000.00

────────────────────────────────────────────────────────────
  Refund Calculation
────────────────────────────────────────────────────────────
  Appears in Refund : YES
  Rs 88,000.00 (TDS + TCS) will be reflected in Form 26AS / AIS.
  If your total tax liability for the year is less than total TDS/TCS deducted,
  the excess will be refunded when you file your ITR.

────────────────────────────────────────────────────────────
  AI Explanation
────────────────────────────────────────────────────────────
  Since the sale amount exceeds Rs 50 lakhs, TDS @ 1% under Section 194IA
  must be deducted by the buyer before making payment to you. As the seller,
  you are also required to collect TCS @ 0.1% under Section 206C(1H) from
  the buyer. Both amounts will appear in your Form 26AS and AIS, and can be
  claimed as credit when filing your ITR to reduce your tax liability or
  receive a refund.
============================================================
```

## Project Structure

```
Day_07_TDS_TCS_Calculator/
├── tds_tcs_calculator.py   # Main agent script
├── requirements.txt
├── README.md
└── sample_data/
    ├── rent_sample.txt              # Sample rent transaction
    ├── sell_property_sample.txt     # Sample property sale
    └── purchase_sample.txt          # Sample purchase without PAN
```
