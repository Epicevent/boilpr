import streamlit as st
import uuid

# App title and configuration
st.set_page_config(page_title="", layout="wide")
st.title("📄🔍 RAG System Prototype")

# -----------------------------
# Sidebar for embedding selection and parameters
# -----------------------------
with st.sidebar:
    st.header("Settings")
    
    # Embedding method selection
    translate_methods = ["Easy","Mbart50","MarianMT","T5","Pegasus","Pegasus","google"]
    embedding_methods = ["SBERT", "BERT", "FastText", "GPT-3", "Word2Vec"]
    selected_translate = st.selectbox("Select Translate Method", translate_methods, index=0)
    selected_embedding = st.selectbox("Select Embedding Method", embedding_methods, index=0)
    
    # Number of results to display
    top_k = st.slider("Number of Results (Top K)", min_value=1, max_value=10, value=5)

    # Button to clear session state
    if st.button("Clear All Data"):
        st.session_state.clear()
        st.success("Session state cleared!")
        st.rerun()

# -----------------------------
# Initialize session state
# -----------------------------
if "uploaded_documents" not in st.session_state:
    st.session_state["uploaded_documents"] = []

# Use a dynamic key for resetting the uploader
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = str(uuid.uuid4())

if "query_results" not in st.session_state:
    st.session_state["query_results"] = []

# -----------------------------
# Document Upload Section
# -----------------------------
st.header("📄 Document Upload")

# 1) The file uploader has a dynamic key
uploaded_files = st.file_uploader(
    "Upload your documents (PDF/TXT)",
    accept_multiple_files=True,
    key=st.session_state["uploader_key"]
)

# 2) An "Upload" button that moves the files into session_state
if st.button("Upload"):
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_info = {
                "name": uploaded_file.name,
                "size": len(uploaded_file.getvalue())
            }
            # Prevent duplicates
            if file_info not in st.session_state["uploaded_documents"]:
                st.session_state["uploaded_documents"].append(file_info)
        st.success("Documents uploaded successfully!")
    else:
        st.warning("No files selected.")

    # 3) Generate a new key to reset/clear the file uploader
    st.session_state["uploader_key"] = str(uuid.uuid4())
    st.rerun()

# -----------------------------
# Display & delete uploaded documents
# -----------------------------
if st.session_state["uploaded_documents"]:
    st.subheader("Uploaded Documents")
    
    doc_names = [doc["name"] for doc in st.session_state["uploaded_documents"]]
    
    # Multi-select for deletion
    selected_docs_to_delete = st.multiselect("Select documents to delete:", doc_names)
    
    # Delete button
    if st.button("Delete Selected Documents"):
        st.session_state["uploaded_documents"] = [
            doc for doc in st.session_state["uploaded_documents"]
            if doc["name"] not in selected_docs_to_delete
        ]
        st.success("Selected documents deleted!")
        st.rerun()
    
    # Show remaining docs
    for doc in st.session_state["uploaded_documents"]:
        st.write(f"- **{doc['name']}** ({doc['size']} bytes)")

# -----------------------------
# Query Input Section
# -----------------------------
st.header("🔍 Query Input")
query = st.text_input("Enter your query:")

if query:
    st.write(f"**Selected Embedding**: {selected_embedding}")
    st.write(f"**Query**: {query}")
    st.write(f"**Top K Results**: {top_k}")
    
    # Simulate query results
    st.subheader("Query Results")
    for i in range(top_k):
        st.markdown(f"**Result {i+1}:** Placeholder text for result {i+1}.")

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("👨‍💻 Built with Streamlit for RAG System Prototyping.")
