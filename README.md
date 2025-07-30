# MAS Hire (Multi-Agent System for Intelligent Hiring and Resmume Evaluation)

MAS HIRE is a Command-Line Interface (CLI)-based multi-agent recruitment automation tool that streamlines the end-to-end hiring process through modular and intelligent agents.

Built for efficiency, MAS HIRE enables recruiters and HR analysts to perform job description parsing, resume processing, candidate-job role matching, and email communication — all directly from the command line.

## 🧩 Core Agents in Action:
- **JD Parsing Agent**: Reads job description CSVs, extracts key role features, and prepares structured summaries.
- **CV Extraction Agent**: Processes multiple resumes in PDF format, extracting structured candidate information like emaila and contact details.
- **Match Score Agent**: Calculates match scores between job roles and candidates using intelligent fine prompted agent.
- **Email Notification Agent**: Automatically sends customized emails to shortlisted candidates based on score thresholds.

## 🚀 Setup & Running Instructions
Follow these steps to get the application up and running:

### 1. 🔧 Install Ollama and Pull `gemma2:2b` Model
Make sure [Ollama](https://ollama.com/) is installed and running on your system.
Then, pull the required model by running the following command in your terminal:
```bash
ollama pull gemma2:2b
```

### 2. 📦 Install Python Dependencies
Install all required Python libraries using requirements.txt:
```bash
pip install -r requirements.txt
```

#### 3. 🔐 Set Up Gmail API Credentials
- Visit the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
- Create a project (if you don’t have one).
- Enable the Gmail API.
- Create OAuth 2.0 Client ID credentials.
- Download the .json file and rename it as: `credentials_email.json`
- Save it in the following path: `credentials/credentials_email.json`

### 4. ✅ Authorize Gmail Access
When you run the app for the first time, it will prompt a browser window for you to authorize access to your Gmail account.
Make sure you're signed in to the correct account when granting permissions.

### 5. 📄 Add Resumes
Put all resume PDF files you want to process inside the following folder: `upload_your_resume/`

### 6. 🧠 Run the Application
Finally, run the script:
```bash
python app.py
```

### 📝 Notes
- Make sure your environment supports Python 3.7+.
- Ensure the Gmail account used allows access from third-party apps via OAuth.
- Enter your Gmail Account in `app.py` in `sender_email`.
- You can also change the `subject` and `body` of email in `app.py`.

Once the process is complete, the results will be automatically emailed using your configured Gmail account.

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork this repo, make changes, and submit a pull request. If you find a bug or have a feature request, please open an issue.

---

## 📧 Contact
For any queries or collaborations:
**Soubhagya Srivastava**  
📧 soubhagyasrivastava@240gmail.com 
🌐 [LinkedIn](https://www.linkedin.com/in/yourprofile)  

