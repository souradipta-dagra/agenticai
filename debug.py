from crewai import LLM
import os
# import litellm
# litellm._turn_on_debug()
from dotenv import load_dotenv

load_dotenv()
os.environ["AZURE_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY") 
os.environ["AZURE_API_BASE"] = os.getenv("AZURE_API_BASE") # "https://your-endpoint.openai.azure.com"
os.environ["AZURE_API_VERSION"] = "2024-12-01-preview"

azure_llm = LLM(
    model="azure/gpt-4o",
)

azure_response = azure_llm.call(
    "Hey, who are you?"
)

print(f'\nAzure Response:\n\n{azure_response}\n')