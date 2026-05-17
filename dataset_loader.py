import os
import pandas as pd
from collections import Counter
import re

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(__file__)
CSV_PATH       = os.path.join(BASE_DIR, "data", "resume", "Resume.csv")
PDF_ROOT       = os.path.join(BASE_DIR, "data", "data")   # contains category sub-folders

# ── Stopwords for keyword extraction ───────────────────────────────────
STOPWORDS = {
    "the","and","for","with","have","this","that","from","was","are","been",
    "has","had","but","not","also","will","can","all","more","such","which",
    "they","their","other","into","about","than","over","its","any","use",
    "used","using","well","both","each","being","through","during","after",
    "before","between","under","while","where","when","would","could","should",
    "there","then","them","these","those","what","your","our","may","new",
    "one","two","three","work","worked","working","time","year","years","based",
    "include","including","various","within","across","along","ability","strong",
    "good","help","make","made","team","provide","provided","experience","skills",
    "knowledge","ability","including","responsible","worked","working","position",
    "company","business","project","projects","related","required","development",
    "management","proficient","excellent","environment","organization","service",
    "support","ensure","perform","maintain","develop","designed","implemented"
}


# ══════════════════════════════════════════════════════════════════════
#  CSV FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def load_csv():
    """Load Resume.csv — returns (DataFrame | None, error_message | None)."""
    if not os.path.exists(CSV_PATH):
        return None, f"Resume.csv not found at: {CSV_PATH}"
    try:
        df = pd.read_csv(CSV_PATH)
        return df, None
    except Exception as e:
        return None, str(e)


def get_csv_categories(df):
    """Return sorted list of unique categories from CSV."""
    if df is None or "Category" not in df.columns:
        return []
    return sorted(df["Category"].dropna().unique().tolist())


def get_csv_sample_resumes(df, category, n=3):
    """Return n sample resume text strings for a given category."""
    if df is None or "Category" not in df.columns:
        return []
    col = "Resume_str" if "Resume_str" in df.columns else df.columns[-1]
    return df[df["Category"] == category][col].dropna().head(n).tolist()


def get_top_keywords_from_csv(df, category, top_n=20):
    """Extract most frequent meaningful words from CSV resumes of a category."""
    if df is None or "Category" not in df.columns:
        return []
    col = "Resume_str" if "Resume_str" in df.columns else df.columns[-1]
    texts = df[df["Category"] == category][col].dropna()
    if texts.empty:
        return []
    all_text = " ".join(texts.tolist()).lower()
    words = re.findall(r'\b[a-z][a-z+#\.]{2,}\b', all_text)
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 3]
    return [w for w, _ in Counter(filtered).most_common(top_n)]


def get_csv_stats(df):
    """Return basic dataset statistics."""
    if df is None:
        return {}
    stats = {"total_resumes": len(df)}
    if "Category" in df.columns:
        stats["categories"] = df["Category"].value_counts().to_dict()
    return stats


# ══════════════════════════════════════════════════════════════════════
#  PDF FOLDER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def get_pdf_categories():
    """Return list of category folder names found in data/data/."""
    if not os.path.exists(PDF_ROOT):
        return []
    return sorted([
        d for d in os.listdir(PDF_ROOT)
        if os.path.isdir(os.path.join(PDF_ROOT, d))
    ])


def get_pdf_files(category):
    """Return list of PDF file paths for a given category folder."""
    folder = os.path.join(PDF_ROOT, category)
    if not os.path.exists(folder):
        return []
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(".pdf")
    ]


def count_pdfs_per_category():
    """Return dict of {category: pdf_count} for all categories."""
    cats = get_pdf_categories()
    return {cat: len(get_pdf_files(cat)) for cat in cats}


def get_top_keywords_from_pdfs(category, max_pdfs=10, top_n=20):
    """
    Extract top keywords from actual PDF resumes of a category.
    Reads up to max_pdfs files to keep it fast.
    """
    from utils.pdf_reader import extract_text_from_pdf_path

    pdf_files = get_pdf_files(category)[:max_pdfs]
    if not pdf_files:
        return []

    all_text = ""
    for path in pdf_files:
        all_text += " " + extract_text_from_pdf_path(path)

    all_text = all_text.lower()
    words = re.findall(r'\b[a-z][a-z+#\.]{2,}\b', all_text)
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 3]
    return [w for w, _ in Counter(filtered).most_common(top_n)]


def get_sample_pdf_texts(category, n=3):
    """
    Return extracted text from n sample PDFs of a category.
    Returns list of (filename, text) tuples.
    """
    from utils.pdf_reader import extract_text_from_pdf_path

    pdf_files = get_pdf_files(category)[:n]
    results = []
    for path in pdf_files:
        text = extract_text_from_pdf_path(path)
        if text:
            results.append((os.path.basename(path), text))
    return results


# ══════════════════════════════════════════════════════════════════════
#  COMBINED SMART KEYWORD SUGGESTION
# ══════════════════════════════════════════════════════════════════════

def get_smart_keywords(df, category, top_n=15):
    """
    Combine keywords from both CSV text data and PDF files.
    PDF keywords are weighted more (real documents).
    Falls back to CSV-only if PDFs not available.
    """
    pdf_kws  = get_top_keywords_from_pdfs(category, max_pdfs=8, top_n=top_n)
    csv_kws  = get_top_keywords_from_csv(df, category, top_n=top_n) if df is not None else []

    # Merge: PDFs first, then fill from CSV
    combined = list(dict.fromkeys(pdf_kws + csv_kws))
    return combined[:top_n]
