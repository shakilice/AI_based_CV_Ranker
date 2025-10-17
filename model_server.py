from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from typing import List

app = FastAPI()

# Allow Streamlit to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load embedding model once
print("🔄 Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Embedding model loaded")

# Load summarization model once
print("🔄 Loading summarization model...")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
print("✅ Summarization model loaded")

# --- Similarity endpoint ---
class EmbedRequest(BaseModel):
    text1: str
    text2: str

@app.post("/similarity")
def get_similarity(data: EmbedRequest):
    emb1 = model.encode(data.text1, convert_to_tensor=True)
    emb2 = model.encode(data.text2, convert_to_tensor=True)
    score = util.cos_sim(emb1, emb2).item()
    return {"similarity": score}

# --- Summary endpoint ---
class SummaryRequest(BaseModel):
    text: str

def chunk_text(text: str, max_chars: int = 2000) -> List[str]:
    """Split text into chunks of ~max_chars, split at newline if possible."""
    chunks = []
    while len(text) > max_chars:
        split_pos = text[:max_chars].rfind("\n")
        if split_pos == -1:
            split_pos = max_chars
        chunks.append(text[:split_pos])
        text = text[split_pos:]
    if text.strip():
        chunks.append(text)
    return chunks

@app.post("/summary")
def generate_summary(data: SummaryRequest):
    text = data.text
    try:
        chunks = chunk_text(text, max_chars=2000)
        summary_chunks = []

        for chunk in chunks:
            summary_chunk = summarizer(
                chunk,
                max_length=300,
                min_length=40,
                do_sample=True,    # enable randomness
                top_k=50,
                top_p=0.95,
                temperature=0.7
            )[0]["summary_text"]
            summary_chunks.append(summary_chunk)

        final_summary = " ".join(summary_chunks)
        return {"summary": final_summary}

    except Exception as e:
        return {"error": str(e)}
