import streamlit as st


def render_add_clause():

    st.markdown("What clause you want to add legal of financial ?")
    if "clause_type" not in st.session_state:
        st.session_state.clause_type = "legal"

# Display radio buttons
    clause_type = st.radio(
        "Select Clause Type:",
        options=["⚖️ Legal", "💵 Finance"],
        index=0 if st.session_state.clause_type == "legal" else 1,
        horizontal=True
    )

    ...
