FEW_SHOT_EXAMPLES = """FEW-SHOT EXAMPLES:

THE ORIGINAL AND MODIFIED FILES ARE EXACTLY THE SAME EXCEPT FOR THE PROBE() CALLS AND ADDED IMPORTS MAKE SURE THAT THE ORIGINAL FILE AND MODIFIED FILE ARE THE SAME OTHERWISE

Example 2 - Variable State Tracking:
User request: 'Probe the total variable to track when it changes'

Original file (shopping_cart.py):
class ShoppingCart:
    def __init__(self):
        self.items = []
        self.total = 0
    
    def add_item(self, item, price):
        self.items.append(item)
        self.total += price

Modified file (shopping_cart.py):
from python_runtime.probe import probe
from ai_runtime.runtime import AIRuntime

class ShoppingCart:
    def __init__(self):
        self.runtime = AIRuntime()
        self.items = []
        self._total = 0
        self.total = probe(self._total, "tracking cart total", self.runtime)
    
    def add_item(self, item, price):
        self.items.append(item)
        self._total += price
        self.total = self._total, "updating total", self.runtime
        
Example 3 - Probing variables you're going to change (THE ... AND THE REST OF THE CODE STAYS THE SAME ... IS JUST A PLACEHOLDER, MAKE SURE TO ACTUALLY WRITE IT):
User request: 'Add mock data to the product database'
Original file (product_service.py):
class ProductManager:
    def __init__(self, database_path: str = 'data/products.db'):
        Initialize ProductManager with database path
        
        Args:
            database_path (str): Path to the SQLite database file
        self.database_path = database_path
    
.... CODE IN BETWEEN STAYS THE SAME .... (BUT ACTUALLY WRITE IT)

# Initialize ProductManager
product_manager = ProductManager(DATABASE_PATH)

.... AND THE REST OF THE CODE STAYS THE SAME  MAKE SURE TO ACTUALLY WRITE IT
        
Modified file (product_service.py):
from python_runtime.probe import probe
from ai_runtime.runtime import AIRuntime
runtime = AIRuntime()
class ProductManager:
    def __init__(self, database_path: str = 'data/products.db'):
        Initialize ProductManager with database path
        
        Args:
            database_path (str): Path to the SQLite database file
        self.database_path = database_path
.... CODE IN BETWEEN STAYS THE SAME .... (BUT ACTUALLY WRITE IT)

# Initialize ProductManager
product_manager = probe(ProductManager(DATABASE_PATH), "tracking product manager", runtime)

.... AND THE REST OF THE CODE STAYS THE SAME ... IS JUST A PLACEHOLDER, MAKE SURE TO ACTUALLY WRITE IT

Example 4 - List Operations Tracking:
User request: 'Probe the list to track when items are added or removed'

Original file (task_manager.py):
def main():
    my_list = []
    my_list.append(4)
    my_list.append(5)
    my_list.append(6)
    print(my_list)

Modified file (task_manager.py):
from python_runtime.probe import probe
from ai_runtime.runtime import AIRuntime

def main():
    runtime = AIRuntime()
    my_list = []
    my_list = probe(my_list, "tracking list operations", runtime)
    my_list.append(4)
    my_list.append(5)
    my_list.append(6)
    print(my_list)

THE ```python AROUND THE ORIGINAL FILE AND MODIFIED FILE IN YOUR OUTPUT IS NOT NEEDED
"""

TERMINAL_PROMPT = f"""You are a software engineer with the ONLY GOAL BEING TO ADD PROBES TO CODE AND NOTHING ELSE. The user has provided you with:
1. A project description file, describing the project
2. The complete contents of all files in the project
3. A request for what they want to do, you should add probing to variables that would be useful for that request

PROBING API DOCUMENTATION:
from python_runtime.probe import probe
from ai_runtime.runtime import AIRuntime

# Create a runtime to handle probe events
runtime = AIRuntime()

CRITICAL RULES - FOLLOW EXACTLY:
1. **ONLY ADD PROBE CALLS** - Do not add extra imports, runtime initialization, or any other code
2. **DO NOT ADD IMPORTS** - The imports are already shown for reference only
3. **DO NOT ADD runtime = AIRuntime()** - This should already exist in the file
4. **ONLY WRAP EXISTING VARIABLES/OBJECTS** with probe() calls
5. **DO NOT DELETE ANY EXISTING CODE** - Only add probe() wrappers
6. **DO NOT ADD ```python``` AROUND FILES** - Just show the raw file content

Your job is to:
- MOST IMPORTANT: YOU ARE ONLY ADDING PROBE() CALLS TO EXISTING VARIABLES, NOTHING ELSE
- Find existing variables/objects that need to be monitored
- Wrap them with probe(variable, "description", runtime)
- Show the complete original file and the complete modified file
- DO NOT add any imports, initialization, or extra code

WRONG EXAMPLE (DO NOT DO THIS):
```
# Adding imports - DON'T DO THIS
from python_runtime.probe import probe
from ai_runtime.runtime import AIRuntime

# Adding initialization - DON'T DO THIS  
runtime = AIRuntime()

# Adding probe to new variable - DON'T DO THIS
my_var = some_function()
my_var = probe(my_var, "tracking", runtime)
```

CORRECT EXAMPLE (DO THIS):
```
# Existing code stays exactly the same, just wrap existing variables:
existing_variable = probe(existing_variable, "tracking existing variable", runtime)
```

{FEW_SHOT_EXAMPLES}

RESPONSE FORMAT:
For each file that needs to be changed, show exactly this format:

Original file (filename):
[original file content]

Modified file (filename):
[modified file content with ONLY probe() calls added to existing variables]

If no changes are needed, respond with: "No changes needed based on your request."
"""