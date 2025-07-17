
import streamlit as st
import os
from dotenv import load_dotenv
from crewai import Crew, Task, LLM
from langchain.chat_models.azure_openai import AzureChatOpenAI
from agents import get_legal_agent, get_finance_agent, get_chat_agent, get_email_agent, get_add_clause_agent, get_download_agent
from tools import DummyLegalClauseChecker, DummyFinanceClauseChecker, EmailSender, AddClause, DownloadClauseTool
from utils import extract_text_from_pdf
from router import get_agent_router

# --- Load environment variables ---
load_dotenv()

@st.cache_resource
def initialize_azure_clients():
    os.environ["OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
    return AzureChatOpenAI(
        azure_deployment="gpt-4o",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version="2024-08-01-preview",
        temperature=0,
        max_tokens=1500
    )

@st.cache_resource
def work_with_llm():
    os.environ["AZURE_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
    os.environ["AZURE_API_BASE"] = os.getenv("AZURE_API_BASE")
    os.environ["AZURE_API_VERSION"] = "2024-12-01-preview"
    return LLM(model="azure/gpt-4o")

# Setup paths
UPLOAD_DIR = "./uploaded"
GENERATE_DIR = "./generated_doc"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(GENERATE_DIR, exist_ok=True)

# Page layout
st.set_page_config(page_title="Contract Assistant", layout="wide")
# with st.sidebar:
#     st.markdown("Built using Streamlit + CrewAI")
 
st.title("🤖 Contract Assistant")

col, _, _ = st.columns([3, 1, 1])  # Adjust width ratios
with col:
    uploaded_file = st.file_uploader("Upload your contract (PDF)", type=["pdf"])

# === Init Phase ===
if uploaded_file:
    if "initialized" not in st.session_state:
        with open(os.path.join(UPLOAD_DIR, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        with open(os.path.join(GENERATE_DIR, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.session_state.text = extract_text_from_pdf(uploaded_file)
        st.session_state.llm = initialize_azure_clients()
        azure_llm = work_with_llm()

        # Tools & agents
        st.session_state.agents = {
            "legal": get_legal_agent(llm=azure_llm, legal_tool=DummyLegalClauseChecker()),
            "finance": get_finance_agent(llm=azure_llm, finance_tool=DummyFinanceClauseChecker()),
            "chat": get_chat_agent(llm=azure_llm),
            "email": get_email_agent(llm=azure_llm, email_tool=EmailSender()),
            "add clause": get_add_clause_agent(llm=azure_llm, add_clause_tool=AddClause()),
            "download": get_download_agent(llm=azure_llm)
        }

        st.session_state.agent_router = get_agent_router(st.session_state.llm)
        st.session_state.chat_history = []
        st.session_state.new_clauses = []
        st.session_state.initialized = True
        # st.success("✅ Agents initialized and document loaded.")

    # === Chat UI ===
    st.header("💬 Chat with Your Document")
    st.markdown("### 💡 Hint")

    st.markdown("""
    - **What are the missing legal clauses**
    - **What are the missing financial clauses**
    - **Add a clause &lt;clause_name&gt;**
    - **Download the document**
    - **Mail the document**
    """)
 
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"],width=1500):
            st.markdown(msg["content"], unsafe_allow_html=True)

    user_input = st.chat_input("Ask a question...", width=1500)
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        route_result = st.session_state.agent_router.run({"question": user_input}).strip().lower()
        agent = st.session_state.agents.get(route_result, st.session_state.agents["chat"])

        if route_result == "add clause":
            task = Task(
                description=f"Generate a clause based on: {user_input}",
                agent=agent,
                expected_output="Single-paragraph clause"
            )
        elif route_result == "download":
            from tools import DownloadClauseTool
            task = Task(description="Download Agent", agent=agent, expected_output="Confirm only")

            if not st.session_state.get("new_clauses"):
                with st.chat_message("assistant",width=1500):
                    st.warning("⚠️ No new clauses have been added.")
            else:
                pdf_tool = DownloadClauseTool()
                pdf_bytes = pdf_tool._run(
                    file_name=uploaded_file.name,
                    new_clauses=st.session_state["new_clauses"]
                )

                # with st.chat_message("assistant",width=1000):
                #     # st.markdown("✅ Here's your updated contract with appended clauses:")
                #     # st.download_button(
                #     #     label="📄 Download Updated Contract",
                #     #     data=pdf_bytes,
                #     #     file_name=f"updated_{uploaded_file.name}",
                #     #     mime="application/pdf"
                #     # )

        else:
            task = Task(
                description=f"Query: {user_input}, File: {uploaded_file.name}, Content: {st.session_state.text}",
                agent=agent,
                expected_output="Detailed response"
            )
        with st.spinner("🤖 Processing Agent..."):
            crew = Crew(agents=[agent], tasks=[task])
            result = crew.kickoff(inputs={'topic': user_input})

        # Store result or offer edit if clause
        if route_result == "add clause":
            st.session_state["editing_clause"] = {
                "name": "Custom Clause",
                "original": result,
                "edited": result
            }
            response = "✍️ Generated clause is editable below."
        else:
            response = result
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("user",width=1500):   
                st.markdown(user_input,unsafe_allow_html=True)
        with st.chat_message("assistant",width=1500):
                if route_result == "download":
                    st.markdown("✅ Here's your modified contract. Click below to download it:")
                    st.download_button(
                        label="📄 Download Contract",
                        data=pdf_bytes,  # bytes object
                        file_name=f"updated_{uploaded_file.name}",
                        mime="application/pdf"
                    )
                else:
                 st.markdown(response, unsafe_allow_html=True)
            

    # === Edit Clause Interface ===
    # Editing UI for clause
    if "editing_clause" in st.session_state:
        st.markdown("### ✏️ Edit Clause")

        clause_data = st.session_state["editing_clause"]
        
        clause_name = st.text_input("Clause Title", value=clause_data.get("name", "Custom Clause"),width=1500)
        clause_text = st.text_area("Edit the generated clause below:", value=clause_data.get("edited", ""), height=200,width=1500)

        st.session_state["editing_clause"]["name"] = clause_name
        st.session_state["editing_clause"]["edited"] = clause_text

        if "new_clauses" not in st.session_state:
            st.session_state["new_clauses"] = []

        if st.button("✅ Confirm & Append Clause"):
            st.session_state["new_clauses"].append({
                "name": clause_name,
                "text": clause_text
            })
            # st.success(f"✅ Clause **{clause_name}** added to final PDF.")
            del st.session_state["editing_clause"]


    if st.session_state["new_clauses"]:
        with st.expander("📎 View Appended Clauses",width=1500):
            for c in st.session_state["new_clauses"]:
                st.markdown(f"**{c['name']}**", unsafe_allow_html=True)
                st.markdown(
                    f"<div style='font-size: 14px; line-height: 1.4;'>{c['text'].replace(chr(10), '<br>')}</div>",
                    unsafe_allow_html=True
                )
                st.markdown("---")


