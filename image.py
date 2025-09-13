from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set. Please add it to your .env file.")

client = genai.Client(api_key=api_key)

def nano_banana(prompt):
  response = client.models.generate_content(
      model="gemini-2.5-flash-image-preview",
      contents=[prompt],
  )

  for part in response.candidates[0].content.parts:
      if part.text is not None:
          print(part.text)
      elif part.inline_data is not None:
          image = Image.open(BytesIO(part.inline_data.data))
          image.save("generated_image.png")