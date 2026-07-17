
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def get_ai_reply(messages):

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=messages,

        temperature=0.7,

        max_tokens=200

    )

    return response.choices[0].message.content


def generate_chat_title(user_message, ai_reply):

    messages = [

        {
            "role": "system",
            "content":
            "Generate a title in maximum 5 words. Return only the title."
        },

        {
            "role": "user",
            "content":
            f"User: {user_message}\nAssistant: {ai_reply}"
        }

    ]

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=messages,

        temperature=0.3,

        max_tokens=10

    )

    return response.choices[0].message.content.strip()