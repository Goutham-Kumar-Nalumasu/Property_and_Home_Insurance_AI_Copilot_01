import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()


class LangChainOpenAIClient:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    def generate_answer(
        self,
        question: str,
        retrieved_context: str,
        session_memory: Dict[str, Any],
        long_term_memory: List[Dict[str, Any]],
    ) -> str:
        system_prompt = """
You are HomeShield Property Insurance AI Copilot.

Answer only using:
1. Retrieved policy context
2. Session memory
3. Long-term user memory

Rules:
- Do not invent policy limits, exclusions, contractors, claim decisions, or payouts.
- Do not approve or reject claims.
- Do not provide binding legal, financial, or insurance advice.
- If context is insufficient, say you do not have enough information.
- Always mention that final claim outcomes depend on insurer assessment.
"""

        user_prompt = f"""
User question:
{question}

Session memory:
{session_memory}

Long-term memory:
{long_term_memory}

Retrieved policy context:
{retrieved_context}

Answer:
"""

        response = self.llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )

        return response.content


llm_client = LangChainOpenAIClient()