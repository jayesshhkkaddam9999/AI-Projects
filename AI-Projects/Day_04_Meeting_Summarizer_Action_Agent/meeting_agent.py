import os
import sys
from pathlib import Path
from typing import Dict, Any

from pydantic import BaseModel

try:
    import openai
except ImportError:
    openai = None


class MeetingSummary(BaseModel):
    summary: str
    decisions: list[str]
    action_items: list[str]


def load_transcript(file_path: str) -> str:
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"Transcript file not found: {file_path}")
    return p.read_text(encoding="utf-8")


def llm_process_transcript(transcript: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment")

    if openai is None:
        raise RuntimeError("openai package is not installed. run pip install -r requirements.txt")

    openai.api_key = api_key
    prompt = (
        "You are a meeting assistant. Extract meeting summary, decisions, and action items.\n"
        "Transcript:\n" + transcript + "\n\n"
        "Return JSON with keys: summary, decisions, action_items. "
        "Additionally answer: \"What are my tasks from today's meeting?\" in plain text."
    )

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
        temperature=0.2,
    )

    text = response.choices[0].message.content.strip()

    return {"raw": text}


def parse_llm_output(raw: str) -> MeetingSummary:
    # Simple fallback parsing if structured response not available
    summary = ""
    decisions = []
    action_items = []

    lines = raw.splitlines()
    mode = None
    for line in lines:
        l = line.strip()
        if not l:
            continue
        low = l.lower()
        if low.startswith("summary"):
            mode = "summary"
            continue
        if low.startswith("decision") or low.startswith("decisions"):
            mode = "decisions"
            continue
        if low.startswith("action") or low.startswith("action items"):
            mode = "action"
            continue

        if mode == "summary":
            summary += (" " + l)
        elif mode == "decisions":
            decisions.append(l.lstrip("- "))
        elif mode == "action":
            action_items.append(l.lstrip("- "))

    if not summary:
        summary = raw[:500].strip()

    return MeetingSummary(summary=summary.strip(), decisions=decisions, action_items=action_items)


def answer_tasks(action_items: list[str]) -> str:
    if not action_items:
        return "No action items detected."
    return "Your tasks from this meeting are:\n" + "\n".join(f"- {a}" for a in action_items)


def run(file_path: str):
    transcript = load_transcript(file_path)
    llm_result = llm_process_transcript(transcript)
    parsed = parse_llm_output(llm_result.get("raw", ""))

    print("\n=== Meeting Summary ===")
    print(parsed.summary)
    print("\n=== Decisions ===")
    print("\n".join(f"- {d}" for d in parsed.decisions) or "(none)")
    print("\n=== Action Items ===")
    print("\n".join(f"- {a}" for a in parsed.action_items) or "(none)")
    print("\n=== Answer: What are my tasks from today’s meeting? ===")
    print(answer_tasks(parsed.action_items))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python meeting_agent.py <transcript-file>")
        sys.exit(1)
    run(sys.argv[1])
