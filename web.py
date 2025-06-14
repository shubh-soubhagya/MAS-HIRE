from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
import time
from werkzeug.utils import secure_filename
import threading

# Import your existing modules
from JDParsingAgent.jobDescription_Agent import load_csv, process_job_descriptions, save_to_csv
from CVParsingAgent.CVExtractor_Agent import process_all_pdfs
from MatchScoreAgent.MatchScore_Agent import load_and_clean_data, match_cvs_with_jobs, save_results
from SendEMailAgent.email_agent import authenticate, build, send_email

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables for status tracking
processing_status = {
    'stage': 'idle',
    'progress': 0,
    'message': 'Ready to start processing'
}

# Ensure directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('agents_outputs', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_job_descriptions', methods=['POST'])
def upload_job_descriptions():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions.csv')
        file.save(filepath)
        return jsonify({'success': True, 'message': 'Job descriptions uploaded successfully'})
    
    return jsonify({'success': False, 'message': 'Please upload a CSV file'})

@app.route('/upload_cvs', methods=['POST'])
def upload_cvs():
    if 'files' not in request.files:
        return jsonify({'success': False, 'message': 'No files uploaded'})
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({'success': False, 'message': 'No files selected'})
    
    cv_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'cvs')
    os.makedirs(cv_folder, exist_ok=True)
    
    uploaded_count = 0
    for file in files:
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(cv_folder, filename)
            file.save(filepath)
            uploaded_count += 1
    
    return jsonify({
        'success': True, 
        'message': f'{uploaded_count} CV files uploaded successfully'
    })

@app.route('/process', methods=['POST'])
def process_data():
    data = request.json
    process_jd = data.get('process_jd', False)
    
    def run_processing():
        global processing_status
        
        try:
            # Stage 1: JD Processing
            if process_jd:
                processing_status.update({
                    'stage': 'jd_processing',
                    'progress': 10,
                    'message': 'Processing job descriptions...'
                })
                
                input_path = os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions.csv')
                output_path = os.path.join('agents_outputs', 'jobs_summary_extracted.csv')
                
                df = load_csv(input_path)
                final_df = process_job_descriptions(df)
                save_to_csv(final_df, output_path)
            else:
                processing_status.update({
                    'stage': 'jd_skipped',
                    'progress': 10,
                    'message': 'JD processing skipped'
                })
            
            # Stage 2: CV Processing
            processing_status.update({
                'stage': 'cv_processing',
                'progress': 40,
                'message': 'Processing CV files...'
            })
            
            cv_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'cvs')
            process_all_pdfs(cv_folder)
            
            # Stage 3: Match Score Calculation
            processing_status.update({
                'stage': 'matching',
                'progress': 70,
                'message': 'Calculating match scores...'
            })
            
            cv_path = os.path.join('agents_outputs', 'cv_analysis_output.csv')
            jd_path = os.path.join('agents_outputs', 'jobs_summary_extracted.csv')
            
            cv_df, jd_df = load_and_clean_data(cv_path, jd_path)
            results_df = match_cvs_with_jobs(cv_df, jd_df)
            save_results(results_df)
            
            # Stage 4: Email Processing
            processing_status.update({
                'stage': 'email_processing',
                'progress': 90,
                'message': 'Sending emails to shortlisted candidates...'
            })
            
            # Email logic here (simplified for demo)
            time.sleep(2)  # Simulate email processing
            
            # Complete
            processing_status.update({
                'stage': 'complete',
                'progress': 100,
                'message': 'Processing completed successfully!'
            })
            
        except Exception as e:
            processing_status.update({
                'stage': 'error',
                'progress': 0,
                'message': f'Error: {str(e)}'
            })
    
    # Start processing in background thread
    thread = threading.Thread(target=run_processing)
    thread.start()
    
    return jsonify({'success': True, 'message': 'Processing started'})

@app.route('/status')
def get_status():
    return jsonify(processing_status)

@app.route('/download/<file_type>')
def download_file(file_type):
    try:
        if file_type == 'cv_analysis':
            filepath = os.path.join('agents_outputs', 'cv_analysis_output.csv')
            return send_file(filepath, as_attachment=True, download_name='cv_analysis_output.csv')
        elif file_type == 'shortlisted':
            filepath = os.path.join('agents_outputs', 'cv_match_scores.csv')
            return send_file(filepath, as_attachment=True, download_name='cv_match_scores.csv')
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)