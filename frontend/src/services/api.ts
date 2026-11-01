
import type { AskRequest, AskResponse } from "@/types/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function askQuestion(
  request: AskRequest
): Promise<AskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    try {
      const error = await response.json();
      message = error.detail ?? message;
    } catch {
      // Keep the fallback message.
    }

    throw new Error(
      typeof message === "string" ? message : JSON.stringify(message)
    );
  }

  return response.json() as Promise<AskResponse>;
}
