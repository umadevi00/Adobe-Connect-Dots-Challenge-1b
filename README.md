# Challenge 1B: CONNECTING THE DOTS

## Overview

This repository contains the Round 1B submission for the Adobe Hackathon 2025.
The objective is to develop a **Persona-Driven Document Intelligence** system that processes multiple collections of PDFs, extracting and ranking the most relevant sections and subsections based on a defined persona and their job-to-be-done.

The solution is designed for **offline execution** on **CPU-only environments**, fully containerized using Docker, and adheres to all challenge constraints regarding runtime, memory, and model size.

---

## Project Structure

```
Challenge_1b/
├── Collection 1/                    # Travel Planning
│   ├── PDFs/                        # PDF documents for this collection
│   ├── challenge1b_input.json       # Input configuration for this collection
│   └── (Output JSON will be generated in /app/output)
├── Collection 2/                    # Adobe Acrobat Learning
│   ├── PDFs/
│   ├── challenge1b_input.json
│   └── (Output JSON will be generated in /app/output)
├── process_pdfs.py                  # Main processing script
├── Dockerfile                       # Container configuration
├── requirements.txt                 # Python dependencies
├── approach_explanation.md          # Methodology explanation
└── README.md                        # Documentation
```

---

## Collections

### Collection 1: Travel Planning

* Challenge ID: round\_1b\_002
* Persona: Travel Planner
* Task: Plan a four-day trip for ten college friends to the South of France
* Documents: Seven travel guides

### Collection 2: Adobe Acrobat Learning

* Challenge ID: round\_1b\_003
* Persona: HR Professional
* Task: Create and manage fillable forms for onboarding and compliance
* Documents: Fifteen Acrobat learning guides

## Input Format (challenge1b\_input.json)

Each collection contains a `challenge1b_input.json` file that defines the persona, job, and document list.

```json
{
  "challenge_info": {
    "challenge_id": "round_1b_003",
    "test_case_name": "create_manageable_forms"
  },
  "documents": [
    {"filename": "Learn Acrobat - Fill and Sign.pdf", "title": "Learn Acrobat - Fill and Sign"}
  ],
  "persona": {"role": "HR professional"},
  "job_to_be_done": {"task": "Create and manage fillable forms for onboarding and compliance."}
}
```

---

## Output Format (challenge1b\_output.json)

The system generates one JSON file per collection, which includes metadata, extracted sections, and subsection analysis.

```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "HR professional",
    "job_to_be_done": "Create and manage fillable forms for onboarding and compliance.",
    "processing_timestamp": "2025-07-28T12:34:56"
  },
  "extracted_sections": [
    {
      "document": "Learn Acrobat - Fill and Sign.pdf",
      "section_title": "Change flat forms to fillable (Acrobat Pro)",
      "importance_rank": 1,
      "page_number": 12
    }
  ],
  "subsection_analysis": [
    {
      "document": "Learn Acrobat - Fill and Sign.pdf",
      "refined_text": "Relevant subsection extracted from: Change flat forms to fillable (Acrobat Pro)",
      "page_number": 12
    }
  ]
}
```

---

## Features

* Persona-driven content analysis
* Ranking of sections by relevance to the persona’s task
* Processing of multiple collections in a single run
* Clean JSON output structure matching challenge requirements
* Offline execution with CPU-only constraints

---

## Build and Run Instructions

### Build the Docker Image

```
docker build --platform linux/amd64 -t pdf-processor .
```

### Run the Container on All Collections

```
docker run --rm -v $(pwd)/challenge_1b:/app/input:ro -v $(pwd)/challenge_1b_outputs:/app/output --network none pdf-processor

```

All processed outputs will be saved in:

```
C:/Users/umadevi/challenge_1b_outputs
```

---

## Deliverables

* `process_pdfs.py` – The main script for document processing
* `Dockerfile` – Container setup for offline execution
* `requirements.txt` – All dependencies listed for reproducibility
* `approach_explanation.md` – 300–500 word explanation of the methodology
* `README.md` – Complete documentation for the solution

---

## Constraints Met

* CPU-only execution
* No internet access during runtime
* Model size under 1GB
* Processing time under 60 seconds for 3–5 PDFs
* Compatible with AMD64 architecture

---

## Test Cases

* Academic Research: Summarizing methodologies, datasets, and benchmarks for PhD-level research
* Business Analysis: Extracting revenue trends, R\&D investments, and market strategies for analysts
* Educational Content: Identifying key concepts and mechanisms for exam preparation in chemistry

