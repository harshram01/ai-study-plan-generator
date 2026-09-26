import os
import json
import re
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from models import StudentProfile, StudyRecommendation, DailyPlanItem

load_dotenv()


def clean_and_parse_json(raw_text: str) -> dict:
    """Extract and parse valid JSON even if surrounded by markdown or extra text."""
    # Remove markdown codeblocks ```json ... ```
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
    
    # Extract first outer { ... }
    match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1)
        
    return json.loads(cleaned)


def generate_study_plan(profile: StudentProfile) -> StudyRecommendation:
    """
    Generates an IKS-aligned remediation timetable without fragile tool-calling,
    using pure JSON output mode.
    """
    if not profile.subjects or len(profile.subjects) == 0:
        raise ValueError("No subjects provided in profile.")

    groq_api_key = os.getenv("GROQ_API_KEY") or ""
    # 8b-instant ya 3.3-70b Groq par fast and complete JSON return karte hain bina truncation ke
    model_name = os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile"

    llm = ChatGroq(
        api_key=SecretStr(groq_api_key),
        model=model_name,
        temperature=0.1,
        max_tokens=3000,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

    details = []
    for sub, data in profile.subjects.items():
        gap = round(data.target_score - data.current_score, 1)
        weak_str = ", ".join(data.weak_areas) if data.weak_areas else "None"
        details.append(
            f"- {sub}: Current={data.current_score}%, Target={data.target_score}% (Gap={gap}%), Weak Areas={weak_str}"
        )
    subject_details_str = "\n".join(details)

    system_instruction = (
        "You are an academic mentor integrating Indian Knowledge Systems (IKS) Adhyayana-Vidhi "
        "(Sravana, Manana, Nididhyasana, Sakshatkaran). "
        "Return ONLY a single valid JSON object strictly matching this schema:\n"
        "{\n"
        '  "diagnostic_summary": "string",\n'
        '  "priority_topics": ["string"],\n'
        '  "weekly_schedule": [\n'
        '    {"day": "Monday", "subject": "string", "topic": "string", "duration_hours": 1.5, "recommended_action": "string"}\n'
        "  ],\n"
        '  "study_tips": ["string"]\n'
        "}\n"
        "Ensure all weekly_schedule durations sum up close to the available weekly hours. Keep JSON concise."
    )

    user_query = (
        f"Student ID: {profile.student_id}\n"
        f"Available Weekly Hours: {profile.available_hours_per_week}\n"
        f"Subjects Performance:\n{subject_details_str}\n\n"
        "Generate the study recommendation JSON now."
    )

    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_query)
    ]

    response = llm.invoke(messages)
    content = str(response.content)

    data = clean_and_parse_json(content)

    # Convert to Pydantic Model
    return StudyRecommendation(**data)