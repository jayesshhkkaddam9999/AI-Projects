# Day 05: Notice Explanation Agent

Project: "Notice Explanation Agent (🔥 Very Powerful)"

An AI agent that explains Income Tax Notices in simple language.

🧠 Input:
Notice PDF / text

Output:
- Reason for notice
- What action required
- Deadline

Example:
"This notice is due to mismatch in TDS. You need to verify Form 26AS."

## Structure

- `requirements.txt` - dependencies
- `notice_agent.py` - main implementation
- `sample_data/` - sample notice text(s)

## Quick start

1. Create and activate a Python venv:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3. Run:
   ```bash
   python notice_agent.py sample_data/notice1.txt
   ```

## Notes

Use any LLM backend (OpenAI, Hugging Face, etc.). This starter uses an abstraction so it can be replaced quickly.