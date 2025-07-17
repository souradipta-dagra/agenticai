# router.py
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


# LLM decides which agent to call
def get_agent_router(llm):
    router_prompt = PromptTemplate.from_template("""
    You are an intelligent routing agent designed to classify user questions based on their intent.

    Your task is to assign the question to one of the following categories:

    1. "legal" – Questions about legal clauses, contract obligations, terms and conditions, or regulatory compliance.
    2. "finance" – Questions related to payments, penalties, revenue, cost structures, or other financial terms.
    3. "chat" – General or factual inquiries about the document that do not fall under legal or financial analysis.
    4. "email" – Requests related to sending emails, generating email drafts, or follow-up communication.
    5. "add clause" – Questions asking to insert or add new legal or financial clauses into the document.
    6. "download" - Request to download or download updated document

    ---
    **User Question:**  
    {question}

    Respond with just one word from the following:  
    "legal", "finance", "chat", "email",  "add clause".
    Do not include any explanation or punctuation.
    """)
    return LLMChain(llm=llm, prompt=router_prompt)
