import os
import json
from datetime import datetime

def generate_input_json(collection_folder, challenge_id, test_case_name, description, persona_role, job_task):
    """Auto-generates challenge1b_input.json based on PDFs present in the folder."""
    pdf_folder = os.path.join(collection_folder, "PDFs")
    os.makedirs(pdf_folder, exist_ok=True)  # ✅ Creates PDFs folder if missing

    pdf_files = sorted([f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")])
    if not pdf_files:
        print(f"⚠ No PDFs found in {pdf_folder}. You can drop them in later.")
    
    data = {
        "challenge_info": {
            "challenge_id": challenge_id,
            "test_case_name": test_case_name,
            "description": description
        },
        "documents": [{"filename": f, "title": os.path.splitext(f)[0]} for f in pdf_files],
        "persona": {
            "role": persona_role
        },
        "job_to_be_done": {
            "task": job_task
        }
    }

    json_path = os.path.join(collection_folder, "challenge1b_input.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"✅ challenge1b_input.json created at {json_path}")
    print(f"📄 PDFs detected: {pdf_files}")

# --- EDIT THIS PART FOR EACH COLLECTION ---
if __name__ == "__main__":
    generate_input_json(
        collection_folder="./Collection 1",
        challenge_id="round_1b_003",
        test_case_name="create_manageable_forms",
        description="Creating manageable forms",
        persona_role="HR professional",
        job_task="Create and manage fillable forms for onboarding and compliance."
    )
