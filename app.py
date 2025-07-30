from JDParsingAgent.jobDescription_Agent import load_csv, process_job_descriptions, save_to_csv
from CVParsingAgent.CVExtractor_Agent import process_all_pdfs
from MatchScoreAgent.MatchScore_Agent import load_and_clean_data, match_cvs_with_jobs, save_results
import pandas as pd
from SendEMailAgent.email_agent import authenticate, build, send_email

######## JD Parsing ##############
user_input = input("🔍 Do you want to run JD parsing? (yes/no): ").strip().lower()
run_jd_parsing = user_input == "yes"

if run_jd_parsing:
    input_path = r"jd_data\job_description.csv"
    output_path = r"agents_outputs\jobs_summary_extracted.csv"

    df = load_csv(input_path)
    final_df = process_job_descriptions(df)
    save_to_csv(final_df, output_path)
    print("✅ JD parsing completed.")
else:
    print("⏭️ JD parsing skipped.")

######## CV #########

test = r"upload_your_resumes"
process_all_pdfs(test)

###################### Match Score ##########################

cv_path = r"agents_outputs\cv_analysis_output.csv"
jd_path = r"agents_outputs\jobs_summary_extracted.csv"

cv_df, jd_df = load_and_clean_data(cv_path, jd_path)
results_df = match_cvs_with_jobs(cv_df, jd_df)
save_results(results_df)
print("✅ Match score computation completed.")

####################### Email Agent Implementation #####################

sender_email = "YOUR_EMAIL_ADDRESS"  # Replace with your Gmail
csv_file = r'agents_outputs\cv_match_scores.csv'

# Load data
try:
    df = pd.read_csv(csv_file)
except Exception as e:
    print(f"❌ Error reading CSV: {e}")
else:
    # Filter applicants
    shortlisted = df[df['match_score'] > 80]

    if shortlisted.empty:
        print("⚠️ No applicants with match_score > 80")
    else:
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
        print("✅ Emails sent to shortlisted candidates.")
