import ollama
import PyPDF2

# ---- STEP 1: Read text from the PDF CV ----
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text.strip()

# ---- STEP 2: Create prompt to extract information ----
def generate_extraction_prompt(cv_text):
    return f"""
From the following resume, extract the following information clearly and concisely:
- Skills
- Experience
- Qualifications
- Job Responsibilities

Format the output with clear section headings and bullet points.

Resume:
{cv_text}
"""

# ---- STEP 3: Call Ollama to get structured info ----
def extract_info_from_cv(cv_text):
    prompt = generate_extraction_prompt(cv_text)
    response = ollama.chat(model='gemma2:2b', messages=[
        {"role": "system", "content": "You are a professional HR assistant."},
        {"role": "user", "content": prompt}
    ])
    return response['message']['content'].strip()

# ---- STEP 4: Run everything together ----
def main():
    pdf_path = input("📄 Enter path to the CV PDF: ").strip()
    
    print("📤 Reading and processing the CV...")
    cv_text = extract_text_from_pdf(pdf_path)
    
    print("🤖 Sending to Gemma 2:2b for extraction...")
    extracted_info = extract_info_from_cv(cv_text)

    print("\n✅ Extracted Information:\n")
    print(extracted_info)

    # Optionally save to a text file
    with open("cv_extracted_info.txt", "w", encoding="utf-8") as f:
        f.write(extracted_info)
    print("\n💾 Output saved to 'cv_extracted_info.txt'")

if __name__ == "__main__":
    main()
