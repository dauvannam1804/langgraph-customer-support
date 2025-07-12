import re
import requests
import numpy as np
import json
from langchain_core.tools import tool

# Tải nội dung FAQ
response = requests.get(
    "https://storage.googleapis.com/benchmarks-artifacts/travel-db/swiss_faq.md"
)
response.raise_for_status()
faq_text = response.text

docs = [{"page_content": txt} for txt in re.split(r"(?=\n##)", faq_text)]

# ===========================
# Sử dụng Ollama để embedding
# ===========================

def ollama_embed(texts: list[str], model: str = "nomic-embed-text") -> list[list[float]]:
    embeddings = []
    for text in texts:
        payload = {
            "model": model,
            "prompt": text
        }
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        response.raise_for_status()
        result = response.json()
        embeddings.append(result["embedding"])
    return embeddings


class VectorStoreRetriever:
    def __init__(self, docs: list, vectors: list):
        self._arr = np.array(vectors)
        self._docs = docs

    @classmethod
    def from_docs(cls, docs):
        texts = [doc["page_content"] for doc in docs]
        vectors = ollama_embed(texts)  # dùng embedding từ Ollama
        return cls(docs, vectors)

    def query(self, query: str, k: int = 5) -> list[dict]:
        query_vector = ollama_embed([query])[0]
        scores = np.array(query_vector) @ self._arr.T
        top_k_idx = np.argpartition(scores, -k)[-k:]
        top_k_idx_sorted = top_k_idx[np.argsort(-scores[top_k_idx])]
        return [
            {**self._docs[idx], "similarity": scores[idx]} for idx in top_k_idx_sorted
        ]


retriever = VectorStoreRetriever.from_docs(docs)


@tool
def lookup_policy(query: str) -> str:
    """Consult the company policies to check whether certain options are permitted.
    Use this before making any flight changes performing other 'write' events."""
    docs = retriever.query(query, k=2)
    return "\n\n".join([doc["page_content"] for doc in docs])

if __name__ == "__main__":
    retriever = VectorStoreRetriever.from_docs(docs)

    query = "How can I change my booking?"
    results = retriever.query(query, k=2)

    print("docs:", docs[0]['page_content'])
    print("query:", query)

    for i, doc in enumerate(results, 1):
        print(f"\n--- Top {i} (Score: {doc['similarity']:.3f}) ---\n")
        print(doc["page_content"])