# Approach Explanation – Challenge 1B

## 1. Problem Understanding

The objective of Challenge 1B is to build an offline, CPU‑only intelligent document analyst that identifies and prioritizes relevant sections from multiple PDF documents based on:

* Persona – the user’s role, expertise, and focus areas
* Job to be done – the specific task the persona needs to accomplish

The system must be domain‑agnostic and work with research papers, financial reports, textbooks, and more. It must also meet strict runtime and size constraints, producing structured JSON outputs that conform to the required schema.

---

## 2. Solution Overview

### Step 1 – Input Handling

* Each collection folder (Collection 1, Collection 2, etc.) contains:

  * PDFs – the source documents
  * challenge1b\_input.json – defines persona, job to be done, and document list
* The script loops through each collection, processes all PDFs, and writes a matching challenge1b\_output.json to the output directory.

### Step 2 – PDF Parsing

* Uses PyMuPDF (fitz) for fast, lightweight PDF parsing.
* Extracts:

  * Text spans and merges them into clean lines
  * Font attributes (size, bold, italic) and positional data

This information is critical for determining document structure and identifying headings.

### Step 3 – Heading Detection

* Headings (H1, H2, H3) are identified using relative font size and style rules:

  * H1: Largest text or all‑caps titles (main sections)
  * H2: Medium text or bold/italic sub‑sections
  * H3: Slightly smaller styled text (minor sections)

Duplicate fragments and junk lines (such as page numbers) are removed.

### Step 4 – Persona Aware Ranking

* Combines persona and job description into a single query text.
* Uses TF‑IDF vectorization (scikit‑learn) to compute similarity between:

  * Persona/job text (query)
  * Extracted headings (candidates)

Headings are scored and sorted by their relevance to the persona’s task.

### Step 5 – Section and Sub‑Section Output

* The top five most relevant sections are selected.
* Each section is labeled with:

  * Document name
  * Section title
  * Page number
  * Importance rank

For each section, a sub‑section analysis placeholder is generated, summarizing or contextualizing the heading. This is lightweight and can be extended later for deeper analysis.

### Step 6 – JSON Generation

* Writes one output JSON per collection that includes:

  * Metadata: persona, job to be done, input documents, processing timestamp
  * Extracted sections: top ranked sections with importance ranking
  * Sub‑section analysis: refined excerpts tied to those sections

---

## 3. Why This Approach Works

* Generic and domain‑independent – Works on research papers, financial reports, academic chapters, and HR documents without hardcoded rules.
* Offline and lightweight – Uses PyMuPDF and TF‑IDF, no internet access, no external APIs, and model size stays well below one gigabyte.
* Efficient – Processes three to ten PDFs in under sixty seconds by parsing in one pass and using vectorization instead of heavy deep learning.
* Extensible – Can easily incorporate semantic models or deeper NLP modules later.

---

## 4. Processing Workflow

1. Scan collections to identify each “Collection X” folder.
2. Load input JSON to read persona, job, and document list.
3. Parse PDFs to extract text spans and clean lines.
4. Detect headings and assign H1, H2, H3 levels.
5. Rank by relevance using TF‑IDF against persona and job text.
6. Select top five sections for output.
7. Generate sub‑section summaries.
8. Write JSON output for each collection.

---

## 5. Constraints and Compliance

* Runs on CPU only, no GPU dependency.
* Model size under one gigabyte.
* Processing time under sixty seconds for a set of up to ten PDFs.
* Works fully offline with no internet calls.
* Dockerized for clean, reproducible execution.

---

## 6. Future Enhancements

* Add small semantic ranking models for richer relevance scoring.
* Generate full contextual summaries instead of placeholders.
* Expand support for multi‑lingual documents.

---

## Conclusion

This solution connects the right content to the right persona by intelligently extracting, ranking, and presenting the most relevant sections from large PDF collections. It is fully compliant with the Adobe Hackathon’s technical requirements and ready for real‑world testing across diverse document domains.
