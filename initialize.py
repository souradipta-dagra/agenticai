# # initialize.py
# import os
# from langchain.chat_models.azure_openai import AzureChatOpenAI
# from langchain.embeddings.azure_openai import AzureOpenAIEmbeddings
# from dotenv import load_dotenv

# load_dotenv()

# def initialize_azure_clients():
#     return AzureChatOpenAI(
#         azure_deployment="gpt-4o",
#         api_version="2024-08-01-preview",
#         api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#         azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#         temperature=0,
#         max_tokens=1500
#     ), AzureOpenAIEmbeddings(
#         azure_deployment="text-embedding-ada-002",
#         api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#         azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#         api_version="2024-08-01-preview",
#         chunk_size = 0
#     )
