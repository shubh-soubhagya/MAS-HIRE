import pandas as pd
import ollama
from tqdm import tqdm

# ----- Load and Clean Data -----
def load_and_clean_data(cv_path, jd_path):
    cv_df = pd.read_csv(cv_path, encoding='ISO-8859-1')
    jd_df = pd.read_csv(jd_path, encoding='ISO-8859-1')

    # Clean column names
    cv_df.columns = cv_df.columns.str.strip()
    jd_df.columns = jd_df.columns.str.strip()

    return cv_df, jd_df

# ----- Construct Prompt -----
def construct_prompt(cv_info, jd_info):
    return f"""
You are a resume-job match evaluator.

Compare the candidate's CV and the job description. Give:
1. A match score from 0 to 100 based only on content relevance and contextual alignment.
2. A detailed explanation of how this score was determined, including step-by-step evaluation of skills, experience, keywords, and job fit.

### Candidate Info:
{cv_info}

### Job Description Info:
{jd_info}

Respond in the following format:
Score: <number>
Reason: <detailed reasoning>
"""

# ----- Evaluate Match Using Ollama -----
def evaluate_match(cv_info, jd_info):
    prompt = construct_prompt(cv_info, jd_info)

    try:
        response = ollama.chat(model="gemma2:2b", messages=[
            {"role": "system", "content": "You are a resume-job match evaluator. Follow the format: Score: <number>, Reason: <detailed reasoning>."},
            {"role": "user", "content": prompt}
        ])
        content = response['message']['content'].strip()

        # Extract score
        score_line = next((line for line in content.splitlines() if "score" in line.lower()), "")
        match_score = int(''.join(filter(str.isdigit, score_line)))
        reason = content.split("Reason:", 1)[-1].strip() if "Reason:" in content else "No reasoning provided."

    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        match_score = "Error"
        reason = f"Error during evaluation: {e}"

    return match_score, reason

# ----- Process All Matches -----
def match_cvs_with_jobs(cv_df, jd_df):
    output_rows = []
    print("🔍 Matching CVs with Job Descriptions...\n")

    for _, cv_row in tqdm(cv_df.iterrows(), total=len(cv_df)):
        job_role = cv_row['job_role'].strip()
        matching_jd = jd_df[jd_df['Job Title'].str.strip() == job_role]

        if matching_jd.empty:
            match_score = "N/A"
            reason = "No matching job description found for the given role."
        else:
            jd_row = matching_jd.iloc[0]
            match_score, reason = evaluate_match(cv_row['cv_extracted_info'], jd_row['extracted_info'])

        output_rows.append({
            "applicant_name": cv_row["applicant_name"],
            "email": cv_row["email"],
            "phone_no": cv_row["phone_no"],
            "job_role": job_role,
            "match_score": match_score,
            "reason": reason
        })

    return pd.DataFrame(output_rows)

# ----- Save to CSV -----
def save_results(df, filename="cv_match_scores.csv"):
    df.to_csv(filename, index=False)
    print(f"\n✅ Matching complete. Results saved to '{filename}'")

# ----- Main Function -----
def main(cv_path, jd_path):
    cv_df, jd_df = load_and_clean_data(cv_path, jd_path)
    results_df = match_cvs_with_jobs(cv_df, jd_df)
    save_results(results_df)

# ----- Entry Point -----
if __name__ == "__main__":
    main("cv_analysis_output.csv", "jobs_summary_extracted.csv")




# import pandas as pd
# import ollama
# from tqdm import tqdm

# # Load data
# cv_df = pd.read_csv(r"cv_analysis_output.csv")
# jd_df = pd.read_csv(r"jobs_summary_extracted.csv")

# # Clean column names
# cv_df.columns = cv_df.columns.str.strip()
# jd_df.columns = jd_df.columns.str.strip()

# # Output rows
# output_rows = []

# print("🔍 Matching CVs with Job Descriptions...\n")

# # Loop through CV rows
# for _, cv_row in tqdm(cv_df.iterrows(), total=len(cv_df)):
#     job_role = cv_row['job_role'].strip()
#     matching_jd = jd_df[jd_df['Job Title'].str.strip() == job_role]

#     if matching_jd.empty:
#         match_score = "N/A"
#         reason = "No matching job description found for the given role."
#     else:
#         jd_row = matching_jd.iloc[0]

#         # Prompt with instructions for match score and detailed reasoning
#         prompt = f"""
# You are a resume-job match evaluator.

# Compare the candidate's CV and the job description. Give:
# 1. A match score from 0 to 100 based only on content relevance and contextual alignment.
# 2. A detailed explanation of how this score was determined, including step-by-step evaluation of skills, experience, keywords, and job fit.

# ### Candidate Info:
# {cv_row['cv_extracted_info']}

# ### Job Description Info:
# {jd_row['extracted_info']}

# Respond in the following format:
# Score: <number>
# Reason: <detailed reasoning>
# """

#         try:
#             response = ollama.chat(model="gemma2:2b", messages=[
#                 {"role": "system", "content": "You are a resume-job match evaluator. Follow the format: Score: <number>, Reason: <detailed reasoning>."},
#                 {"role": "user", "content": prompt}
#             ])
#             content = response['message']['content'].strip()

#             # Extract score and reason from the response
#             score_line = next((line for line in content.splitlines() if "score" in line.lower()), "")
#             reason_line = content.split("Reason:", 1)[-1].strip() if "Reason:" in content else "No reasoning provided."

#             match_score = int(''.join(filter(str.isdigit, score_line)))
#             reason = reason_line

#         except Exception as e:
#             print(f"❌ Error processing: {e}")
#             match_score = "Error"
#             reason = f"Error during evaluation: {e}"

#     # Append result
#     output_rows.append({
#         "applicant_name": cv_row["applicant_name"],
#         "email": cv_row["email"],
#         "phone_no": cv_row["phone_no"],
#         "job_role": job_role,
#         "match_score": match_score,
#         "reason": reason
#     })

# # Create DataFrame
# results_df = pd.DataFrame(output_rows)

# # Save output
# results_df.to_csv("cv_match_scores.csv", index=False)
# print("\n✅ Matching complete. Results saved to 'cv_match_scores.csv'")