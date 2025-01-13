import streamlit as st
import uuid

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(page_title="📄🔍 RAG System Prototype", layout="wide")
st.title("📄🔍 RAG System Prototype")

# -----------------------------
# Initialize Session State
# -----------------------------
if "uploaded_documents" not in st.session_state:
    st.session_state["uploaded_documents"] = []

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = str(uuid.uuid4())

if "query_results" not in st.session_state:
    st.session_state["query_results"] = []

# -----------------------------
# Sidebar: Settings
# -----------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    
    with st.expander("🔤 Translation & Embedding Methods", expanded=True):
        # Embedding method selection
        translate_methods = ["Easy", "Mbart50", "MarianMT", "T5", "Pegasus", "Google Translate"]
        embedding_methods = ["SBERT", "BERT", "FastText", "GPT-3", "Word2Vec"]
        
        col1, col2 = st.columns(2)
        with col1:
            selected_translate = st.selectbox("Select Translation Method", translate_methods, index=0)
        with col2:
            selected_embedding = st.selectbox("Select Embedding Method", embedding_methods, index=0)
    
    with st.expander("📈 Query Parameters", expanded=True):
        # Number of results to display
        top_k = st.slider("Number of Results (Top K)", min_value=1, max_value=10, value=5)
    
    # Button to clear session state
    if st.button("🧹 Clear All Data"):
        st.session_state.clear()
        st.success("Session state cleared!")
        st.rerun()

# -----------------------------
# Document Upload Section
# -----------------------------
st.header("📄 Document Upload")

upload_col1, upload_col2 = st.columns([3, 1])

with upload_col1:
    uploaded_files = st.file_uploader(
        "Upload your documents (PDF/TXT)",
        accept_multiple_files=True,
        key=st.session_state["uploader_key"]
    )
    if st.button("📥 Upload"):
        if uploaded_files:
            new_files = False
            for uploaded_file in uploaded_files:
                file_info = {
                    "id": str(uuid.uuid4()),
                    "name": uploaded_file.name,
                    "size": len(uploaded_file.getvalue()),
                    "type": uploaded_file.type,
                    "data": uploaded_file.getvalue()
                }
                # Prevent duplicates based on file name
                if not any(doc["name"] == uploaded_file.name for doc in st.session_state["uploaded_documents"]):
                    st.session_state["uploaded_documents"].append(file_info)
                    new_files = True
            if new_files:
                st.success("Documents uploaded successfully!")
            else:
                st.info("No new documents to upload.")
        else:
            st.warning("No files selected.")
        
        # Reset the uploader
        st.session_state["uploader_key"] = str(uuid.uuid4())
        st.rerun()

# -----------------------------
# Display Uploaded Documents
# -----------------------------
if st.session_state["uploaded_documents"]:
    st.subheader("🗂️ Uploaded Documents")
    
    # Search functionality
    search_query = st.text_input("🔍 Search Documents:")
    if search_query:
        filtered_docs = [doc for doc in st.session_state["uploaded_documents"] if search_query.lower() in doc["name"].lower()]
    else:
        filtered_docs = st.session_state["uploaded_documents"]
    
    if filtered_docs:
        # Display documents in a table
        import pandas as pd
        doc_df = pd.DataFrame([{
            "Name": doc["name"],
            "Size (KB)": f"{doc['size'] / 1024:.2f}",
            "Type": doc["type"]
        } for doc in filtered_docs])
        st.table(doc_df)
        
        # Selection for deletion
        selected_docs_to_delete = st.multiselect("Select documents to delete:", [doc["name"] for doc in filtered_docs])
        
        if st.button("🗑️ Delete Selected Documents"):
            st.session_state["uploaded_documents"] = [
                doc for doc in st.session_state["uploaded_documents"]
                if doc["name"] not in selected_docs_to_delete
            ]
            st.success("Selected documents deleted!")
            st.rerun()
    else:
        st.info("No documents match your search.")

# -----------------------------
# Query Input Section
# -----------------------------
st.header("🔍 Query Input")

query_col1, query_col2 = st.columns([3, 1])

with query_col1:
    query = st.text_input("Enter your query:")
    submit_query = st.button("🔍 Submit Query")

    if submit_query and query:
        with st.spinner("Processing your query..."):
            # Simulate processing delay
            import time
            time.sleep(2)
            
            # Simulate query results
            st.session_state["query_results"] = [f"**Result {i+1}:** Placeholder text for result {i+1}." for i in range(top_k)]

        st.success("Query processed!")
    
    if st.session_state["query_results"]:
        st.subheader("📄 Query Results")
        for result in st.session_state["query_results"]:
            with st.expander(result.split(":")[0]):
                st.write(result.split(":")[1].strip())

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("👨‍💻 Built with [Streamlit](https://streamlit.io/) for RAG System Prototyping.")
