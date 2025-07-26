import os
import json
from datetime import datetime
from utils import extract_sections_from_pdf, rank_sentences
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

INPUT_DIR = "input" if os.path.exists("input") else "/app/input"
OUTPUT_DIR = "output" if os.path.exists("output") else "/app/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_input_config(input_path="input.json"):
    """Load configuration from input.json."""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        persona = config.get("persona", {}).get("role", "General Researcher")
        job = config.get("job_to_be_done", {}).get("task", "Summarize key insights from documents")
        documents = [doc["filename"] for doc in config.get("documents", [])]
        return persona, job, documents
    except FileNotFoundError:
        raise FileNotFoundError(f"{input_path} not found")

def semantic_filter(refined_texts, job_description, threshold=0.25, fallback_top_n=5):
    """Filter sections semantically based on job description alone."""
    if not refined_texts:
        return []

    all_texts = [t['refined_text'] for t in refined_texts] + [job_description]
    vectorizer = TfidfVectorizer(stop_words="english", min_df=1).fit(all_texts)
    matrix = vectorizer.transform(all_texts)
    job_vector = matrix[-1]
    doc_vectors = matrix[:-1]

    similarities = cosine_similarity(doc_vectors, job_vector).ravel()

    enriched = [
        refined_texts[i] | {"_similarity": similarities[i]}
        for i in range(len(similarities))
    ]

    # Keep top N most relevant semantically
    sorted_by_similarity = sorted(enriched, key=lambda x: x["_similarity"], reverse=True)
    top_filtered = [x for x in sorted_by_similarity if x["_similarity"] >= threshold]

    return (top_filtered or sorted_by_similarity[:fallback_top_n])[:fallback_top_n]

def analyze_all_pdfs(input_path="input.json"):
    # Load persona, job, and document list from input.json
    persona, job, input_files = load_input_config(input_path)

    # Verify that all specified files exist in INPUT_DIR
    missing_files = [f for f in input_files if not os.path.exists(os.path.join(INPUT_DIR, f))]
    if missing_files:
        raise ValueError(f"Missing PDF files: {missing_files}")

    all_sections = []
    timestamp = datetime.now().isoformat()

    # Extract sections from specified PDFs
    for file in input_files:
        path = os.path.join(INPUT_DIR, file)
        sections = extract_sections_from_pdf(path)
        all_sections.extend([(file, s[0], s[1], s[2]) for s in sections])

    if not all_sections:
        raise ValueError("No valid sections extracted from documents")

    # Rank sections based on job_to_be_done
    ranked = rank_sentences([(s[1], s[2], s[3]) for s in all_sections], job, top_n=10)

    # Build refined_text items
    raw_refined = []
    for item in ranked:
        filename = next(f for f, text, page, title in all_sections if text == item["text"])
        raw_refined.append({
            "document": filename,
            "refined_text": item["text"],
            "page_number": item["page"],
            "title": item["title"],
            "score": item["score"]
        })

    # Apply semantic filter to remove off-topic refined_texts, with fallback
    final_refined = semantic_filter(raw_refined, job)

    extracted_sections = []
    subsection_analysis = []

    for i, item in enumerate(final_refined, 1):
        extracted_sections.append({
            "document": item["document"],
            "page_number": item["page_number"],
            "section_title": item["title"],
            "importance_rank": i
        })
        subsection_analysis.append({
            "document": item["document"],
            "refined_text": item["refined_text"],
            "page_number": item["page_number"]
        })

    result = {
        "metadata": {
            "input_documents": input_files,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": timestamp
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    output_path = os.path.join(OUTPUT_DIR, "analysis.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    analyze_all_pdfs()