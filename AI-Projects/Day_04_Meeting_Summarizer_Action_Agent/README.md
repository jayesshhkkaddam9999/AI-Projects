# Day 04: Meeting Summarizer & Action Agent

Project: "Meeting Summarizer & Action Agent"

An AI helper that processes meeting transcripts and extracts:

- key points
- decisions
- action items
- answers to questions like: "What are my tasks from today’s meeting?"

## Structure

- `requirements.txt` - dependencies
- `meeting_agent.py` - main implementation
- `sample_data/` - sample transcript(s)

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
   python meeting_agent.py sample_data/meeting1.txt
   ```

## Notes

Use any LLM backend (OpenAI, Hugging Face, etc.). This starter uses an abstraction so it can be replaced quickly.
