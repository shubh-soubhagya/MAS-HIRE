import pandas as pd
import ollama
from tqdm import tqdm


jd_df = pd.read_csv(r"cv_analysis_output.csv")
cv_df = pd.read_csv(r"jobs_summary_extracted.csv")


print(jd_df.columns)