import openai
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
MARTIAN_ENV = os.getenv("MARTIAN_ENV")

oai_client = openai.OpenAI(
    api_key=MARTIAN_ENV, base_url="https://api.withmartian.com/v1"
)


def use_martian(message, instructions, context):
    messages = []

    if instructions:
        messages.append({"role": "system", "content": instructions})

    messages.append({"role": "user", "content": message})

    messages.append(
        {
            "role": "user",
            "content": "Context of previous prompts in this session: " + context,
        }
    )

    response = oai_client.chat.completions.create(
        model="google/gemini-2.5-flash",  # "cohere/command-r7b-12-2024",
        messages=messages,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content
