import os
import sys
from pathlib import Path
from typing import Dict, Any

from pydantic import BaseModel

try:
    import openai
except ImportError:
    openai = None


class NoticeExplanation(BaseModel):
    reason: str
    action_required: str
    deadline: str


def load_notice(file_path: str) -> str:
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"Notice file not found: {file_path}")
    return p.read_text(encoding="utf-8")


def llm_process_notice(notice_text: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment")

    if openai is None:
        raise RuntimeError("openai package is not installed. run pip install -r requirements.txt")

    openai.api_key = api_key
    prompt = (
        "You are a tax notice explanation assistant. Analyze this income tax notice and extract:\n"
        "- Reason for the notice\n"
        "- What action is required\n"
        "- Deadline for compliance\n\n"
        "Notice text:\n" + notice_text + "\n\n"
        "Return JSON with keys: reason, action_required, deadline."
    )

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.2,
    )

    text = response.choices[0].message.content.strip()

    return {"raw": text}


def parse_llm_output(raw: str) -> NoticeExplanation:
    # Simple fallback parsing if structured response not available
    reason = ""
    action_required = ""
    deadline = ""

    lines = raw.splitlines()
    mode = None
    for line in lines:
        l = line.strip()
        if not l:
            continue
        low = l.lower()
        if "reason" in low:
            mode = "reason"
            continue
        if "action" in low:
            mode = "action"
            continue
        if "deadline" in low:
            mode = "deadline"
            continue

        if mode == "reason":
            reason += (" " + l)
        elif mode == "action":
            action_required += (" " + l)
        elif mode == "deadline":
            deadline += (" " + l)

    if not reason:
        reason = raw[:200].strip()

    return NoticeExplanation(
        reason=reason.strip(),
        action_required=action_required.strip(),
        deadline=deadline.strip()
    )


def run(file_path: str):
    notice_text = load_notice(file_path)
    llm_result = llm_process_notice(notice_text)
    parsed = parse_llm_output(llm_result.get("raw", ""))

    print("\n=== Notice Explanation ===")
    print(f"Reason: {parsed.reason}")
    print(f"Action Required: {parsed.action_required}")
    print(f"Deadline: {parsed.deadline}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python notice_agent.py <notice-file>")
        sys.exit(1)
    run(sys.argv[1])