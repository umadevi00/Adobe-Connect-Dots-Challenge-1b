import fitz
import json
import os
import re
from collections import Counter
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer

# Input/Output Directories (Docker mapped)
INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def clean_text(text: str) -> str:
    """
    Normalize text by removing excessive spaces and fixing broken characters.
    Example: 'T o SEE Y ou' -> 'To SEE You'
    """
    if not text:
        return ""
    replacements = {
        '\u2013': '-', '\u2014': '--', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2022': '*', '\uf0b7': '*'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r'([A-Za-z])\s+([A-Za-z])', r'\1\2', text)  # Fix broken words
    return re.sub(r'\s+', ' ', text).strip()

def extract_lines(page, page_index):
    """
    Extract merged text lines with font attributes for heading detection.
    """
    merged_lines = []
    data = page.get_text("dict", flags=fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_SPANS)
    for block in data["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            words, sizes, bold_flags, italic_flags, y_positions = [], [], [], [], []
            for span in line["spans"]:
                txt = clean_text(span["text"])
                if txt:
                    words.append(txt)
                    sizes.append(span["size"])
                    bold_flags.append(any(x in span["font"].lower() for x in ["bold", "black", "heavy", "demi"]))
                    italic_flags.append("italic" in span["font"].lower())
                    y_positions.append(span["origin"][1])
            if words:
                merged_lines.append({
                    "text": " ".join(words),
                    "size": sum(sizes) / len(sizes),
                    "is_bold": any(bold_flags),
                    "is_italic": any(italic_flags),
                    "y": sum(y_positions) / len(y_positions),
                    "page": page_index
                })
    return merged_lines

def classify_heading(line, h1_size, h2_size, h3_size, max_font_size):
    """
    Decide if a line qualifies as a heading and assign H1/H2/H3.
    """
    text = line["text"]

    # Skip junk or very short text unless it's the largest font
    if len(text) < 3 and line["size"] < max_font_size:
        return None
    if re.match(r"^Page\s+\d+", text, re.IGNORECASE):
        return None

    # All caps are strong H1 candidates
    if text.isupper() and len(text) > 3 and line["size"] >= h2_size:
        return "H1"

    # Numbered heading detection (e.g., 1. Introduction)
    if re.match(r"^\d+(\.\d+)*\s+.+", text):
        dots = text.count(".")
        if dots == 0 and line["size"] >= h1_size * 0.9:
            return "H1"
        elif dots == 1 and line["size"] >= h2_size * 0.8:
            return "H2"
        elif dots >= 2 and line["size"] >= h3_size * 0.8:
            return "H3"

    # Bold/Italic rule
    if line["is_bold"] or line["is_italic"]:
        if line["size"] >= h1_size:
            return "H1"
        elif line["size"] >= h2_size:
            return "H2"
        elif line["size"] >= h3_size:
            return "H3"

    return None

def extract_headings(doc):
    """
    Extract all potential headings and clean duplicates.
    """
    all_lines = []
    repeat_tracker = Counter()

    for p in range(doc.page_count):
        lines = extract_lines(doc.load_page(p), p)
        for l in lines:
            all_lines.append(l)
            repeat_tracker[l["text"]] += 1

    body_sizes = [l["size"] for l in all_lines if len(l["text"]) > 4]
    base_font = Counter(body_sizes).most_common(1)[0][0] if body_sizes else 10
    max_font = max((l["size"] for l in all_lines), default=base_font)

    # Thresholds for heading classification
    h1_size = max(max_font * 0.65, base_font * 1.6)
    h2_size = max(max_font * 0.5, base_font * 1.3)
    h3_size = max(max_font * 0.3, base_font * 1.1)

    outline_temp = []
    seen_texts = set()

    for line in all_lines:
        txt = line["text"]

        # Filter duplicate fragments (e.g., quest f, quest fo)
        if any(txt in seen for seen in seen_texts if len(txt) < len(seen)):
            continue
        seen_texts.add(txt)

        level = classify_heading(line, h1_size, h2_size, h3_size, max_font)
        if level:
            outline_temp.append((line["page"], line["y"], {
                "level": level,
                "text": txt,
                "page": line["page"]
            }))

    # Sort by page then vertical position
    outline_temp.sort(key=lambda x: (x[0], x[1]))

    # Deduplicate exact same heading on same page
    final_outline = []
    seen_keys = set()
    for _, _, heading in outline_temp:
        key = (heading["text"], heading["page"])
        if key not in seen_keys:
            final_outline.append(heading)
            seen_keys.add(key)

    return final_outline

def rank_sections_by_relevance(headings, persona_text):
    """
    Rank headings by relevance to persona/job text using TF-IDF similarity.
    """
    if not headings:
        return []
    texts = [h["text"] for h in headings]
    tfidf = TfidfVectorizer(stop_words="english")
    matrix = tfidf.fit_transform([persona_text] + texts)
    scores = matrix[0, 1:].toarray().flatten()

    ranked = sorted(
        zip(headings, scores),
        key=lambda x: x[1],
        reverse=True
    )
    return ranked

def process_collection(collection_path):
    """
    Process a single collection folder: read input JSON, analyze PDFs, write output JSON.
    """
    input_json_path = os.path.join(collection_path, "challenge1b_input.json")
    if not os.path.exists(input_json_path):
        print(f"Skipping {collection_path}: No challenge1b_input.json")
        return

    with open(input_json_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    persona_text = f"{config['persona']['role']} {config['job_to_be_done']['task']}"

    all_headings = []

    for doc_info in config["documents"]:
        pdf_path = os.path.join(collection_path, "PDFs", doc_info["filename"])
        if not os.path.exists(pdf_path):
            print(f"Missing PDF: {pdf_path}")
            continue

        doc = fitz.open(pdf_path)
        headings = extract_headings(doc)
        doc.close()

        for h in headings:
            h["document"] = doc_info["filename"]
            all_headings.append(h)

    ranked_headings = rank_sections_by_relevance(all_headings, persona_text)

    # Build output JSON
    output = {
        "metadata": {
            "input_documents": [d["filename"] for d in config["documents"]],
            "persona": config["persona"]["role"],
            "job_to_be_done": config["job_to_be_done"]["task"],
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    # Top 5 relevant sections
    for rank, (h, score) in enumerate(ranked_headings[:5], start=1):
        output["extracted_sections"].append({
            "document": h["document"],
            "section_title": h["text"],
            "importance_rank": rank,
            "page_number": h["page"]
        })

    # Subsection placeholder analysis (can be enhanced)
    for item in output["extracted_sections"]:
        output["subsection_analysis"].append({
            "document": item["document"],
            "refined_text": f"Relevant subsection extracted from: {item['section_title']}",
            "page_number": item["page_number"]
        })

    # Write output to OUTPUT_DIR (not the read-only input dir)
    collection_name = os.path.basename(collection_path)
    output_path = os.path.join(OUTPUT_DIR, f"{collection_name}_output.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print(f"Processed {collection_name} → {collection_name}_output.json")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    collections = [d for d in os.listdir(INPUT_DIR) if d.startswith("Collection")]

    if not collections:
        print("No Collection folders found.")
        return

    for c in collections:
        process_collection(os.path.join(INPUT_DIR, c))

if __name__ == "__main__":
    main()
