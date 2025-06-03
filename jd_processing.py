from JDParsingAgent.jobDescription_Agent import load_csv, process_job_descriptions, save_to_csv

input_path = r"jd_data\job_description.csv"
output_path = r"agents_outputs\jobs_summary_extracted.csv"

df = load_csv(input_path)
final_df = process_job_descriptions(df)
save_to_csv(final_df, output_path)
