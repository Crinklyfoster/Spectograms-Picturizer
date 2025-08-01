"""
Full-Stack Flask Motor Audio Analysis Application
Combines frontend serving and backend API in single Flask app
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_from_directory
import os
import tempfile
import uuid
from werkzeug.utils import secure_filename
import json
import logging
from datetime import datetime
import mimetypes

from backend.audio_utils import AudioProcessor
from backend.spectrograms import SpectrogramGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change in production

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['TEMP_FOLDER'] = os.path.join('backend', 'temp_files')

# Ensure directories exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['TEMP_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Initialize processors
audio_processor = AudioProcessor()
spectrogram_generator = SpectrogramGenerator()

# Session storage for files and results
session_data = {}

@app.route('/')
def index():
    """Main page with upload interface"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and initial processing"""
    try:
        # Check if file was uploaded
        if 'audio_file' not in request.files:
            flash('No audio file selected', 'error')
            return redirect(url_for('index'))
        
        file = request.files['audio_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        # Validate file type
        allowed_extensions = {'wav', 'mp3', 'flac', 'm4a'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            flash('Invalid file type. Please upload WAV, MP3, FLAC, or M4A files.', 'error')
            return redirect(url_for('index'))
        
        # Generate session ID and save file
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        
        filename = secure_filename(f"{session_id}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Store file info in session
        session_data[session_id] = {
            'filename': file.filename,
            'file_path': file_path,
            'upload_time': datetime.now().isoformat()
        }
        
        flash('File uploaded successfully! Processing...', 'success')
        return redirect(url_for('analyze', session_id=session_id))
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        flash(f'Upload failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/analyze/<session_id>')
def analyze(session_id):
    """Process audio and display results"""
    try:
        if session_id not in session_data:
            flash('Session not found', 'error')
            return redirect(url_for('index'))
        
        session_info = session_data[session_id]
        file_path = session_info['file_path']
        
        # Load and validate audio
        audio_data, sample_rate = audio_processor.load_audio(file_path)
        
        # Check duration
        duration = len(audio_data) / sample_rate
        if duration > 20:
            flash(f'Audio too long: {duration:.1f}s (max 20s)', 'error')
            return redirect(url_for('index'))
        
        # Extract features
        logger.info("Extracting audio features...")
        features = audio_processor.extract_features(audio_data, sample_rate)
        
        # Generate spectrograms
        logger.info("Generating spectrograms...")
        spectrograms = {}
        
        spectrogram_types = [
            ('mel_spectrogram', 'Mel-Spectrogram'),
            ('cqt', 'Constant-Q Transform'),
            ('log_stft', 'Log-STFT'),
            ('wavelet_scalogram', 'Wavelet Scalogram'),
            ('spectral_kurtosis', 'Spectral Kurtosis'),
            ('modulation_spectrogram', 'Modulation Spectrogram')
        ]
        
        for spec_key, spec_name in spectrogram_types:
            try:
                method = getattr(spectrogram_generator, f'generate_{spec_key}')
                spectrograms[spec_key] = {
                    'name': spec_name,
                    'data': method(audio_data, sample_rate)
                }
            except Exception as e:
                logger.warning(f"Failed to generate {spec_name}: {e}")
                spectrograms[spec_key] = {
                    'name': spec_name,
                    'data': None,
                    'error': str(e)
                }
        
        # Store results
        session_data[session_id].update({
            'duration': duration,
            'sample_rate': sample_rate,
            'features': features,
            'spectrograms': spectrograms,
            'analysis_time': datetime.now().isoformat()
        })
        
        return render_template('results.html', 
                             session_id=session_id, 
                             data=session_data[session_id])
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        flash(f'Analysis failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/features/<session_id>')
def get_features(session_id):
    """API endpoint to get features as JSON"""
    if session_id not in session_data or 'features' not in session_data[session_id]:
        return jsonify({'error': 'No features found'}), 404
    
    return jsonify(session_data[session_id]['features'])

@app.route('/download/csv/<session_id>')
def download_csv(session_id):
    """Download features as CSV"""
    if session_id not in session_data or 'features' not in session_data[session_id]:
        flash('No features available for download', 'error')
        return redirect(url_for('index'))
    
    features = session_data[session_id]['features']
    
    # Create CSV content
    csv_content = "feature,value\n"
    for key, value in features.items():
        csv_content += f"{key},{value}\n"
    
    from flask import Response
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=features_{session_id}.csv"}
    )

@app.route('/download/json/<session_id>')
def download_json(session_id):
    """Download features as JSON"""
    if session_id not in session_data or 'features' not in session_data[session_id]:
        flash('No features available for download', 'error')
        return redirect(url_for('index'))
    
    features = session_data[session_id]['features']
    
    from flask import Response
    return Response(
        json.dumps(features, indent=2),
        mimetype="application/json",
        headers={"Content-disposition": f"attachment; filename=features_{session_id}.json"}
    )

@app.route('/clear')
def clear_session():
    """Clear current session and files"""
    session_id = session.get('session_id')
    if session_id and session_id in session_data:
        # Remove uploaded file
        file_path = session_data[session_id].get('file_path')
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        # Clear session data
        del session_data[session_id]
    
    session.clear()
    flash('Session cleared successfully', 'success')
    return redirect(url_for('index'))

@app.errorhandler(413)
def file_too_large(e):
    flash('File too large (max 50MB)', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    flash('Internal server error occurred', 'error')
    return redirect(url_for('index'))

from flask import send_from_directory, Response
import mimetypes
import os

@app.route('/audio/<session_id>/<filename>')
def serve_audio(session_id, filename):
    """Serve audio files with proper headers for streaming"""
    try:
        if session_id not in session_data:
            return "File not found", 404
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        
        if not os.path.exists(file_path):
            return "File not found", 404
        
        # Get file size for proper streaming
        file_size = os.path.getsize(file_path)
        
        # Set proper MIME type
        if filename.lower().endswith('.mp3'):
            mimetype = 'audio/mpeg'
        elif filename.lower().endswith('.wav'):
            mimetype = 'audio/wav'
        elif filename.lower().endswith('.m4a'):
            mimetype = 'audio/mp4'
        elif filename.lower().endswith('.flac'):
            mimetype = 'audio/flac'
        else:
            mimetype = 'audio/mpeg'
        
        def generate():
            with open(file_path, 'rb') as audio_file:
                data = audio_file.read(1024)
                while data:
                    yield data
                    data = audio_file.read(1024)
        
        response = Response(
            generate(),
            mimetype=mimetype,
            headers={
                'Content-Length': str(file_size),
                'Accept-Ranges': 'bytes',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'Access-Control-Allow-Origin': '*'
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error serving audio file: {e}")
        return "Error serving file", 500

if __name__ == '__main__':
    logger.info("Starting Motor Audio Analysis Flask App...")
    app.run(debug=True, host='0.0.0.0', port=5000)


