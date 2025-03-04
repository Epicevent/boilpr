import streamlit as st
import torch
import gc

# Example: If you have multiple translation libraries
# (EasyNMT, MarianMT, MBART, etc.), you can unify them in a loader function:
from easynmt import EasyNMT
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModel

def load_translation_model(method_name: str):
    """
    Loads a translation model or sets up an API-based method 
    based on the selected method_name.
    Returns either a model object or a (tokenizer, model) tuple, depending on your approach.
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    if method_name == "Easy":
        translator = EasyNMT('opus-mt', device=device)
        return translator

    elif method_name == "Mbart50":
        tokenizer = AutoTokenizer.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
        model = AutoModelForSeq2SeqLM.from_pretrained("facebook/mbart-large-50-many-to-many-mmt").to(device)
        return (tokenizer, model)

    elif method_name == "MarianMT":
        # Example MarianMT for ko->en or en->ko
        tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-ko-en")
        model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-ko-en").to(device)
        return (tokenizer, model)

    elif method_name == "T5":
        tokenizer = AutoTokenizer.from_pretrained("t5-small")
        model = AutoModelForSeq2SeqLM.from_pretrained("t5-small").to(device)
        return (tokenizer, model)

    elif method_name == "Pegasus":
        tokenizer = AutoTokenizer.from_pretrained("google/pegasus-xsum")
        model = AutoModelForSeq2SeqLM.from_pretrained("google/pegasus-xsum").to(device)
        return (tokenizer, model)

    elif method_name == "Google Translate":
        # Google Translate might be an API-based solution (no local model)
        # Return None or some wrapper object indicating no local model is loaded
        return None

    # Fallback if none is selected
    return None

def render_sidebar():
    """Render sidebar with settings."""
    st.sidebar.header("⚙️ Settings")

    with st.sidebar.expander("🔤 Translation & Embedding Methods", expanded=True):
        translate_methods = ["Easy", "Mbart50", "MarianMT", "T5", "Pegasus", "Google Translate"]
        embedding_methods = ["SBERT", "BERT", "FastText", "GPT-3", "Word2Vec"]

        col1, col2 = st.columns(2)

        with col1:
            selected_translate_method = st.selectbox("Select Translation Method", translate_methods, index=0)

            # A button that triggers load/reload
            if st.button("Load/Reload Translation Model"):
                # 1) Unload previous model if exists
                if "translation_model" in st.session_state:
                    del st.session_state["translation_model"]
                    gc.collect()  # Encourage freeing GPU/CPU memory
                
                # 2) Load new model if not "Google Translate" (or whichever logic you prefer)
                if selected_translate_method != "Google Translate":
                    with st.spinner(f"Loading {selected_translate_method}..."):
                        st.session_state["translation_model"] = load_translation_model(selected_translate_method)
                    st.success(f"{selected_translate_method} loaded successfully!")
                else:
                    st.session_state["translation_model"] = None
                    st.info("Using Google Translate (no local model loaded).")

        with col2:
            st.selectbox("Select Embedding Method", embedding_methods, index=0)
    
    with st.sidebar.expander("📈 Query Parameters", expanded=True):
        st.slider("Number of Results (Top K)", min_value=1, max_value=10, value=5)

    # Example 'Clear All Data' button
    if st.sidebar.button("🧹 Clear All Data"):
        st.session_state.clear()
        st.success("Session state cleared!")
        # st.rerun()  # Usually you want to rerun after clearing to show a clean slate
