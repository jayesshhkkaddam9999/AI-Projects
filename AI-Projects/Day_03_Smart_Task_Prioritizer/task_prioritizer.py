import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a productivity expert.

The user will provide a list of tasks. Your job is to categorize each task into an Eisenhower Matrix:
1. Urgent & Important (DO - Do these now!)
2. Not Urgent & Important (SCHEDULE - Plan for later)
3. Urgent & Not Important (DELEGATE - Can someone else do this?)
4. Not Urgent & Not Important (ELIMINATE - Why are these even here?)

Output the result in a well-formatted, beautiful structure. For each category, list the tasks and a 1-sentence explanation of why they belong there.
"""

def prioritize_tasks(tasks):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is my messy task list:\n{tasks}"}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error contacting Groq API: {e}"

if __name__ == "__main__":
    print("\n📅 Smart Task Prioritizer (Agentic AI)")
    print("---------------------------------------")
    print("Paste your messy list of tasks below. Type 'DONE' on a new line when finished.\n")

    lines = []
    while True:
        line = input()
        if line.strip().upper() == "DONE":
            break
        lines.append(line)

    user_tasks = "\n".join(lines)

    if not user_tasks.strip():
        print("No tasks entered. Exiting...")
    else:
        print("\n⏳ Analyzing tasks and creating your Eisenhower Matrix...")
        result = prioritize_tasks(user_tasks)
        print("\n🤖 Your Priority Matrix:\n" + "="*40 + "\n" + result + "\n" + "="*40)
