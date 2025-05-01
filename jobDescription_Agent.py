import pandas as pd
import ollama
from tqdm import tqdm

def load_csv(file_path: str, encoding: str = 'cp1252') -> pd.DataFrame:
    return pd.read_csv(file_path, encoding=encoding)

def get_extract_prompt(jd: str) -> str:
    return f"""
From the following job description, extract the following key points clearly and concisely:
- Required Skills
- Required Experience
- Required Qualifications
- Job Responsibilities

Format the output with clear headings and bullet points.

Job Description:
{jd}
"""

def get_summary_prompt(jd: str) -> str:
    return f"""
Summarize the following job description into 3-4 concise lines:

Job Description:
{jd}
"""

def extract_info(jd: str) -> str:
    response = ollama.chat(
        model='gemma2:2b',
        messages=[
            {"role": "system", "content": "You are an AI recruiter assistant."},
            {"role": "user", "content": get_extract_prompt(jd)}
        ]
    )
    return response['message']['content'].strip()

def summarize_jd(jd: str) -> str:
    response = ollama.chat(
        model='gemma2:2b',
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes job descriptions."},
            {"role": "user", "content": get_summary_prompt(jd)}
        ]
    )
    return response['message']['content'].strip()

def process_job_descriptions(df: pd.DataFrame) -> pd.DataFrame:
    summarized_list = []
    extracted_info_list = []

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing Jobs"):
        jd = row['Job Description']
        summarized_list.append(summarize_jd(jd))
        extracted_info_list.append(extract_info(jd))

    df['summarized_jd'] = summarized_list
    df['extracted_info'] = extracted_info_list
    return df[['Job Title', 'Job Description', 'summarized_jd', 'extracted_info']]

def save_to_csv(df: pd.DataFrame, output_path: str) -> None:
    df.to_csv(output_path, index=False)
    print(f"✅ Output saved to '{output_path}'")


input_path = r"data\job_description.csv"
output_path = "jobs_summary_extracted.csv"

def main_jd():
    df = load_csv(input_path)
    final_df = process_job_descriptions(df)
    save_to_csv(final_df, output_path)

if __name__ == "__main__":
    main_jd()


