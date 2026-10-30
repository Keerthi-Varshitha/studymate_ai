
from sentence_transformers import SentenceTransformer
import numpy as np
import requests

# Load the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve_relevant_chunks(question, document_chunks, top_k=4):
    if not document_chunks:
        return []

    texts = [item["text"] for item in document_chunks]

    document_embeddings = embedding_model.encode(
        texts,
        normalize_embeddings=True
    )

    question_embedding = embedding_model.encode(
        [question],
        normalize_embeddings=True
    )

    similarities = np.dot(
        document_embeddings,
        question_embedding[0]
    )

    best_indices = np.argsort(similarities)[::-1][:top_k]

    results = []

    for index in best_indices:
        results.append({
            "text": texts[index],
            "source": document_chunks[index]["source"],
            "score": float(similarities[index])
        })

    return results


def generate_answer(question, relevant_chunks):
    if not relevant_chunks:
        return "No relevant information was found in your uploaded documents."

    context = "\n\n".join(
        f"Source: {item['source']}\n{item['text']}"
        for item in relevant_chunks
    )

    prompt = f"""
You are StudyMate AI, a helpful study assistant.

Answer the user's question using only the provided document context.
If the answer is not available in the context, clearly say that
the uploaded documents do not contain the answer.
Do not invent information.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}
"""

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["message"]["content"]


def answer_question(question, document_chunks):
    relevant_chunks = retrieve_relevant_chunks(
        question,
        document_chunks
    )

    answer = generate_answer(question, relevant_chunks)

    sources = list(dict.fromkeys(
        item["source"] for item in relevant_chunks
    ))

    return {
        "answer": answer,
        "sources": sources
    }
