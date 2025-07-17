import json
from typing import List

def analyze_legal_clauses(contract_text: str, template_clauses: List[str]) -> str:
    """
    Analyzes the presence of legal clauses in the contract text.

    Args:
        contract_text (str): The full text of the contract.
        template_clauses (List[str]): A list of legal clauses to check for in the contract.

    Returns:
        str: A JSON string indicating which clauses are present and which are missing.
    """
    present, missing = [], []
    lower_text = contract_text.lower()
    for clause in template_clauses:
        (present if clause.lower() in lower_text else missing).append(clause)
    result = {"present": present, "missing": missing}
    return json.dumps(result, indent=2)

def analyze_financial_clauses(contract_text: str, template_clauses: List[str]) -> str:
    """
    Analyzes the presence of financial clauses in the contract text.

    Args:
        contract_text (str): The full text of the contract.
        template_clauses (List[str]): A list of financial clauses to check for in the contract.

    Returns:
        str: A JSON string indicating which clauses are present and which are missing.
    """
    present, missing = [], []
    lower_text = contract_text.lower()
    for clause in template_clauses:
        (present if clause.lower() in lower_text else missing).append(clause)
    result = {"present": present, "missing": missing}
    return json.dumps(result, indent=2)
