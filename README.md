# 📄 Smart Resume Ranker with AI Summary & PDF Preview

An intelligent web app that automatically ranks resumes based on a given Job Description (JD) using semantic similarity and provides AI-generated summaries for each resume.  
Built with Streamlit (frontend) and FastAPI (backend).

---

## 🚀 Features

✅ Upload multiple resumes (PDF)  
✅ Paste or type a Job Description  
✅ AI-based similarity scoring between JD and resumes using Sentence Transformers  
✅ Resume-to-Resume similarity (to balance candidate uniqueness and relevance)  
✅ Weighted ranking system  
✅ Interactive PDF preview directly in the browser  
✅ AI-powered text summarization for each resume using HuggingFace transformers  
✅ Beautiful Streamlit interface with custom styling  

---

## 🧠 Tech Stack

| Component | Technology |
|------------|-------------|
| Frontend | Streamlit |
| Backend API | FastAPI |
| AI Models | SentenceTransformer (all-MiniLM-L6-v2) and DistilBART (sshleifer/distilbart-cnn-12-6) |
| NLP Libraries | sentence-transformers, transformers |
| PDF Extraction | PyPDF2 |
| Communication | REST API (via requests) |
| Styling | Custom CSS in Streamlit |

---

## 📦 Project Structure

