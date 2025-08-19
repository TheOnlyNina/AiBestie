import os

# ✅ Use the correct environment variable name
OPENAI_API_KEY = os.getenv("OpenAI_Key")

if not OPENAI_API_KEY:
    raise ValueError("⚠️ OpenAI API key not found. Make sure it's set as OPENAI_API_KEY in your environment.")
