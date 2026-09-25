import os
from typing import Any
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

load_dotenv()


def explain_recommendations(
    provider: str = "groq",
    original_text: str = "",
    extracted: Any = None,
    fuzzy_result: Any = None
) -> str:
    """
    Generates a natural language pedagogical explanation of the student's 
    extracted performance data and recommendations.
    """
    groq_api_key: str = os.getenv("GROQ_API_KEY") or ""
    groq_model: str = os.getenv("GROQ_MODEL") or "llama-3.1-70b-versatile"

    # Initialize LLM with SecretStr wrapper to satisfy Pylance
    llm = ChatGroq(
        api_key=SecretStr(groq_api_key),
        model=groq_model,
        temperature=0.3
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an academic advisor. Provide a clear, encouraging, and actionable "
            "explanation of the student's academic standing and remediation plan."
        ),
        (
            "user",
            "Provider: {provider}\n"
            "Original Student Input: {original_text}\n"
            "Extracted Metrics: {extracted}\n"
            "Evaluation Assessment: {fuzzy_result}\n\n"
            "Please provide an analytical explanation and next steps for the student."
        )
    ])

    chain = prompt | llm | StrOutputParser()

    try:
        response = chain.invoke({
            "provider": provider,
            "original_text": original_text,
            "extracted": str(extracted) if extracted is not None else "No data",
            "fuzzy_result": str(fuzzy_result) if fuzzy_result is not None else "No data"
        })
        return str(response)
    except Exception as e:
        return f"Unable to generate explanation: {e}"