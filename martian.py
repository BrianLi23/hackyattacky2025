import openai
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
MARTIAN_ENV = os.getenv("MARTIAN_ENV")

oai_client = openai.OpenAI(
    api_key=MARTIAN_ENV,
    base_url="https://api.withmartian.com/v1"
)

# Persistent storage for conversation sessions and their messages
conversationSessions = {}  # {session_id: {"messages": [], "created_at": timestamp, "type": "database|api|etc"}}
sessionData = {}  # {session_id: {"variables": {}, "structured_data": []}}

def use_martian(message, instructions=None):
  messages = []
  
  if instructions:
    messages.append({
      "role": "system", 
      "content": instructions
    })
  
  messages.append({
    "role": "user",
    "content": message
  })
  
  response = oai_client.chat.completions.create(
    model = "cohere/command-r7b-12-2024",
    messages=messages
  )
  return response.choices[0].message.content

def create_session(session_type="general"):
  """Create a new conversation session"""
  session_id = str(uuid.uuid4())
  conversationSessions[session_id] = {
    "messages": [],
    "created_at": datetime.now().isoformat(),
    "type": session_type
  }
  sessionData[session_id] = {
    "variables": {},
    "structured_data": []
  }
  return session_id

def add_to_session(session_id, message, response):
  """Add a message and response to a session"""
  if session_id in conversationSessions:
    conversationSessions[session_id]["messages"].append({
      "message": message,
      "response": response,
      "timestamp": datetime.now().isoformat()
    })

def add_data(session_id, data_type, description):
  """Generate structured data for a session using Martian model"""
  if session_id not in conversationSessions:
    raise Exception(f"Session {session_id} not found")
  
  prompt = f"""
  Generate structured data for {data_type} based on this description: {description}
  
  Return a JSON object with the following structure:
  {{
    "variable_name": "suggested_variable_name",
    "data_type": "{data_type}",
    "value": "suggested_value_or_structure",
    "description": "{description}"
  }}
  
  Only return valid JSON, no other text.
  """
  
  instructions = "You are a data structure generator. Return only valid JSON."
  
  response = use_martian(prompt, instructions)
  
  try:
    structured_response = json.loads(response)
    sessionData[session_id]["structured_data"].append(structured_response)
    
    # Also store in variables for easy access
    var_name = structured_response.get("variable_name", f"{data_type}_{len(sessionData[session_id]['variables'])}")
    sessionData[session_id]["variables"][var_name] = structured_response.get("value")
    
    add_to_session(session_id, f"add_data({data_type}, {description})", response)
    
    return structured_response
  except json.JSONDecodeError:
    # If JSON parsing fails, store as raw text
    fallback_data = {
      "variable_name": f"{data_type}_{len(sessionData[session_id]['variables'])}",
      "data_type": data_type,
      "value": response,
      "description": description
    }
    sessionData[session_id]["structured_data"].append(fallback_data)
    add_to_session(session_id, f"add_data({data_type}, {description})", response)
    return fallback_data

class MartianService:
  def __init__(self):
    self.is_running = False
  
  def start(self):
    self.is_running = True
    print("Martian service started")
  
  def stop(self):
    self.is_running = False
    print("Martian service stopped")
  
  def process_request(self, message, instructions=None, session_id=None):
    if not self.is_running:
      raise Exception("Service not started")
    
    response = use_martian(message, instructions)
    
    if session_id:
      add_to_session(session_id, message, response)
    
    return response
  
  def get_session_data(self, session_id):
    return sessionData.get(session_id, {})
  
  def get_session_messages(self, session_id):
    return conversationSessions.get(session_id, {}).get("messages", [])

# Global service instance
martian_service = MartianService()

if __name__ == "__main__":
  # Test the service with sessions
  martian_service.start()
  
  # Create a database session
  db_session = create_session("database")
  print(f"Created database session: {db_session}")
  
  # Add structured data
  data_result = add_data(db_session, "user_table", "A table to store user information with id, name, email, and created_at fields")
  print("Added data:", data_result)
  
  # Process a regular request with session tracking
  response = martian_service.process_request("Write a Python function that calculates Mars orbital period.", session_id=db_session)
  print("Response:", response)
  
  # Check session data
  print("Session data:", martian_service.get_session_data(db_session))
  print("Session messages:", martian_service.get_session_messages(db_session))
  
  martian_service.stop()