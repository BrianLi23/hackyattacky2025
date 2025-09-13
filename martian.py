import openai
import os
from dotenv import load_dotenv
load_dotenv()
MARTIAN_ENV = os.getenv("MARTIAN_ENV")

oai_client = openai.OpenAI(
    api_key=MARTIAN_ENV,
    base_url="https://api.withmartian.com/v1"
)

def use_martian_smart_routing(message):
  response = oai_client.chat.completions.create(
    model = "martian/code",
    messages=[
      {
        "role": "user",
        "content": message
      }
    ]
  )
  return response.choices[0].message.content

message = "Write a Python function that calculates Mars orbital period."
response = use_martian_smart_routing(message)

print(response)