
import json
from typing import Any

from ollama import ResponseError, chat


class FaithfulnessEvaluator:
    def __init__(
        self,
        model_name: str = "qwen3:4b-instruct",
    ) -> None:
        self.model_name = model_name

    def evaluate(
        self,
        answer: str,
        context: str,
    ) -> dict[str, Any]:
        if not answer.strip() or not context.strip():
            return self._empty_result()

        system_prompt = """
You are an evaluator for a university knowledge assistant.

Your task is to evaluate whether each factual claim in an answer
is supported by the provided context.

Instructions:
1. Break the answer into individual factual claims.
2. Evaluate each claim using ONLY the provided context.
3. Use one of these verdicts:
   - supported: the context directly supports the entire claim.
   - partially_supported: the context supports only part of the claim.
   - unsupported: the context does not support the claim.
4. Do not use outside knowledge.
5. Do not treat a citation number as evidence by itself.
6. Do not penalize harmless paraphrasing.
7. Ignore introductory phrases and non-factual wording.

Return ONLY valid JSON in this exact structure:

{
  "claims": [
    {
      "claim": "A factual claim from the answer",
      "verdict": "supported",
      "evidence": "Relevant text from the context"
    }
  ]
}

If there are no factual claims, return:
{"claims": []}
"""

        user_prompt = f"""
CONTEXT:
{context}

GENERATED ANSWER:
{answer}
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
                        "content": user_prompt,
                    },
                ],
                format="json",
                options={"temperature": 0},
            )
        except ResponseError as exc:
            raise RuntimeError(
                "The faithfulness evaluation model failed."
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                "The faithfulness evaluation service is unavailable."
            ) from exc

        try:
            raw_output = response.message.content.strip()
            result = json.loads(raw_output)

            if not isinstance(result, dict):
                raise ValueError("Expected a JSON object.")

            claims = result.get("claims")

            if not isinstance(claims, list):
                raise ValueError("Expected a claims list.")

            valid_verdicts = {
                "supported",
                "partially_supported",
                "unsupported",
            }

            for claim in claims:
                if not isinstance(claim, dict):
                    raise ValueError("Invalid claim entry.")

                if not isinstance(claim.get("claim"), str):
                    raise ValueError("Invalid claim text.")

                if claim.get("verdict") not in valid_verdicts:
                    raise ValueError("Invalid claim verdict.")

                if not isinstance(claim.get("evidence"), str):
                    raise ValueError("Invalid claim evidence.")

            return self._calculate_metrics(claims)

        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                "The faithfulness evaluator returned invalid output."
            ) from exc

    @staticmethod
    def _calculate_metrics(
        claims: list[dict[str, str]],
    ) -> dict[str, Any]:
        supported = sum(
            claim["verdict"] == "supported"
            for claim in claims
        )

        partially_supported = sum(
            claim["verdict"] == "partially_supported"
            for claim in claims
        )

        unsupported = sum(
            claim["verdict"] == "unsupported"
            for claim in claims
        )

        total = len(claims)

        return {
            "claims": claims,
            "total_claims": total,
            "supported_claims": supported,
            "partially_supported_claims": partially_supported,
            "unsupported_claims": unsupported,
            "faithfulness_score": (
                supported / total if total else None
            ),
        }

    @staticmethod
    def _empty_result() -> dict[str, Any]:
        return {
            "claims": [],
            "total_claims": 0,
            "supported_claims": 0,
            "partially_supported_claims": 0,
            "unsupported_claims": 0,
            "faithfulness_score": None,
        }
