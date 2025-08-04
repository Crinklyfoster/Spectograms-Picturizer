"""
Motor Fault Detection Flask Application
Main application file with routes for upload, analysis, and clearing results.
"""

from flask import Flask, render_template, request, redirect, url_for, session, send_file, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
import pandas as pd
import json
from io import BytesIO

from backend.spectrograms import generate_all_spectrograms
from backend.features import extract_all_features
from backend.utils import save_uploaded_file, clear_session_files, get_upload_path

app = Flask(__name__)
app.secret_key = 'motor_fault_detection_secret_key_2025'

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'm4a', 'ogg'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if uploaded file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main upload page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and redirect to analysis."""
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            
            # Save uploaded file
            filename = save_uploaded_file(file, session_id)
            session['filename'] = filename
            
            return redirect(url_for('results'))
        except Exception as e:
            app.logger.error(f"Upload error: {str(e)}")
            return render_template('index.html', error="Error uploading file. Please try again.")
    
    return render_template('index.html', error="Invalid file type. Please upload WAV, MP3, FLAC, M4A, or OGG files.")

@app.route('/results')
def results():
    """Generate and display analysis results."""
    if 'session_id' not in session or 'filename' not in session:
        return redirect(url_for('index'))
    
    session_id = session['session_id']
    filename = session['filename']
    
    try:
        # Get file path
        audio_path = get_upload_path(filename, session_id)
        
        if not os.path.exists(audio_path):
            return redirect(url_for('index'))
        
        # Generate spectrograms
        spectrogram_paths = generate_all_spectrograms(audio_path, session_id)
        
        # Convert file paths to web URLs for each spectrogram
        for spec_type in spectrogram_paths:
            if 'path' in spectrogram_paths[spec_type]:
                # Convert file path to web URL
                filename_only = os.path.basename(spectrogram_paths[spec_type]['path'])
                spectrogram_paths[spec_type]['path'] = url_for('serve_result_file', 
                                                              session_id=session_id, 
                                                              filename=filename_only)
        
        # Extract features
        features_df = extract_all_features(audio_path)
        
        # Store features in session for download
        session['features'] = features_df.to_dict('records')[0]
        
        # Convert features to readable format for display
        features_display = {}
        for key, value in session['features'].items():
            if isinstance(value, float):
                features_display[key] = round(value, 4)
            else:
                features_display[key] = value
        
        return render_template('results.html', 
                             spectrograms=spectrogram_paths,
                             features=features_display,
                             filename=filename)
    
    except Exception as e:
        app.logger.error(f"Analysis error: {str(e)}")
        return render_template('index.html', error=f"Error analyzing file: {str(e)}")

@app.route('/results/<session_id>/<filename>')
def serve_result_file(session_id, filename):
    """Serve generated result files (spectrograms)."""
    try:
        # Security check: ensure session_id matches current session
        if 'session_id' not in session or session['session_id'] != session_id:
            return "Unauthorized", 403
        
        results_dir = os.path.join(os.getcwd(), 'results', session_id)
        
        # Check if file exists
        file_path = os.path.join(results_dir, filename)
        if not os.path.exists(file_path):
            app.logger.error(f"File not found: {file_path}")
            return "File not found", 404
        
        return send_from_directory(results_dir, filename)
    
    except Exception as e:
        app.logger.error(f"Error serving file {filename}: {str(e)}")
        return "Error serving file", 500

@app.route('/download/<format>')
def download_features(format):
    """Download features in CSV or JSON format."""
    if 'features' not in session:
        return redirect(url_for('index'))
    
    features = session['features']
    
    if format == 'csv':
        # Create CSV
        df = pd.DataFrame([features])
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(output, 
                        mimetype='text/csv',
                        as_attachment=True,
                        download_name='motor_features.csv')
    
    elif format == 'json':
        # Create JSON
        output = BytesIO()
        json_str = json.dumps(features, indent=2)
        output.write(json_str.encode())
        output.seek(0)
        
        return send_file(output,
                        mimetype='application/json',
                        as_attachment=True,
                        download_name='motor_features.json')
    
    return redirect(url_for('results'))

@app.route('/clear', methods=['POST'])
def clear_results():
    """Clear all session data and uploaded files."""
    if 'session_id' in session:
        clear_session_files(session['session_id'])
    
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html', error="Page not found."), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal server error: {str(error)}")
    return render_template('index.html', error="Internal server error."), 500

# Add a health check route for debugging
@app.route('/health')
def health_check():
    """Health check endpoint."""
    return {
        'status': 'healthy',
        'upload_folder_exists': os.path.exists(UPLOAD_FOLDER),
        'results_folder_exists': os.path.exists(RESULTS_FOLDER),
        'session_active': 'session_id' in session
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
