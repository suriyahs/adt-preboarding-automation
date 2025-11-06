# AI-Powered Preboarding Escalation Prototype

This is a functional prototype built for an internship interview with ADT's TA Technology team. It demonstrates a complete, two-part system for automation and AI-driven process improvement.

The goal was to build a workflow that not only automates new hire preboarding but also uses AI to identify high-risk candidates and escalate them to the TA team.

The Problem
A busy talent team can't manually track every new hire. Simple automation might send a welcome email, but it won't alert the team to candidates who are "stuck" (taking too long) or "at-risk" (processed too fast, risking errors).

The Solution: A Two-Part System

Part 1: The brain (Python AI Script)
A Python script (analyze_hires.py) runs to analyze all candidates in the 'Hires - ADT Preboarding' Google Sheet.

Technology: Python, Pandas, gspread, scikit-learn

Process:
    1. Reads the Google Sheet data.
    2. Analyzes the 'DaysSinceOffer' column using an 'IsolationForest' (anomaly detection) model.
    3. Flags any "anomalies" (hires taking unusually long *or* unusually short times) by writing "FLAGGED" into the 'AI_Alert' column.

Part 2: Zapier Workflow
A Zapier workflow (AI New Hire Escalation) runs 24/7 to act on the AI's findings.

Technology: Zapier, Google Sheets, Gmail, Google Tasks
Process:
    1.  Trigger: Activates on any new or updated row in the Google Sheet.
    2.  Filter: The workflow *only* continues if **two** conditions are met:
        Status == In Progress
        AND
        AI_Alert == FLAGGED
    3.  Action: It sends a welcome email via gmail and creates a follow-up task in Google Tasks for the TA team.

The Pivot
My initial plan was to use Power Automate and Excel. However, I was blocked by an enterprise AAD authentication error (AADSTS500200) that my university's onedrive kept throwing.

I pivoted to an analogous toolset (Zapier/Google) to build a 100% functional prototype. This was done to overcome technical blockers to deliver a working solution.