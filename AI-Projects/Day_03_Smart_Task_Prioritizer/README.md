# Day 03: Smart Task Prioritizer 📅

Organize your messy life with Agentic AI! This tool uses an LLM to categorize any list of tasks into the Eisenhower Matrix (Urgent vs. Important).

## 🚀 Features
- **AI Prioritization**: Automatically sorts tasks into four quadrants.
- **Contextual Explanations**: Tells you *why* each task is where it is.
- **Messy Input Support**: Just dump your thoughts; the AI handles the structure.

## 🛠️ Setup
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage
Run the script from your terminal:
```bash
python task_prioritizer.py
```

Then paste your list of tasks. Type `DONE` on a new line to finalize!
