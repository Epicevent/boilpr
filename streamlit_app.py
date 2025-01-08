import streamlit as st

# App title and configuration
st.set_page_config(page_title="RAG System Prototype", layout="wide")
st.title("📄🔍 RAG System Prototype")

# Sidebar for embedding selection and parameters
with st.sidebar:
    st.header("Settings")
    
    # Embedding method selection
    embedding_methods = ["SBERT", "BERT", "FastText", "GPT-3", "Word2Vec"]
    selected_embedding = st.selectbox("Select Embedding Method", embedding_methods, index=0)
    
    # Number of results to display
    top_k = st.slider("Number of Results (Top K)", min_value=1, max_value=10, value=5)

    # Button to clear session state
    if st.button("Clear All Data"):
        st.session_state.clear()
        st.success("Session state cleared!")

# Initialize session state
if "uploaded_documents" not in st.session_state:
    st.session_state["uploaded_documents"] = []
if "query_results" not in st.session_state:
    st.session_state["query_results"] = []

# Document Upload Section
st.header("📄 Document Upload")
uploaded_files = st.file_uploader("Upload your documents (PDF/TXT)", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_info = {"name": uploaded_file.name, "size": len(uploaded_file.getvalue())}
        if file_info not in st.session_state["uploaded_documents"]:
            st.session_state["uploaded_documents"].append(file_info)
    st.success("Documents uploaded successfully!")

# Display uploaded documents
if st.session_state["uploaded_documents"]:
    st.subheader("Uploaded Documents")
    for doc in st.session_state["uploaded_documents"]:
        st.write(f"- **{doc['name']}** ({doc['size']} bytes)")

# Query Input Section
st.header("🔍 Query Input")
query = st.text_input("Enter your query:")

if query:
    st.write(f"**Selected Embedding**: {selected_embedding}")
    st.write(f"**Query**: {query}")
    st.write(f"**Top K Results**: {top_k}")
    
    # Simulate results (static placeholders)
    st.subheader("Query Results")
    for i in range(top_k):
        st.markdown(f"**Result {i+1}:** Placeholder text for result {i+1}.")

# Footer
st.markdown("---")
st.markdown("👨‍💻 Built with Streamlit for RAG System Prototyping.")
