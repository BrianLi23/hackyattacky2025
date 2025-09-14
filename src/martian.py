import openai
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

load_dotenv()
MARTIAN_ENV = os.getenv("MARTIAN_ENV")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable not set. Please add it to your .env file."
    )

oai_client = openai.OpenAI(
    api_key=GEMINI_API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Initialize Google Genai client for image generation
genai_client = genai.Client(api_key=GEMINI_API_KEY)


def image_generator_tool(image_description: str) -> str:
    """
    Generates an image based on the provided description using Google Genai
    """
    response = genai_client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=[image_description],
    )

    print("I am here!")
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            # Generate unique filename
            filename = f"generated_image_{uuid.uuid4().hex[:8]}.png"
            image = Image.open(BytesIO(part.inline_data.data))
            image.save(filename)
            print("I am returning the filename:", filename)
            return os.path.abspath(filename)

    return "No image generated"


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

    tools = [
        {
            "type": "function",
            "function": {
                "name": "image_generator_tool",
                "description": "Generates an image based on the provided description using Google Genai",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_description": {
                            "type": "string",
                            "description": "Description of the image to generate",
                        }
                    },
                    "required": ["image_description"],
                },
            },
        }
    ]

    response = oai_client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=messages,
        response_format={"type": "json_object"},
        # tools=tools,
        # tool_choice="auto",
    )
    return response.choices[0].message.content
