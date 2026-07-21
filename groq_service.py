import json
import os
from typing import List

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, ValidationError

from prompts import GRAPH_EXTRACTION_PROMPT

load_dotenv()


class Triple(BaseModel):
    head: str
    relation: str
    tail: str


class GroqService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env")

        self.client = Groq(api_key=api_key)

        # Reliable structured-output model
        self.model = "llama-3.3-70b-versatile"

    def extract_triples(self, text: str) -> List[Triple]:
        """
        Extract knowledge triples from text using Groq.
        """

        prompt = GRAPH_EXTRACTION_PROMPT.format(text=text)

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a knowledge graph extraction assistant. "
                        "Return ONLY valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        content = response.choices[0].message.content.strip()

        # Remove Markdown code fences if present
        if content.startswith("```"):
            lines = content.splitlines()

            if lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]

            content = "\n".join(lines).strip()

        try:
            data = json.loads(content)

        except json.JSONDecodeError as e:
            print("\n========== GROQ RESPONSE ==========")
            print(content)
            print("===================================\n")

            raise ValueError(
                f"Groq returned invalid JSON: {e}"
            )

        triples = []

        for item in data:
            try:
                triples.append(Triple(**item))

            except ValidationError:
                continue

        return triples