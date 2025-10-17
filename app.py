import streamlit as st
import PyPDF2
import base64
import requests

API_URL_SIM = "http://127.0.0.1:8000/similarity"
API_URL_SUM = "http://127.0.0.1:8000/summary"

# Weights
WEIGHT_JD = 0.7
WEIGHT_CV = 0.3

# --- Page styling ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {

}
[data-testid="stAppViewContainer"] h1 {
    color: blue !important;
    text-align: center;
}
 [data-testid="stAppViewContainer"] .resume-card {
    background-color:white;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 12px;
    box-shadow: 0px 3px 8px rgba(0,0,0,0.15);
}
.score {
    color: #ff6600;
    font-weight: bold;
}
.summary-text {
    background-color:green;
    padding: 12px;
    border-radius: 8px;
}
button {
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>📄 Smart Resume Ranker with PDF Preview & AI Summary</h1>", unsafe_allow_html=True)

# --- PDF text extraction ---
def extract_text(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    file.seek(0)
    return text

# --- PDF preview ---
def open_pdf(file):
    pdf_bytes = file.read()
    b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    js = f"""
    <script>
        var pdfWindow = window.open("");
        pdfWindow.document.write(
            '<iframe width="100%" height="100%" src="data:application/pdf;base64,{b64_pdf}"></iframe>'
        );
    </script>
    """
    st.components.v1.html(js, height=400)
    file.seek(0)

# --- Generate summary via backend ---
def generate_summary(text):
    try:
        response = requests.post(API_URL_SUM, json={"text": text})
        if response.status_code == 200:
            return response.json()["summary"]
        else:
            return f"⚠️ Error generating summary: {response.text}"
    except Exception as e:
        return f"⚠️ Error: {e}"

# --- Upload resumes & JD ---
uploaded_files = st.file_uploader("Upload resumes (PDF)", type=["pdf"], accept_multiple_files=True)
job_description = st.text_area("Paste Job Description")

if uploaded_files and job_description.strip():
    resumes = []
    for file in uploaded_files:
        text = extract_text(file)
        if not text.strip():
            st.warning(f"{file.name} is empty. Skipping.")
            continue
        # JD similarity
        response = requests.post(API_URL_SIM, json={"text1": job_description, "text2": text})
        jd_score = response.json()["similarity"] if response.status_code == 200 else 0
        resumes.append({"name": file.name, "file": file, "text": text, "jd_score": jd_score, "cv_score": 0})

    # CV-to-CV similarity
    for i, r1 in enumerate(resumes):
        cv_scores = []
        for j, r2 in enumerate(resumes):
            if i == j:
                continue
            response = requests.post(API_URL_SIM, json={"text1": r1["text"], "text2": r2["text"]})
            if response.status_code == 200:
                cv_scores.append(response.json()["similarity"])
        r1["cv_score"] = sum(cv_scores)/len(cv_scores) if cv_scores else 0

    # Final weighted score
    for r in resumes:
        r["final_score"] = WEIGHT_JD * r["jd_score"] + WEIGHT_CV * r["cv_score"]

    # Sort by final_score
    resumes.sort(key=lambda x: x["final_score"], reverse=True)

    st.subheader("🏆 Final Ranking")
    
    for i, r in enumerate(resumes, 1):
        st.markdown(f"<div class='resume-card'>", unsafe_allow_html=True)
        st.markdown(
            f"**{i}. {r['name']}** — Final Score: <span class='score'>{r['final_score']:.4f}</span> ",
            unsafe_allow_html=True
        )
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button(f"👁 Preview", key=f"preview_{i}"):
                open_pdf(r["file"])
        with col2:
            if st.button(f"📝 Generate Summary", key=f"summary_{i}"):
                with st.spinner("Generating summary..."):
                    summary = generate_summary(r["text"])
                    st.markdown(f"<div class='summary-text'>{summary}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif uploaded_files and not job_description.strip():
    st.info("✍️ Please enter a job description to rank the resumes.")
else:
    st.info("📂 Upload resumes to start ranking.")
