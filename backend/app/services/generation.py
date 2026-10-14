from ollama import chat


class AnswerGenerator:
    def __init__(
        self,
        model_name: str = "qwen3:4b-instruct",
    ) -> None:
        self.model_name = model_name

    def generate(
        self,
        question: str,
        context: str,
    ) -> str:
        if not question.strip():
            return ""

        if not context.strip():
            return (
                "I don't know based on the available documents."
            )

        system_prompt = """You are a university knowledge assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Do not use outside knowledge.
- Do not invent facts.
- If the context does not contain enough information to answer, say:
  "I don't know based on the available documents."
- Be concise and directly answer the question.
"""

        response = chat(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": (
                        f"Context:\n{context}\n\n"
                        f"Question:\n{question}"
                    ),
                },
            ],
        )

        return response.message.content.strip()