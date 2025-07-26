import fitz  # PyMuPDF
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re

nltk.download("punkt", quiet=True)
from nltk.tokenize import sent_tokenize, word_tokenize

def clean_text(text):
    """Clean text by normalizing whitespace and removing artifacts."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\.{2,}", ".", text)
    return text.strip()

def is_noise(text):
    """Identify and filter out noisy text."""
    text = text.strip()
    if not text:
        return True
    if len(text) < 20:
        return True
    if text.lower() in {"continued", "figure", "table", "contents", "abstract", "references"}:
        return True
    if re.search(r"page \d+", text.lower()):
        return True
    return False

def clean_bullets(text):
    """Remove leading bullets and extra whitespace."""
    return re.sub(r"^[•\-\*]+\s*", "", text)

def extract_sections_from_pdf(pdf_path):
    """Extract sections from PDF with clean titles and paragraphs."""
    doc = fitz.open(pdf_path)
    all_sections = []

    for page_num, page in enumerate(doc):
        blocks = sorted(page.get_text("blocks"), key=lambda b: b[1])  # sort top-to-bottom
        section_title = None
        current_paragraph = []

        for block in blocks:
            text = clean_text(block[4])
            if not text or is_noise(text):
                continue

            # Check for possible section title (short, title-case, no punctuation)
            if len(text) < 60 and text.istitle() and not re.search(r"[.:;]$", text):
                # Save previous section
                if section_title and current_paragraph:
                    full_text = " ".join(current_paragraph).strip()
                    if len(full_text) > 50:
                        all_sections.append((full_text, page_num + 1, section_title))
                # Start new section
                section_title = text
                current_paragraph = []
            else:
                current_paragraph.append(text)

        # Save last section of page
        if section_title and current_paragraph:
            full_text = " ".join(current_paragraph).strip()
            if len(full_text) > 50:
                all_sections.append((full_text, page_num + 1, section_title))

    doc.close()
    return all_sections

def rank_sentences(sections, job_description, top_n=10):
    """
    Rank sections based on semantic similarity to job description.
    Uses TF-IDF cosine similarity + deduplication.
    """
    from sklearn.metrics.pairwise import cosine_similarity

    texts = [s[0] for s in sections]
    titles = [s[2] for s in sections]
    combined = [f"{titles[i]}: {texts[i]}" for i in range(len(sections))]
    combined_with_job = combined + [job_description]

    vectorizer = TfidfVectorizer(stop_words="english", min_df=1).fit(combined_with_job)
    tfidf_matrix = vectorizer.transform(combined)
    job_vector = vectorizer.transform([job_description])

    similarities = cosine_similarity(tfidf_matrix, job_vector).ravel()
    scores = np.asarray(tfidf_matrix.sum(axis=1)).ravel() * similarities

    # Filter out irrelevant sections based on similarity threshold
    relevance_threshold = np.percentile(similarities, 50)  # Top 50%
    valid_indices = [i for i, sim in enumerate(similarities) if sim >= relevance_threshold]

    # Deduplicate based on semantic similarity
    threshold = 0.95
    unique_indices = []
    seen = []

    for idx in sorted(valid_indices, key=lambda i: scores[i], reverse=True):
        if len(unique_indices) >= top_n:
            break
        vec = tfidf_matrix[idx]
        is_duplicate = any(cosine_similarity(vec, tfidf_matrix[i])[0][0] > threshold for i in seen)
        if not is_duplicate:
            unique_indices.append(idx)
            seen.append(idx)

    ranked = [{
        "text": sections[i][0],
        "page": sections[i][1],
        "title": sections[i][2],
        "score": float(scores[i])
    } for i in unique_indices]

    return ranked