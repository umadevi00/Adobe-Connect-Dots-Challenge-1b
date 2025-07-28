import fitz  # PyMuPDF
import json
import os
import re
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

INPUT_JSON = "/app/input/challenge1b_input.json"
OUTPUT_JSON = "/app/output/challenge1b_output.json"
PDF_FOLDER = "/app/input/PDFs"

def clean_text(text):
    """Basic cleanup for extracted PDF text."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_sections_from_pdf(pdf_path):
    """
    Extracts text chunks per page to simulate sections.
    (Real systems might use ML/heading detection here)
    """
    sections = []
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")  # returns (x0, y0, x1, y1, text, block_no, block_type)
        for b in blocks:
            txt = clean_text(b[4])
            if txt and len(txt.split()) > 3:  # ignore junk
                sections.append({
                    "page": page_num,
                    "text": txt[:2000],  # truncate very long sections for relevance scoring
                })
    return sections

def score_sections(sections, query):
    """
    Uses TF-IDF cosine similarity to score relevance of sections to the persona+job query.
    """
    corpus = [s["text"] for s in sections]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform([query] + corpus)
    scores = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
    for idx, score in enumerate(scores):
        sections[idx]["score"] = float(score)
    return sorted(sections, key=lambda x: x["score"], reverse=True)

def process_all_pdfs(input_data):
    persona = input_data["persona"]["role"]
    job = input_data["job_to_be_done"]["task"]
    query = f"{persona} needs to {job}"

    all_sections = []
    for doc in input_data["documents"]:
        pdf_path = os.path.join(PDF_FOLDER, doc["filename"])
        if not os.path.exists(pdf_path):
            print(f"⚠ Missing PDF: {pdf_path}")
            continue
        sections = extract_sections_from_pdf(pdf_path)
        for s in sections:
            s["document"] = doc["filename"]
        all_sections.extend(sections)

    # Rank all extracted sections
    ranked_sections = score_sections(all_sections, query)

    # Top 5 “sections”
    extracted_sections = []
    for idx, sec in enumerate(ranked_sections[:5], 1):
        extracted_sections.append({
            "document": sec["document"],
            "section_title": sec["text"][:80] + ("..." if len(sec["text"]) > 80 else ""),
            "importance_rank": idx,
            "page_number": sec["page"]
        })

    # Take sub-sections (best 5 chunks of text)
    subsection_analysis = []
    for sec in ranked_sections[:5]:
        refined_texts = sec["text"].split(". ")[:2]  # take 2 sentences for brevity
        for rt in refined_texts:
            if len(rt.strip()) > 10:
                subsection_analysis.append({
                    "document": sec["document"],
                    "refined_text": rt.strip(),
                    "page_number": sec["page"]
                })

    return extracted_sections, subsection_analysis

def main():
    if not os.path.exists(INPUT_JSON):
        print(f"❌ {INPUT_JSON} not found")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    extracted_sections, subsection_analysis = process_all_pdfs(input_data)

    output = {
        "metadata": {
            "input_documents": [doc["filename"] for doc in input_data["documents"]],
            "persona": input_data["persona"]["role"],
            "job_to_be_done": input_data["job_to_be_done"]["task"],
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    os.makedirs("/app/output", exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print(f"✅ Output written to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
