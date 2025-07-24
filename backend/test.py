from openai import OpenAI
import json
import os

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded .env file")
except ImportError:
    print("Note: python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"Note: Could not load .env file: {e}")

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("Error: OPENAI_API_KEY environment variable is not set!")
    print("\nTo fix this:")
    print("1. Copy env_template.txt to .env in the root directory")
    print("2. Edit .env and replace 'sEPLACE_WITH_YOUR_OPENAI_API_KEY_HERE' with your actual API key")
    print("3. Install python-dotenv: pip install python-dotenv")
    print("\nAlternatively, set it directly:")
    print("Windows: set OPENAI_API_KEY=your_api_key_here")
    exit(1)

# Initialize the OpenAI client
client = OpenAI(api_key=api_key)

# Step 1: Define the actual tool/function
def printer_tool(message: str):
    print(f"[Printer Tool test hereOutput] {message}")
    return f"Message '{message}' printed successfully."

# Step 2: Define the tool in OpenAI format
tools = [
    {
        "type": "function",
        "function": {
            "name": "printer_tool",
            "description": "Prints a message to the console",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to print"
                    }
                },
                "required": ["message"]
            }
        }
    }
]

# Step 3: Ask the LLM something that triggers the tool
user_prompt = "Can you print Hello World?"

# Step 4: Call the LLM with tool definitions
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": user_prompt}
    ],
    tools=tools,
    tool_choice="auto"
)

# Step 5: Parse and execute the tool if needed
message = response.choices[0].message

if message.tool_calls:
    tool_call = message.tool_calls[0]
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name == "printer_tool":
        result = printer_tool(**arguments)

        # Step 6: Return result to the LLM
        final_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_prompt},
                message,
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                }
            ]
        )
        print(f"\n[LLM Final Reply] {final_response.choices[0].message.content}")
else:
    print("[LLM Reply] No function was called.")
    print(f"[LLM Direct Reply] {message.content}")
