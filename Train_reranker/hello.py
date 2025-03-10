import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, logging


# Load model and tokenizer
model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # Changed model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Example query and candidates
query = "나는 방금 밥을 먹었다."
candidates = [
    "나는 내일 밥을 먹었다.",
    "나는 어제 밥을 먹었다.",
    "나는 지금 밥을 먹고 있다."
]

# Encode and score each candidate
scores = []
for candidate in candidates:
    inputs = tokenizer.encode_plus(query, candidate, return_tensors="pt", truncation=True, padding=True)  # Added truncation and padding
    outputs = model(**inputs)
    score = outputs.logits.softmax(dim=1)[0][1].item()  # Assuming binary classification
    scores.append((candidate, score))

# Sort candidates by score
ranked_candidates = sorted(scores, key=lambda x: x[1], reverse=True)

# Print ranked candidates
for candidate, score in ranked_candidates:
    print(f"Candidate: {candidate}, Score: {score}")