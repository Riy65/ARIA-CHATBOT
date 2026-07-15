import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL_NAME = "gemini-flash-latest"


def get_ai_reply(messages: list) -> str:
    """
    Sends conversation messages to Gemini
    and returns the AI reply.
    """

    prompt = ""

    for message in messages:

        prompt += f"{message['role'].capitalize()}: {message['content']}\n\n"

    response = client.models.generate_content(

        model=MODEL_NAME,

        contents=prompt

    )

    return response.text.strip()


def generate_chat_title(user_message, ai_reply):

    prompt = f"""
Generate a short title (maximum 5 words)
for this conversation.

Return ONLY the title.

User:
{user_message}

Assistant:
{ai_reply}
"""

    response = client.models.generate_content(

        model=MODEL_NAME,

        contents=prompt

    )

    return response.text.strip()

