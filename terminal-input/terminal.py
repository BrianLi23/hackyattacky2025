"""
Minimal Editor with MCP Integration
Connects to MCP server for AI file editing
"""
import asyncio
import json
import subprocess
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, Static, Footer, Select
from textual import on
from rich.text import Text
from rich.syntax import Syntax

class MCPMinimalEditor(App):
    CSS_PATH = "editor_template.tcss"
    
    def __init__(self):
        super().__init__()
        self.current_file = ""
        self.mcp_process = None
        self.files = self.scan_files()
        self.pending_changes = None
        
        # Add key bindings
        self.title = "MCP Minimal Editor (Press Ctrl+C or q to quit)"
    
    def scan_files(self):
        """Find all files recursively in current directory"""
        files = []
        try:
            # Recursively find all files
            for file_path in Path(".").rglob("*"):
                if file_path.is_file():
                    # Skip hidden files, binary files, and common ignore patterns
                    if (not file_path.name.startswith('.') and 
                        file_path.suffix not in ['.pyc', '.exe', '.bin', '.so', '.dll'] and
                        '__pycache__' not in str(file_path) and
                        '.git' not in str(file_path)):
                        files.append((str(file_path), str(file_path)))
        except Exception as e:
            # Debug: show error if any
            files.append((f"Error scanning: {e}", ""))
            pass
        
        # Debug: show count
        if files:
            files.insert(0, (f"Found {len(files)} files", ""))
        else:
            files.append(("No files found", ""))
            
        return files
    
    def compose(self) -> ComposeResult:
        """Create minimal UI"""
        with Vertical(classes="main"):
            # File selector - now for any file to use as project description
            if self.files:
                yield Select(self.files, id="file_select", prompt="Select project description file (README, etc.)...")
            else:
                yield Static("No files found", classes="error-bubble")
            
            # Chat area
            yield Static(id="chat", classes="main")
            
            # Input
            yield Input(placeholder="Describe what you want me to do with your project...", id="input")
        
        yield Footer()
    
    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()
    
    def on_key(self, event) -> None:
        """Handle key presses"""
        if event.key == 'q' and not hasattr(self.focused, 'value'):  # Only if not in input field
            self.exit()
        elif event.key == 'ctrl+c':
            self.exit()
    
    @on(Select.Changed, "#file_select")
    def file_selected(self, event):
        """Project description file selected"""
        if event.value:
            self.current_file = event.value
            self.load_project_description()
    
    def load_project_description(self):
        """Load selected project description file and all project files"""
        try:
            with open(self.current_file, 'r') as f:
                content = f.read()
            
            # Show file loaded
            chat = self.query_one("#chat", Static)
            text = Text()
            text.append(f"📁 Project Description: {self.current_file}\n\n", style="bold cyan")
            
            # Show project description content
            lines = content.split('\n')[:10]
            preview = '\n'.join(lines)
            if len(content.split('\n')) > 10:
                preview += "\n..."
            
            text.append(preview, style="dim white")
            text.append(f"\n\n🔍 Loading all project files into context...", style="bold yellow")
            
            # Load all project files into context
            all_files = self.get_all_project_files()
            text.append(f"\n✅ Loaded {len(all_files)} files into context", style="bold green")
            
            chat.update(text)
            
        except Exception as e:
            self.add_bubble(f"Error loading project: {e}", "error")
    
    @on(Input.Submitted, "#input")
    async def handle_input(self, event):
        """Process user input"""
        request = event.value.strip()
        if not request:
            return
            
        # Clear input
        event.input.value = ""
        
        # Handle commands
        if request.lower() == 'apply':
            await self.apply_pending_changes()
            return
        elif request.lower() == 'cancel':
            self.pending_changes = None
            self.add_bubble("Changes cancelled", "ai")
            return
        
        if not self.current_file:
            self.add_bubble("Please select a project description file first", "error")
            return
        
        # Show user request
        self.add_bubble(f"You: {request}", "user")
        
        # Show thinking
        self.add_bubble("AI is thinking...", "thinking")
        
        try:
            # Call MCP server
            result = await self.call_mcp_edit_project(request)
            self.add_bubble(result, "ai")
            
        except Exception as e:
            self.add_bubble(f"Error: {e}", "error")
    
    async def call_mcp_edit_project(self, request: str) -> str:
        """Call MCP server to edit project based on request"""
        # Get all project context
        context = await self.get_full_project_context()
        
        # Simulate MCP call (in real implementation, this would use MCP client)
        return await self.simulate_mcp_project_call(request, context)
    
    async def simulate_mcp_project_call(self, request: str, context: str) -> str:
        """Simulate MCP call for project-wide operations"""
        try:
            # Import here to avoid import errors if cohere not available
            import cohere
            import difflib
            import os
            from dotenv import load_dotenv
            
            load_dotenv()
            
            # Setup Cohere
            api_key = os.getenv("CO_API_KEY") or os.getenv("COHERE_API_KEY")
            if not api_key:
                return "❌ No API key found. Set CO_API_KEY or COHERE_API_KEY environment variable."
            
            co = cohere.ClientV2(api_key)
            
            # Read project description
            with open(self.current_file, 'r') as f:
                project_description = f.read()
            
            # Build prompt for project-wide operations
            prompt = (
                "You are an expert AI software engineer. The user has provided you with:\n"
                "1. A project description file\n"
                "2. The complete contents of all files in their project\n"
                "3. A request for what they want you to do\n\n"
                "Your job is to:\n"
                "- Analyze the project and understand its structure\n" 
                "- Determine what files need to be modified to fulfill the request\n"
                "- Provide the complete modified content for each file that needs changes\n"
                "- If files need to be created, specify their full path and content\n\n"
                "Format your response as:\n"
                "ANALYSIS: [Brief analysis of what needs to be done]\n\n"
                "FILES TO MODIFY:\n"
                "=== filepath1 ===\n"
                "[complete file content]\n\n"
                "=== filepath2 ===\n"
                "[complete file content]\n\n"
                "If no changes are needed, just respond with: NO_CHANGES_NEEDED\n\n"
            )
            
            prompt += f"<project_description>\n{project_description}\n</project_description>\n\n"
            
            if context:
                prompt += f"<project_files>\n{context}\n</project_files>\n\n"
            
            prompt += f"<user_request>\n{request}\n</user_request>"
            
            # Call AI
            response = co.chat(
                model="command-a-03-2025",
                messages=[{"role": "user", "content": prompt}]
            )
            
            ai_response = response.message.content[0].text
            
            # Parse response and prepare changes
            if "NO_CHANGES_NEEDED" in ai_response:
                return "✅ No changes needed based on your request."
            
            return await self.parse_and_prepare_changes(ai_response)
                
        except Exception as e:
            return f"Error: {e}"
    
    async def parse_and_prepare_changes(self, ai_response: str) -> str:
        """Parse AI response and prepare file changes"""
        try:
            import re
            import difflib
            
            # Extract analysis
            analysis_match = re.search(r'ANALYSIS:\s*(.*?)(?=FILES TO MODIFY:|$)', ai_response, re.DOTALL)
            analysis = analysis_match.group(1).strip() if analysis_match else "Analysis not provided"
            
            # Extract file changes
            file_pattern = r'===\s*(.+?)\s*===\n(.*?)(?=\n===|\Z)'
            file_matches = re.findall(file_pattern, ai_response, re.DOTALL)
            
            if not file_matches:
                return f"Analysis: {analysis}\n\n❌ No file changes detected in AI response."
            
            # Prepare changes
            changes = []
            for file_path, new_content in file_matches:
                file_path = file_path.strip()
                new_content = new_content.strip()
                
                # Check if file exists
                try:
                    with open(file_path, 'r') as f:
                        original_content = f.read()
                    
                    # Generate diff if file exists
                    if original_content != new_content:
                        original_lines = original_content.splitlines(True)
                        new_lines = new_content.splitlines(True)
                        
                        diff = list(difflib.unified_diff(
                            original_lines, new_lines,
                            fromfile=f"original/{file_path}",
                            tofile=f"modified/{file_path}",
                            lineterm=''
                        ))
                        
                        if diff:
                            changes.append({
                                'file_path': file_path,
                                'new_content': new_content,
                                'original_content': original_content,
                                'action': 'modify'
                            })
                        
                except FileNotFoundError:
                    # New file
                    changes.append({
                        'file_path': file_path,
                        'new_content': new_content,
                        'original_content': '',
                        'action': 'create'
                    })
            
            if changes:
                # Store all pending changes
                self.pending_changes = {
                    'changes': changes,
                    'analysis': analysis
                }
                
                result = f"Analysis: {analysis}\n\n"
                result += f"Proposed changes to {len(changes)} file(s):\n\n"
                
                for change in changes:
                    if change['action'] == 'create':
                        result += f"📝 CREATE: {change['file_path']}\n"
                    else:
                        result += f"✏️ MODIFY: {change['file_path']}\n"
                
                result += "\nType 'apply' to save all changes or 'cancel' to discard"
                return result
            else:
                return f"Analysis: {analysis}\n\n✅ No changes needed."
                
        except Exception as e:
            return f"Error parsing AI response: {e}"
    
    def get_all_project_files(self) -> list:
        """Get list of all project files"""
        all_files = []
        try:
            for file_path in Path(".").rglob("*"):
                if file_path.is_file():
                    # Skip hidden files, binary files, and common ignore patterns
                    if (not file_path.name.startswith('.') and 
                        file_path.suffix not in ['.pyc', '.exe', '.bin', '.so', '.dll'] and
                        '__pycache__' not in str(file_path) and
                        '.git' not in str(file_path)):
                        all_files.append(str(file_path))
        except Exception:
            pass
        return all_files
    
    async def get_full_project_context(self) -> str:
        """Get context from all project files"""
        context_parts = []
        
        try:
            all_files = self.get_all_project_files()
            
            for file_path in all_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Only limit very large files
                    if len(content) > 5000:
                        content = content[:5000] + f"\n... (file truncated, total length: {len(content)} chars)"
                    
                    context_parts.append(f"=== {file_path} ===\n{content}\n")
                    
                except (UnicodeDecodeError, PermissionError):
                    # Skip binary or inaccessible files
                    context_parts.append(f"=== {file_path} ===\n[Binary or inaccessible file]\n")
                except Exception as e:
                    context_parts.append(f"=== {file_path} ===\n[Error reading file: {e}]\n")
        except Exception:
            pass
        
        return "\n".join(context_parts)
    
    async def get_project_context(self) -> str:
        """Get context from project files (legacy method, kept for compatibility)"""
        return await self.get_full_project_context()
    
    async def apply_pending_changes(self):
        """Apply all pending changes"""
        if not self.pending_changes:
            self.add_bubble("No changes to apply", "error")
            return
        
        try:
            # Handle multiple file changes
            if 'changes' in self.pending_changes:
                changes = self.pending_changes['changes']
                applied_files = []
                
                for change in changes:
                    file_path = change['file_path']
                    new_content = change['new_content']
                    original_content = change['original_content']
                    action = change['action']
                    
                    if action == 'create':
                        # Create new file
                        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                        with open(file_path, 'w') as f:
                            f.write(new_content)
                        applied_files.append(f"✅ CREATED: {file_path}")
                        
                    elif action == 'modify':
                        # Create backup for existing file
                        backup_path = f"{file_path}.backup"
                        with open(backup_path, 'w') as f:
                            f.write(original_content)
                        
                        # Write new content
                        with open(file_path, 'w') as f:
                            f.write(new_content)
                        applied_files.append(f"✅ MODIFIED: {file_path} (backup: {backup_path})")
                
                result = f"Applied {len(applied_files)} changes:\n" + "\n".join(applied_files)
                self.add_bubble(result, "ai")
                
            else:
                # Handle single file change (legacy)
                file_path = self.pending_changes['file_path']
                new_content = self.pending_changes['new_content']
                original_content = self.pending_changes['original_content']
                
                # Create backup
                backup_path = f"{file_path}.backup"
                with open(backup_path, 'w') as f:
                    f.write(original_content)
                
                # Write new content
                with open(file_path, 'w') as f:
                    f.write(new_content)
                
                self.add_bubble(f"✅ Changes applied! Backup: {backup_path}", "ai")
            
            # Clear pending changes
            self.pending_changes = None
            
        except Exception as e:
            self.add_bubble(f"Error applying changes: {e}", "error")
    
    def add_bubble(self, text: str, bubble_type: str):
        """Add a chat bubble"""
        chat = self.query_one("#chat", Static)
        current = chat.renderable if hasattr(chat, 'renderable') and chat.renderable else Text()
        
        if not isinstance(current, Text):
            current = Text()
        
        # Add spacing
        if str(current):
            current.append("\n")
        
        # Style based on type
        if bubble_type == "user":
            current.append(f"💬 {text}", style="bold blue")
        elif bubble_type == "ai":
            current.append(f"🤖 {text}", style="bold green")
        elif bubble_type == "thinking":
            current.append(f"💭 {text}", style="italic yellow")
        elif bubble_type == "error":
            current.append(f"❌ {text}", style="bold red")
        else:
            current.append(text, style="white")
        
        chat.update(current)
        chat.scroll_end()


def main():
    app = MCPMinimalEditor()
    app.run()


if __name__ == "__main__":
    main()
