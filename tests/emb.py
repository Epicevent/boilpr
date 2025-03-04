import ollama
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

# Create a persistent Chroma client that stores data in the local "chroma_db" folder.
client = chromadb.PersistentClient(
    path="chroma_db",
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)

# Create a collection named "docs"
collection = client.create_collection(name="docs")

# Example documents to store
documents = [
    "오늘은 날씨가 참 좋아서 외출하기에 아주 좋은 날이에요.",
    "책을 읽는 것은 마음을 편안하게 해주고 지식을 넓혀줍니다.",
    "나는 미래에 대한 두려움을 가지지 않고 미래를 기대하며 살고 있습니다.",
    "요리를 하며 시간을 보내는 것은 나에게 큰 즐거움을 줍니다."
]

# Process each document: generate an embedding and add it to the collection.
for i, d in enumerate(documents):
    response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
    embedding = response["embedding"]
    collection.add(
        ids=[str(i)],
        embeddings=[embedding],
        documents=[d]
    )

print("Persistent Vector DB created and stored in the 'chroma_db' folder.")
