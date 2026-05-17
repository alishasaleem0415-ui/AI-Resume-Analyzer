# 📄 AI Resume Analyzer — Full Dataset Edition

> A powerful AI-driven resume analyzer that uses **2,400+ real resumes** from Kaggle — both CSV text data and actual PDF files — to give smart keyword suggestions, ATS scoring, and skills gap analysis.

**Built by Alisha Saleem | BS Artificial Intelligence | UMT Lahore**

---

## 🎯 Features

| Feature | Description |
|--------|-------------|
| 🔍 ATS Score | Match your resume against job description keywords |
| 💡 Smart Keywords | Auto-extracted from real PDF resumes by job category |
| 📊 Dataset Overview | Charts showing resume distribution across categories |
| 📚 PDF Resume Browser | Read actual PDF resumes extracted from the dataset |
| 📝 CSV Explorer | Browse and filter the full text resume dataset |
| 🚀 Skills Gap Analysis | Find missing technical & soft skills |
| 📝 Personalized Tips | Actionable improvement advice |

---

## 📦 Dataset Setup

Download from Kaggle:
👉 https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset

After extracting, your folder should look like this:

```
AI-Resume-Analyzer/
└── data/
    ├── resume/
    │   └── Resume.csv          ← from the 'resume' folder
    └── data/
        ├── ENGINEERING/
        │   ├── 12345678.pdf
        │   └── ...
        ├── MEDICAL/
        ├── ACCOUNTING/
        └── ...                 ← all category folders go here
```

---

## 🚀 Quick Start (Windows)

```bash
# Option 1 — Double click setup.bat then run.bat

# Option 2 — Manual
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## 🛠️ Tech Stack

- **Python** — Core language
- **Streamlit** — Web UI
- **PyMuPDF** — PDF text extraction (both uploads & dataset)
- **NLTK** — Natural language processing
- **Pandas** — CSV data handling
- **Kaggle Dataset** — 2,400+ real resume PDFs + CSV

---

## 📁 Project Structure

```
AI-Resume-Analyzer/
├── app.py                  ← Main app (4 tabs)
├── analyzer.py             ← Skills analysis & tips
├── dataset_loader.py       ← CSV + PDF dataset integration
├── requirements.txt
├── README.md
├── setup.bat               ← Windows auto-setup
├── run.bat                 ← Windows quick launch
├── utils/
│   ├── pdf_reader.py       ← PDF extraction (upload + disk)
│   └── scorer.py           ← ATS keyword scoring
└── data/
    ├── resume/             ← Place Resume.csv here
    └── data/               ← Place category folders here
```

---

## 🌐 Deploy Free on Streamlit Cloud

1. Push code to GitHub (dataset files are gitignored — too large)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → set `app.py` as main file
4. Deploy ✅

> Note: For cloud deployment, the app works without the dataset (graceful fallback).

---

## 🤝 Connect

- 💼 [LinkedIn](https://linkedin.com/in/YOUR-PROFILE)
- 🐙 [GitHub](https://github.com/YOUR-USERNAME)

---

## 📜 License

MIT License
