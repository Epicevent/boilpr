import ollama
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

# Connect to the persistent DB using the same "chroma_db" folder.
client = chromadb.PersistentClient(
    path="chroma_db",
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)

# Retrieve the existing collection named "docs"
collection = client.get_collection(name="docs")

# Define a query prompt.
prompt = "저는 요리를 좋아합니다."

# Generate an embedding for the query prompt.
response = ollama.embeddings(model="mxbai-embed-large", prompt=prompt)
query_embedding = response["embedding"]

# Query the vector DB for the most relevant document.
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=1
)
retrieved_doc = results["documents"][0][0]

# Form a RAG prompt using the retrieved document as context.
rag_prompt = f"Using this data: {retrieved_doc}. Respond in Korean to this prompt: {prompt}"

# Generate a response using a language model.
output = ollama.generate(model="exaone3.5:32b", prompt=rag_prompt)

print("Retrieved document:", retrieved_doc)
print("Generated response:", output["response"])
