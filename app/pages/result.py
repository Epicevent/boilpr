import streamlit as st

def show_result():
    """
    Displays a list or dropdown of uploaded documents.
    Allows the user to preview the text content in a text area.
    Provides a download button for convenience.
    """
    st.header("Result Page")

    # 1) Check if we have documents
    if "uploaded_documents" not in st.session_state or not st.session_state["uploaded_documents"]:
        st.warning("No documents uploaded yet. Please upload files on the 'Upload' page.")
        return

    # 2) Build a list of document names
    doc_names = [doc["name"] for doc in st.session_state["uploaded_documents"]]

    # 3) Let the user choose which file to view
    selected_name = st.selectbox("Select a file to view:", doc_names)

    # 4) Retrieve the selected document from session_state
    selected_doc = next((doc for doc in st.session_state["uploaded_documents"] if doc["name"] == selected_name), None)
    if not selected_doc:
        st.error("Selected document not found.")
        return

    # 5) Decode the document data into a string (assuming it's text-based)
    #    If your code sometimes stores raw PDF bytes, you'll need a separate way
    #    to handle PDF display. But for .txt or converted-from-.hwp data, this is fine.
    try:
        text_content = selected_doc["data"].decode("utf-8", errors="replace")
    except Exception as e:
        st.error(f"Error decoding text: {e}")
        return

    # 6) Display the text in a large text area
    st.subheader(f"Preview: {selected_doc['name']}")
    st.text_area("File Content", text_content, height=400)

    # 7) Provide a Download button for the user to save the text
    #    We'll guess a .txt extension. Adjust as needed if your document is actually PDF or something else.
    st.download_button(
        label="Download File as .txt",
        data=selected_doc["data"],
        file_name=f"{selected_doc['name']}.txt",
        mime="text/plain"
    )
