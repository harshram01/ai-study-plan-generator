import os
from typing import Any
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from models import StudentAcademicData, StudentProfile

load_dotenv()


def extract_student_data(raw_text: str) -> StudentProfile:
    """
    Extracts structured student academic information from free-form text
    or unstructured logs using LangChain and Groq.
    """
    groq_api_key: str = os.getenv("GROQ_API_KEY") or ""
    groq_model: str = os.getenv("GROQ_MODEL") or "llama-3.1-70b-versatile"

    # Initialize LLM with SecretStr wrapper to satisfy Pylance
    llm = ChatGroq(
        api_key=SecretStr(groq_api_key),
        model=groq_model,
        temperature=0.1
    )

    parser = PydanticOutputParser(pydantic_object=StudentProfile)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an academic data extractor. Convert the following unstructured text into structured student metrics.\n{format_instructions}"
        ),
        (
            "user",
            "Unstructured Student Report:\n{raw_text}"
        )
    ])

    chain = prompt | llm | parser

    result = chain.invoke({
        "raw_text": raw_text,
        "format_instructions": parser.get_format_instructions()
    })

    return result