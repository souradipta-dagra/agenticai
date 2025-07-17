from user_functions_2 import analyze_legal_clauses, analyze_financial_clauses
from langchain_core.messages import HumanMessage

def load_clause_templates(filepath="clause_doc.txt"):
    legal_mandatory = []
    legal_optional = []
    financial_mandatory = []
    financial_optional = []
    clause_templates = {}

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("::")
            if len(parts) != 2:
                continue  # skip bad lines

            clause_info, template = parts
            try:
                category, importance, name = clause_info.split(":")
            except ValueError:
                continue  # skip invalid format

            clause_templates[name] = template.strip()

            if category == "Legal":
                if importance == "Mandatory":
                    legal_mandatory.append(name)
                else:
                    legal_optional.append(name)
            elif category == "Financial":
                if importance == "Mandatory":
                    financial_mandatory.append(name)
                else:
                    financial_optional.append(name)

    return legal_mandatory, legal_optional, financial_mandatory, financial_optional, clause_templates



def get_missing_clauses(text, legal_templates, financial_templates):
    legal_missing = eval(analyze_legal_clauses(text, legal_templates))["missing"]
    financial_missing = eval(analyze_financial_clauses(text, financial_templates))["missing"]
    return legal_missing + financial_missing

def generate_clause(chat_client, clause_name):
    prompt = (
        f"Write a single, final version of a concise, legally valid contract clause for: '{clause_name}'. "
    )
    response = chat_client.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


def extract_clause_from_standard_pdf(standard_pdf_text, clause_name, chat_client):
    """
    Try extracting clause from standard contract.
    If not found, fallback to GPT to generate it.
    Returns:
        clause_text (str): The extracted or generated clause.
        source (str): Either 'standard' or 'ai'.
    """
    prompt = f"""
You are a contract assistant AI.

Extract the full clause or paragraph related to "{clause_name}" from the standard agreement below.
If not found, return "NOT FOUND".

Standard Agreement:
\"\"\"
{standard_pdf_text[:3000]}
\"\"\"
"""
    response = chat_client.invoke([HumanMessage(content=prompt)])
    content = response.content.strip()

    if "NOT FOUND" in content or len(content) < 40:
        # Fallback to GPT
        fallback_prompt = f"""
Write a concise, legally valid contract clause for: "{clause_name}".
Return only the clause text.
"""
        fallback_response = chat_client.invoke([HumanMessage(content=fallback_prompt)])
        return fallback_response.content.strip(), "ai"
    
    return content, "standard"





