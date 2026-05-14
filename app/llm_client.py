import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def generate_llm_answer(question: str, context: str, memory: dict) -> str:
    """
    Generate a grounded insurance answer using OpenAI.
    """

    if not USE_LLM:
        return (
            "LLM is disabled. Retrieved context:\n\n"
            + context[:1800]
        )

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    system_prompt = """
You are HomeShield Property Insurance AI Copilot.

You answer only using the provided context and session memory.
You must not invent policy limits, contractors, claims, or coverage.
You must not approve or reject claims.
You must not provide binding legal, financial, or insurance advice.
Always say final claim outcomes depend on insurer assessment.
If the answer is not in the context, say you do not have enough information.

When answering:
- Be concise.
- Mention relevant limits and exclusions.
- Include a safe disclaimer.
- Cite source document names if provided in context.
"""

    user_prompt = f"""
User question:
{question}

Session memory:
{memory}

Retrieved HomeShield context:
{context}

Answer:
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content