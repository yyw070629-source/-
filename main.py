import os
import sys

from google import genai
from google.genai import types

# Replit AI Integrations - Gemini access (no personal API key needed)
AI_INTEGRATIONS_GEMINI_API_KEY = os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY")
AI_INTEGRATIONS_GEMINI_BASE_URL = os.environ.get("AI_INTEGRATIONS_GEMINI_BASE_URL")

client = genai.Client(
    api_key=AI_INTEGRATIONS_GEMINI_API_KEY,
    http_options={
        'api_version': '',
        'base_url': AI_INTEGRATIONS_GEMINI_BASE_URL
    }
)

MODEL = "gemini-2.5-flash"

def main():
    print("=" * 50)
    print("  Gemini AI Assistant")
    print("=" * 50)
    print()
    print("Type your message and press Enter.")
    print("Type 'quit' or 'exit' to leave.")
    print("Type 'clear' to reset the conversation.")
    print()

    history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        if user_input.lower() == "clear":
            history.clear()
            print("\nConversation cleared.\n")
            continue

        history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

        try:
            print("\nAssistant: ", end="", flush=True)
            full_response = ""
            for chunk in client.models.generate_content_stream(
                model=MODEL,
                contents=history,
                config=types.GenerateContentConfig(max_output_tokens=8192)
            ):
                text = chunk.text or ""
                print(text, end="", flush=True)
                full_response += text

            print("\n")
            history.append(types.Content(role="model", parts=[types.Part(text=full_response)]))

        except Exception as e:
            error_msg = str(e)
            if "FREE_CLOUD_BUDGET_EXCEEDED" in error_msg:
                print(f"\n\nYour cloud budget has been exceeded. Please check your Replit credits.\n")
            else:
                print(f"\n\nSomething went wrong: {error_msg}\n")
            if history and history[-1].role == "user":
                history.pop()


if __name__ == "__main__":
    main()
