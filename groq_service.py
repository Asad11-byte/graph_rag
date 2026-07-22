import json
import os
from typing import List

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, ValidationError

from prompts import (
    GRAPH_EXTRACTION_PROMPT,
    GRAPH_RAG_PROMPT,
    ENTITY_EXTRACTION_PROMPT,
)

load_dotenv()

MODEL_NAME = "llama-3.1-8b-instant"

DEBUG = False


class Triple(BaseModel):
    head: str
    relation: str
    tail: str


class GroqService:
    """
    Wrapper around the Groq API.

    Responsibilities
    ----------------
    - Extract knowledge triples
    - Extract entities from questions
    - Generate GraphRAG answers
    """

    def __init__(self):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env")

        self.client = Groq(api_key=api_key)

        self.model = MODEL_NAME

    # ====================================================
    # Internal Chat Helper
    # ====================================================

    def _chat(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        """
        Send a prompt to Groq and return the text response.
        """

        messages = []

        if system_prompt:

            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=messages,
        )

        return response.choices[0].message.content.strip()

    # ====================================================
    # Triple Extraction
    # ====================================================

    def extract_triples(
        self,
        text: str,
    ) -> List[Triple]:
        """
        Extract knowledge triples from text.
        """

        prompt = GRAPH_EXTRACTION_PROMPT.format(
            text=text
        )

        content = self._chat(
            prompt=prompt,
            system_prompt=(
                "You are a Knowledge Graph extraction assistant. "
                "Return ONLY valid JSON."
            ),
        )

        if DEBUG:
            print("\n========== RAW GROQ RESPONSE ==========\n")
            print(content)
            print("\n=======================================\n")

        # Remove Markdown code fences

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:

            data = json.loads(content)

        except json.JSONDecodeError as error:

            raise ValueError(
                f"Groq returned invalid JSON.\n\n{content}"
            ) from error

        if not isinstance(data, list):

            raise ValueError(
                "Expected a JSON array of triples."
            )

        triples: List[Triple] = []

        for item in data:

            try:

                triples.append(
                    Triple(**item)
                )

            except ValidationError as error:

                if DEBUG:
                    print(error)

        if DEBUG:
            print(f"\n✓ Extracted {len(triples)} triples.\n")

        return triples

    # ====================================================
    # Entity Extraction
    # ====================================================

    def extract_entity(
        self,
        question: str,
    ) -> str:
        """
        Extract the main entity from the user's question.
        """

        prompt = ENTITY_EXTRACTION_PROMPT.format(
            question=question
        )

        entity = self._chat(prompt)

        entity = (
            entity
            .replace('"', "")
            .replace("'", "")
            .replace(".", "")
            .strip()
        )

        return entity

    # ====================================================
    # GraphRAG Question Answering
    # ====================================================

    def answer_question(
        self,
        context: str,
        question: str,
    ) -> str:
        """
        Answer a question using only graph context.
        """

        prompt = GRAPH_RAG_PROMPT.format(
            context=context,
            question=question,
        )

        answer = self._chat(prompt)

        return answer