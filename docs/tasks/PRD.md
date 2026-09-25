# PRD: Student Academic Performance & Study Recommendation System

## Project Goal

Test and maintain the existing AI-Based Student Academic Performance & Study Recommendation System Using Fuzzy Logic.

The project is a college Internal Assessment mini project combining:
- LangChain + LLM
- Pydantic structured output
- Genuine Fuzzy Logic
- Streamlit UI

## Mandatory Requirements

### 1. LangChain / LLM

The application must use LangChain for genuine language processing.

The LLM must:
- Understand natural-language academic input.
- Extract:
  - study_hours
  - attendance
  - test_score
- Return structured data using Pydantic/structured output.
- Generate a meaningful explanation/recommendation based on the fuzzy result.

Do not replace the LLM with regex or hardcoded keyword extraction.

### 2. Genuine Fuzzy Logic

The application must implement a real fuzzy inference system containing:

- Membership functions
- Fuzzification
- Fuzzy rule evaluation
- Rule firing strengths
- Aggregation
- Centroid defuzzification

Do not replace fuzzy logic with ordinary if/else threshold logic.

The fuzzy system should use gradual membership values such as Low, Medium, and High.

### 3. Streamlit

The application must:
- Start successfully.
- Accept natural-language student input.
- Display extracted academic values.
- Display fuzzy memberships/results.
- Display the final score/risk.
- Display the AI-generated explanation.
- Handle invalid/casual input gracefully without crashing.

### 4. Security

Never expose, print, hardcode, or commit API keys.

The `.env` file must remain ignored by Git.

Streamlit Cloud secrets must be supported safely.

### 5. Dependencies

All dependencies in `requirements.txt` must install correctly without broken dependencies.

## Testing Requirements

Thoroughly test the complete pipeline.

### Test 1 — Valid Academic Input

Example:

"I studied 2 hours today, my attendance is 68%, and I scored 55% in my last test."

Verify that LangChain extracts the correct structured values.

### Test 2 — Casual / Invalid Input

Example:

"Good morning, how are you today?"

The application must not crash.

It should return a friendly error/message requesting the required academic information.

### Test 3 — Strong Performance

Test a case with high study hours, high attendance, and high test score.

Verify that the fuzzy system produces an appropriate low-risk/high-performance result.

### Test 4 — High Effort but Low Score

Test:

- Study hours: 10
- Attendance: 95
- Test score: 20

Verify that the fuzzy system handles the conflicting inputs logically.

### Test 5 — High Score but Poor Academic Conditions

Test:

- Study hours: 1
- Attendance: 20
- Test score: 95

Verify that the fuzzy system considers all relevant inputs.

### Test 6 — Severe Risk

Test:

- Study hours: 1
- Attendance: 20
- Test score: 20

Verify that the result represents high academic risk.

### Test 7 — Intermediate / Boundary Values

Test values around membership-function boundaries.

Verify:
- No crashes.
- Membership values remain valid.
- Rules fire correctly.
- Defuzzification produces a valid result.

### Test 8 — Full Fuzzy Pipeline

Verify:

Crisp Inputs
→ Fuzzification
→ Membership Degrees
→ Rule Evaluation
→ Aggregation
→ Centroid Defuzzification
→ Final Score/Risk

### Test 9 — AI Explanation

Verify that the LangChain explanation:
- Uses the actual fuzzy result.
- Is relevant to the student's inputs.
- Provides useful study recommendations.

### Test 10 — Streamlit Startup

Run Streamlit in headless mode and verify that the application starts without errors.

### Test 11 — Dependency Check

Run an appropriate dependency check and verify there are no broken requirements.

### Test 12 — Git/Security Check

Verify:
- `.env` is ignored.
- No API key appears in tracked files.
- Repository is suitable for GitHub.

## Rules for Changes

If a genuine bug is found:
- Fix it.
- Keep the existing architecture.
- Do not remove LangChain.
- Do not remove genuine fuzzy inference.
- Do not replace fuzzy logic with if/else.
- Do not add unnecessary features.
- Do not expose API keys.
- Do not commit or push to GitHub automatically.

## Final Report

After testing, report:

1. Tests performed
2. PASS/FAIL for each test
3. Bugs found
4. Files changed
5. Fixes made
6. Remaining warnings
7. Final readiness status