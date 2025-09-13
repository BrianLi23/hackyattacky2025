import cohere
import os
import difflib
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Cohere client with API key from environment variable
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.ClientV2(COHERE_API_KEY)

def cohere_llm_call(file_content, user_request):
    """Calls Cohere LLM to propose a file change."""
    prompt = (
        "You are an expert AI code editor. The user will provide you with the full content of a file "
        "and a request to modify it. Your ONLY output should be the complete, modified file content. "
        "Do not add any commentary, explanations, or code fences (```).\n"
        f"<file_content>\n{file_content}\n</file_content>\n\n<user_request>\n{user_request}\n</user_request>"
    )
    response = co.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": prompt}]
    )
    # For Cohere V2 API, the response structure is different
    return response.message.content[0].text

def get_llm_proposal(filepath, user_request):
    """Gets a proposed file change from Cohere LLM."""
    with open(filepath, 'r') as f:
        content = f.read()
    new_content = cohere_llm_call(content, user_request)
    return content.splitlines(True), new_content.splitlines(True)


# We reuse show_diff_and_confirm and write_file_content from Implementation 1

# --- Paste the functions here ---
def show_diff_and_confirm(original_lines, proposed_lines, filename):
    diff = difflib.unified_diff(original_lines, proposed_lines, fromfile=f'original: {filename}', tofile=f'modified: {filename}', lineterm='')
    print("\n--- PROPOSED CHANGE (from LLM) ---")
    diff_text = '\n'.join(list(diff))
    if not diff_text: print("No changes to apply."); return False
    print(diff_text)
    print("---------------------------------")
    while True:
        confirm = input("Apply this change? (y/n): ").lower().strip()
        if confirm == 'y': return True
        elif confirm == 'n': return False
        else: print("Invalid input.")

def write_file_content(filepath, lines):
    with open(filepath, 'w') as f: f.writelines(lines)
    print(f"✅ Changes applied to '{filepath}'")
# ---

def main_llm():
    print("LLM File Editor Agent. Type 'exit' to quit.")
    
    # We will assume the file is 'my_script.py' for simplicity
    filename = "my_script.py"
    if not os.path.exists(filename):
        print(f"File '{filename}' not found. Please create it first.")
        return

    while True:
        command = input(f"\nWhat change to make to '{filename}'? > ")
        if command.lower() == 'exit':
            break

        original_lines, proposed_lines = get_llm_proposal(filename, command)

        if show_diff_and_confirm(original_lines, proposed_lines, filename):
            write_file_content(filename, proposed_lines)
        else:
            print("🛑 Change cancelled.")

if __name__ == "__main__":
    with open("my_script.py", "w") as f:
        f.write("import os\n\ndef main():\n    print('hello')\n")
    main_llm()