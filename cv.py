import ollama
import PyPDF2

# ----- List of Predefined Job Roles -----
job_roles = [
    "Software Engineer", "Data Scientist", "Product Manager", "Cloud Engineer",
    "Cybersecurity Analyst", "Machine Learning Engineer", "DevOps Engineer",
    "Full Stack Developer", "Big Data Engineer", "AI Researcher", "Database Administrator",
    "Network Engineer", "Software Architect", "Blockchain Developer", "IT Project Manager",
    "Business Intelligence Analyst", "Robotics Engineer", "Embedded Systems Engineer",
    "Quality Assurance Engineer", "UX/UI Designer"
]

# ----- Read Text from PDF -----
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

# ----- Prompt for Extraction -----
def generate_prompt(cv_text):
    return f"""
You are an AI recruiter assistant.

From the following resume, extract:
- Skills
- Experience
- Qualifications
- Job Responsibilities

Then based on the content, predict the most appropriate job role the candidate is likely applying for from the following list:

{', '.join(job_roles)}

Format output clearly with section headers and bullet points.

Resume:
{cv_text}
"""

# ----- Get Info from Ollama -----
def analyze_cv(cv_text):
    prompt = generate_prompt(cv_text)
    response = ollama.chat(model='gemma2:2b', messages=[
        {"role": "system", "content": "You are a professional HR assistant."},
        {"role": "user", "content": prompt}
    ])
    return response['message']['content'].strip()

# ----- Main Runner -----
def main():
    pdf_path = input("📄 Enter path to the candidate's CV PDF: ").strip()
    
    print("📤 Extracting text from PDF...")
    cv_text = extract_text_from_pdf(pdf_path)
    
    print("🤖 Sending to Gemma 2:2b...")
    result = analyze_cv(cv_text)

    print("\n✅ Extracted CV Insights:\n")
    print(result)

    # Save to file
    with open("cv_analysis_output.txt", "w", encoding="utf-8") as f:
        f.write(result)

    print("\n💾 Output saved to 'cv_analysis_output.txt'")

if __name__ == "__main__":
    main()
