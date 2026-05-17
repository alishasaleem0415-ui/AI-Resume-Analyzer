import nltk

for pkg, path in [('punkt','tokenizers/punkt'), ('stopwords','corpora/stopwords'), ('punkt_tab','tokenizers/punkt_tab')]:
    try:
        nltk.data.find(path)
    except LookupError:
        nltk.download(pkg, quiet=True)

SKILL_CATEGORIES = {
    "Programming Languages": [
        "python", "java", "c++", "javascript", "r", "sql", "scala",
        "matlab", "typescript", "go", "ruby", "php"
    ],
    "AI / ML Skills": [
        "machine learning", "deep learning", "neural network", "nlp",
        "natural language processing", "computer vision", "reinforcement learning",
        "transfer learning", "model deployment", "data science", "generative ai"
    ],
    "Frameworks & Libraries": [
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas",
        "numpy", "opencv", "hugging face", "transformers", "langchain",
        "streamlit", "flask", "fastapi", "django", "spark", "hadoop"
    ],
    "Data & Cloud Tools": [
        "mysql", "mongodb", "firebase", "aws", "azure", "google cloud",
        "docker", "kubernetes", "git", "github", "tableau", "power bi",
        "excel", "postgresql"
    ],
    "Soft Skills": [
        "communication", "teamwork", "leadership", "problem solving",
        "critical thinking", "time management", "adaptability",
        "collaboration", "presentation", "research"
    ]
}


def analyze_resume(text):
    text_lower = text.lower()
    found, missing = {}, {}
    for category, skills in SKILL_CATEGORIES.items():
        f = [s for s in skills if s in text_lower]
        m = [s for s in skills if s not in text_lower]
        if f: found[category] = f
        if m: missing[category] = m
    return found, missing


def get_resume_tips(score, missing_keywords):
    tips = []
    if score < 40:
        tips.append("🔴 Your resume needs significant improvement to pass ATS filters.")
        tips.append("📝 Rewrite your resume to include more keywords from the job description.")
    elif score < 70:
        tips.append("🟡 Partial match — a few more targeted keywords will push you over 70%.")
        tips.append("✏️ Add missing keywords naturally in your experience or skills section.")
    else:
        tips.append("🟢 Great match! Your resume is well-aligned with the job description.")
        tips.append("🚀 Quantify achievements (e.g. 'Improved model accuracy by 20%').")

    if missing_keywords:
        tips.append(f"🔑 Priority keywords to add: {', '.join(missing_keywords[:5])}")

    tips.append("📄 Keep your resume to 1–2 pages maximum.")
    tips.append("🔠 Use an ATS-friendly font — Arial or Calibri work best.")
    tips.append("📌 Avoid tables and graphics — they confuse ATS parsers.")
    tips.append("🔢 Quantify results wherever possible — numbers stand out.")
    return tips
