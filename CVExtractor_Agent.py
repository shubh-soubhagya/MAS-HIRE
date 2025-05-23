import ollama
import PyPDF2
import csv
import os
import re


test = r"test_pdf"

# ----- Predefined Job Roles -----
job_roles = [
    "Software Engineer", "Data Scientist", "Product Manager", "Cloud Engineer",
    "Cybersecurity Analyst", "Machine Learning Engineer", "DevOps Engineer",
    "Full Stack Developer", "Big Data Engineer", "AI Researcher", "Database Administrator",
    "Network Engineer", "Software Architect", "Blockchain Developer", "IT Project Manager",
    "Business Intelligence Analyst", "Robotics Engineer", "Embedded Systems Engineer",
    "Quality Assurance Engineer", "UX/UI Designer"
]

# job_roles = [
#     "Data Scientist", "Product Manager"
# ]

# ----- Extract Text from PDF -----
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

# ----- Prompt Construction -----
def generate_prompt(cv_text):
    return f"""
You are an expert recruiter assistant.

From the following resume, extract the following in the EXACT format:

**Applicant Name:** Full Name  
**Email:** email@example.com  
**Phone Number:** +91-XXXXXXX  

**Required Skills:**
* Skill 1
* Skill 2

**Required Experience:**
* Experience 1
* Experience 2

**Required Qualifications:**
* Qualification 1 (e.g., Bachelor's or any other degree in Computer Science or any other domain)
* Qualification 2 

**Job Responsibilities:**
* Responsibility 1
* Responsibility 2

From this list:
{', '.join(job_roles)}

Predict one or more job roles the candidate fits best, like this:
**Predicted Job Role:** Role 1, Role 2
There shouldn't be NULL values or Unknown Job roles. There should be atleast one job role.


Resume:
{cv_text}
"""

# ----- Ollama API Call -----
def analyze_cv(cv_text):
    prompt = generate_prompt(cv_text)
    response = ollama.chat(model='gemma2:2b', messages=[
        {"role": "system", "content": "You are a professional HR assistant."},
        {"role": "user", "content": prompt}
    ])
    return response['message']['content'].strip()

# ----- Extract Info Using Regex ----
def extract_info(response):
    name = re.search(r"\*\*Applicant Name:\*\*\s*(.*)", response)
    email = re.search(r"\*\*Email:\*\*\s*(.*)", response)
    phone = re.search(r"\*\*Phone Number:\*\*\s*(.*)", response)
    roles = re.search(r"\*\*Predicted Job Role:\*\*\s*(.*)", response)

    # Clean values
    applicant_name = name.group(1).strip() if name else "Not found"
    email_id = email.group(1).strip() if email else "Not found"
    phone_no = phone.group(1).strip() if phone else "Not found"
    predicted_roles = roles.group(1).strip().split(",") if roles else ["Unknown"]
    predicted_roles = [r.strip() for r in predicted_roles if r.strip()]

    # Clean response (remove extracted fields)
    cleaned_response = re.sub(r"\*\*Applicant Name:\*\*.*", "", response)
    cleaned_response = re.sub(r"\*\*Email:\*\*.*", "", cleaned_response)
    cleaned_response = re.sub(r"\*\*Phone Number:\*\*.*", "", cleaned_response)
    cleaned_response = re.sub(r"\*\*Predicted Job Role:\*\*.*", "", cleaned_response).strip()

    return applicant_name, email_id, phone_no, predicted_roles, cleaned_response

# ----- Analyze Single PDF -----
def process_single_pdf(pdf_path):
    print(f"📤 Extracting text from: {pdf_path}")
    cv_text = extract_text_from_pdf(pdf_path)

    print("🤖 Sending to Gemma 2:2b...")
    result = analyze_cv(cv_text)

    return extract_info(result)

# ----- Process All PDFs in Folder -----
def process_all_pdfs(folder_path):
    output_data = []
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print("❌ No PDF files found in folder.")
        return

    for pdf_file in pdf_files:
        full_path = os.path.join(folder_path, pdf_file)
        try:
            name, email, phone, roles, info = process_single_pdf(full_path)
            for role in roles:
                output_data.append([name, email, phone, info, role])
        except Exception as e:
            print(f"⚠️ Error processing {pdf_file}: {e}")

    # Save all results
    with open(r"agents_outputs\cv_analysis_output.csv", mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["applicant_name", "email", "phone_no", "cv_extracted_info", "job_role"])
        writer.writerows(output_data)

    print("\n✅ All results saved to 'cv_analysis_output.csv'.")

# ----- Main Entry -----
if __name__ == "__main__":
    process_all_pdfs(test)  # or any other folder you want to scan
