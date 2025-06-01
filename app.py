# from jobDescription_Agent import load_csv, process_job_descriptions, save_to_csv 



# ######### JD ########

# input_path_jd = r"data\job_description.csv"
# output_path_jd = r"agents_outputs\jobs_summary_extracted.csv"

# df = load_csv(input_path_jd)
# final_df = process_job_descriptions(df)
# save_to_csv(final_df, output_path_jd)

######## CV #########

from CVExtractor_Agent import process_all_pdfs

test = r"one"

process_all_pdfs(test)

########### Match Score ###########

from MatchScore_Agent import load_and_clean_data, match_cvs_with_jobs, save_results
cv_path = r"agents_outputs\cv_analysis_output.csv"
jd_path = r"agents_outputs\jobs_summary_extracted.csv"


cv_df, jd_df = load_and_clean_data(cv_path, jd_path)
results_df = match_cvs_with_jobs(cv_df, jd_df)
save_results(results_df)