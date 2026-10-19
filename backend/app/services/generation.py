import re
from dataclasses import dataclass

from ollama import ResponseError, chat


UNKNOWN_ANSWER = "I don't know based on the available documents."

def validate_citations(
    answer: str,
    sources: list["CitationSource"],
) -> bool:
    """Return False if the answer references unavailable sources."""
    cited_references = {
        int(reference)
        for reference in re.findall(r"\[(\d+)\]", answer)
    }

    available_references = {
        source.reference for source in sources
    }

    return cited_references.issubset(available_references)


@dataclass
class CitationSource:
    reference: int
    title: str
    page_number: int | None = None
    section_title: str | None = None
    source_url: str | None = None

    def format(self) -> str:
        details = [self.title]

        if self.section_title:
            details.append(f"Section: {self.section_title}")

        if self.page_number is not None:
            details.append(f"Page {self.page_number}")

        if self.source_url:
            details.append(self.source_url)

        return f"[{self.reference}] " + " | ".join(details)


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
        sources: list[CitationSource] | None = None,
    ) -> str:
        if not question.strip():
            return ""

        if not context.strip():
            return UNKNOWN_ANSWER

        source_list = sources or []

        if source_list:
            source_references = "\n".join(
                source.format() for source in source_list
            )

            citation_instructions = f"""
Citation rules:
- Cite supporting information using references such as [1] or [2].
- Use ONLY these available sources:
{source_references}
- Never invent a source, reference number, page number, or URL.
- Place citations immediately after the claims they support.
- If the sources do not support an answer, say:
  "{UNKNOWN_ANSWER}"
- Do not include a separate sources list; the application will add it.
"""
        else:
            citation_instructions = f"""
- No source metadata is available.
- Do not invent citations or sources.
- If the context does not support an answer, say:
  "{UNKNOWN_ANSWER}"
"""

        system_prompt = f"""You are a university knowledge assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Do not use outside knowledge.
- Do not invent facts.
- Be concise and directly answer the question.
{citation_instructions}
"""

        try:
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
        except ResponseError as exc:
            raise RuntimeError(
                "The local language model could not generate an answer."
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                "The answer generation service is unavailable."
            ) from exc

        answer = response.message.content.strip()

        if not answer:
            return UNKNOWN_ANSWER

        if not validate_citations(answer, source_list):
            return UNKNOWN_ANSWER

        return answer

    @staticmethod
    def format_sources(
        sources: list[CitationSource],
    ) -> str:
        if not sources:
            return ""

        formatted_sources = "\n".join(
            source.format() for source in sources
        )

        return f"Sources:\n{formatted_sources}"