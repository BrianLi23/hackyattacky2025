from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
MARTIAN_ENV = os.getenv("MARTIAN_ENV")

client = OpenAI(
  api_key = MARTIAN_ENV,
  base_url="https://withmartian.com/api/openai/v1"
)

cohere_models = [
  "command-a-03-2025",
  "command-r-08-2024", 
  "command-r7b",
  "command-a-translate",
  "command-a-reasoning",
  "command-a-vision"
]

def use_cohere(message):
  response = client.chat.completions.create(
    model = "router",
    messages = [
      {"role": "user", "content": message}
    ]
  )
  return response.choices[0].message.content

response = use_cohere("Hello! Can you help me understand AI?")
print(response)