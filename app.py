######## CV #########
from CVParsingAgent.CVExtractor_Agent import process_all_pdfs

test = r"one"

process_all_pdfs(test)

###################### Match Score ##########################

from MatchScoreAgent.MatchScore_Agent import load_and_clean_data, match_cvs_with_jobs, save_results
cv_path = r"agents_outputs\cv_analysis_output.csv"
jd_path = r"agents_outputs\jobs_summary_extracted.csv"


cv_df, jd_df = load_and_clean_data(cv_path, jd_path)
results_df = match_cvs_with_jobs(cv_df, jd_df)
save_results(results_df)

####################### Email Agent Implementation #####################

import pandas as pd
from SendEMailAgent.email_agent import authenticate, build, send_email


sender_email = "soubhagyasrivastava240@gmail.com"  # Replace with your Gmail
csv_file = r'agents_outputs\cv_match_scores.csv'

    # Load data
try:
    df = pd.read_csv(csv_file)
except Exception as e:
    print(f"❌ Error reading CSV: {e}")


    # Filter applicants
shortlisted = df[df['match_score'] > 80]

if shortlisted.empty:
    print("⚠️ No applicants with match_score > 80")
    

    # Authenticate Gmail API
creds = authenticate()
service = build('gmail', 'v1', credentials=creds)

for _, row in shortlisted.iterrows():
    applicant_name = row['applicant_name']
    email = row['email']
    job = row['job_role']

    subject = f"Shortlisted for {job} Role"
    body = f"""
Dear {applicant_name},

We are pleased to inform you that you have been shortlisted for the position of {job} at our organization.

Your qualifications and experience align well with the requirements of the role, and we were impressed by your overall profile.

Our team will be reaching out to you shortly with the next steps in the selection process.

Thank you for your interest, and we look forward to the possibility of working together.

Best regards,  
HR Team
"""


    send_email(service, sender_email, email, subject, body)