# agents.py
from crewai import Agent

def get_legal_agent(llm, legal_tool):
    return Agent(
        role='Legal Agent',
        goal='Identify missing legal clauses from a given document and return the  output format from in a good tabular form ',
        backstory='An expert legal reviewer with a reliable clause-checking tool.',
        verbose=True,
        allow_delegation=False,
        tools=[legal_tool],
        llm=llm  # no LLM; only uses tool
    )

def get_finance_agent(llm, finance_tool):
    return Agent(
        role='Finance Agent',
        goal='Identify missing financial clauses from a document  and return the  output format from in a good tabular form',
        backstory='A financial checker who uses automated tools to scan contracts.',
        verbose=True,
        allow_delegation=False,
        tools=[finance_tool],
        llm=llm  # no LLM; only uses tool
    )

def get_chat_agent(llm):
    return Agent(
        role='Chat Agent',
        goal='Answer any questions based on the content of the document and give the output in one line ',
        backstory='A helpful assistant who knows the uploaded document thoroughly.',
        verbose=True,
        allow_delegation=False,
        # tools=[chat_tool],
        llm=llm
    )


def get_email_agent(llm,email_tool):
    return Agent(
        role='Email Agent',
        goal='Send email by invoking the tool and send filename argument to the tool',
        backstory='A helpful assistant that sends email',
        verbose=True,
        allow_delegation=False,
        tools=[email_tool],
        llm=llm
    )


def get_add_clause_agent(llm,add_clause_tool):
    return Agent(
        role='Add Clause Agent',
        goal='Generate an one paragraph about the clause to be added and pass this content to the tool',
        backstory='A helpful assistant who knows the uploaded document thoroughly.',
        verbose=True,
        allow_delegation=False,
        tools=[add_clause_tool],
        llm=llm
    )

def get_download_agent(llm):
    return Agent(
        role='Download Agent',
        goal='To download the updated document to the user browser just return the text please click to download',
        backstory='A helpful assistant who downloads the updated document for the user.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )