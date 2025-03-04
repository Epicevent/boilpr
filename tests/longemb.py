import ollama

def count_tokens(text: str) -> int:
    """
    Counts tokens in the text.
    (For demonstration, we split on whitespace.
    Replace with a proper tokenizer for production use.)
    """
    return len(text.split())

def get_model_context_length(model: str) -> int:
    """
    Query the model info using ollama.show() to determine its maximum context length (in tokens).
    Assumes that the response includes a key like "model_info" with "llama.context_length".
    """
    response = ollama.show(model=model)
    # For example, the context length might be under "model_info" -> "llama.context_length"
    context_length = response.get("model_info", {}).get("llama.context_length")
    if context_length is None:
        raise ValueError(f"Cannot determine context length for model '{model}'.")
    return context_length

def generate_embedding(text: str, model: str = "mxbai-embed-large") -> list:
    """
    Generate an embedding for the given text using the specified model.
    The function checks if the input text's token count exceeds the model's maximum context length.
    If so, it raises an error rather than silently truncating the text.
    """
    max_tokens = get_model_context_length(model)
    token_count = count_tokens(text)
    if token_count > max_tokens:
        raise ValueError(
            f"Input text is too long: {token_count} tokens (max allowed for model '{model}' is {max_tokens})."
        )
    
    response = ollama.embeddings(model=model, prompt=text)
    return response["embedding"]

if __name__ == "__main__":
    # Example with a short text that should work fine.
    text_normal = "This is a sample text that should be short enough."
    try:
        embedding = generate_embedding(text_normal)
        print("Short text embedding generated successfully. Vector length:", len(embedding))
    except Exception as e:
        print("Error generating embedding for short text:", e)
    
    # Example with an overly long text to trigger the error.
    # Here we create a long text by repeating a word many times.
    long_text = "word " * 5000  # Adjust multiplier as needed to exceed the model's context length.
    try:
        embedding = generate_embedding(long_text)
        print("Long text embedding generated successfully. Vector length:", len(embedding))
    except Exception as e:
        print("Error generating embedding for long text:", e)
