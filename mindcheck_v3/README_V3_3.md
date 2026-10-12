# MindCheck V3.3 — Evaluation Flow Fix

## What changed
- No forced Think Again page after each answer.
- Student flow is now Explain → Apply → Transfer → Understanding Profile → Reflection.
- AI/API failures never become a fake Developing grade.
- Student intro performs a live API connection test and shows the actual status.
- Evaluation errors are surfaced as Not evaluated with a useful diagnostic.
- Evaluation prompt separates scope alignment, conceptual accuracy, and Explain/Apply/Transfer evidence.
- Required concepts are semantic anchors, not keyword matching.
- Understanding Profile layout no longer uses the broken expander arrow icons.
- CSS no longer overrides Streamlit's Material icon font.

## API setup
Create `.env` next to `app.py`:

OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.6-luna

Restart Streamlit after changing `.env`.

## Run
python -m pip install -r requirements.txt
python -m streamlit run app.py
