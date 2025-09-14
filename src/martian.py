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
from martian_prompt import IMAGE_GENERATION, MODEL_SELECTION
import base64
import re

load_dotenv()
MARTIAN_ENV = os.getenv("MARTIAN_ENV")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable not set. Please add it to your .env file."
    )

if not MARTIAN_ENV:
    raise ValueError(
        "MARTIAN_ENV environment variable not set. Please add it to your .env file."
    )

# Gemini client for direct Gemini API calls
gemini_client = openai.OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Martian client for routing to different models
martian_client = openai.OpenAI(
    api_key=MARTIAN_ENV, 
    base_url="https://api.withmartian.com/v1"
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


def decide_model(prompt: str) -> str:
    """
    Decides which model to use by asking Martian's google/gemini-2.5-flash:cheap to analyze the prompt.
    Returns 'cohere/command-a' for ASK_MODEL_DECISION prompts, 'gemini-2.5-flash' for others.
    """
    print("🤖 [ROUTER] Asking Martian's google/gemini-2.5-flash:cheap to decide model selection...")
    
    decision_prompt = MODEL_SELECTION.format(prompt=prompt)

    try:
        # Make API call to Martian with google/gemini-2.5-flash:cheap to decide
        decision_response = martian_client.chat.completions.create(
            model="google/gemini-2.5-flash:cheap",
            messages=[{"role": "user", "content": decision_prompt}],
        )
        
        decision = decision_response.choices[0].message.content.strip()
        print(f"🔍 [ROUTER] Martian decision: {decision}")
        
        if "ASK_MODEL_DECISION" in decision:
            selected_model = "cohere/command-a"
            print(f"✅ [ROUTER] Selected model: {selected_model} (via Martian)")
            return selected_model
        else:
            selected_model = "gemini-2.5-flash"
            print(f"✅ [ROUTER] Selected model: {selected_model} (direct Gemini)")
            return selected_model
            
    except Exception as e:
        print(f"⚠️ [ROUTER] Error calling Martian for decision: {e}")
        print("🔄 [ROUTER] Falling back to gemini-2.5-flash")
        return "gemini-2.5-flash"


def use_martian(message, instructions, context):
    # Decide which model to use based on the message content
    selected_model = decide_model(message)
    
    messages = []
    messages.append({"role": "user", "content": message})
    messages.append({"role": "system", "content": IMAGE_GENERATION})

    # Route to the appropriate client based on the selected model
    if selected_model == "cohere/command-a":
        # Use Martian client for Cohere model
        print(f"🚀 [ROUTER] Making API call to {selected_model} via Martian...")
        response = martian_client.chat.completions.create(
            model=selected_model,
            messages=messages,
            response_format={"type": "json_object"},
        )
        print("✨ [ROUTER] Received response from Martian API")
    else:
        # Use direct Gemini client for Gemini model
        print(f"🚀 [ROUTER] Making API call to {selected_model} via direct Gemini...")
        response = gemini_client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=messages,
            response_format={"type": "json_object"},
        )
        print("✨ [ROUTER] Received response from Gemini API")

    message = response.choices[0].message
    content = message.content

    image_url_pattern = r"IMAGE_URL\(([^)]+)\)"
    matches = re.findall(image_url_pattern, content)

    for description in matches:
        clean_description = description.strip("\"'")
        image_path = image_generator_tool(clean_description)
        content = content.replace(f"IMAGE_URL({description})", image_path, 1)

    return content
