import openai
import os
import json
import uuid
import tempfile
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
            # Generate unique filename in temp directory within current directory
            temp_dir = os.path.join(os.getcwd(), "temp")
            os.makedirs(temp_dir, exist_ok=True)
            filename = f"generated_image_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(temp_dir, filename)
            image = Image.open(BytesIO(part.inline_data.data))
            image.save(filepath)
            print("I am returning the filename:", filepath)
            return os.path.abspath(filepath)

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
        tools=tools,
        tool_choice="auto",
    )
    
    # Handle tool calls
    message = response.choices[0].message
    if message.tool_calls:
        generated_image_paths = []
        
        # Execute each tool call
        for tool_call in message.tool_calls:
            if tool_call.function.name == "image_generator_tool":
                # Parse arguments and call the function
                args = json.loads(tool_call.function.arguments)
                image_path = image_generator_tool(args["image_description"])
                generated_image_paths.append(image_path)
        
        # If images were generated, make a second call to integrate paths
        if generated_image_paths:
            # Add the assistant's tool call message to conversation
            messages.append({
                "role": "assistant", 
                "content": None,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function", 
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                    } for tc in message.tool_calls
                ]
            })
            
            # Add tool results to conversation
            for i, tool_call in enumerate(message.tool_calls):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": generated_image_paths[i]
                })
            
            # Add instruction to incorporate image paths
            messages.append({
                "role": "user",
                "content": f"I have generated {len(generated_image_paths)} images with the following file paths: {generated_image_paths}. Please provide your response incorporating these image file paths in the appropriate locations."
            })
            
            # Make second API call without tools to get final response
            final_response = oai_client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=messages,
                response_format={"type": "json_object"},
            )
            return final_response.choices[0].message.content
    
    # If no tool calls, return the regular response
    return message.content
