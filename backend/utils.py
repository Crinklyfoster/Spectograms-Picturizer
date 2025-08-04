"""
Utility functions for file handling, cleanup, and helper operations.
"""

import os
import shutil
import uuid
from werkzeug.utils import secure_filename

def save_uploaded_file(file, session_id):
    """
    Save uploaded file with a unique name.
    
    Args:
        file: Flask file object
        session_id: Unique session identifier
    
    Returns:
        str: Filename of saved file
    """
    # Create session directory
    session_dir = os.path.join('uploads', session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    
    # Save file
    file_path = os.path.join(session_dir, unique_filename)
    file.save(file_path)
    
    return unique_filename

def get_upload_path(filename, session_id):
    """
    Get the full path to an uploaded file.
    
    Args:
        filename: Name of the file
        session_id: Session identifier
    
    Returns:
        str: Full path to the file
    """
    return os.path.join('uploads', session_id, filename)

def clear_session_files(session_id):
    """
    Remove all files associated with a session.
    
    Args:
        session_id: Session identifier to clear
    """
    # Clear upload directory
    upload_dir = os.path.join('uploads', session_id)
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    
    # Clear results directory
    results_dir = os.path.join('results', session_id)
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)

def ensure_directories():
    """
    Ensure all necessary directories exist.
    """
    directories = ['uploads', 'results', 'static/css', 'static/js', 'templates']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def cleanup_old_sessions(max_age_hours=24):
    """
    Clean up old session files older than specified age.
    
    Args:
        max_age_hours: Maximum age in hours before cleanup
    """
    import time
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    # Clean uploads
    uploads_dir = 'uploads'
    if os.path.exists(uploads_dir):
        for session_dir in os.listdir(uploads_dir):
            session_path = os.path.join(uploads_dir, session_dir)
            if os.path.isdir(session_path):
                dir_age = current_time - os.path.getctime(session_path)
                if dir_age > max_age_seconds:
                    shutil.rmtree(session_path)
    
    # Clean results
    results_dir = 'results'
    if os.path.exists(results_dir):
        for session_dir in os.listdir(results_dir):
            session_path = os.path.join(results_dir, session_dir)
            if os.path.isdir(session_path):
                dir_age = current_time - os.path.getctime(session_path)
                if dir_age > max_age_seconds:
                    shutil.rmtree(session_path)

def get_file_info(file_path):
    """
    Get information about an audio file.
    
    Args:
        file_path: Path to the audio file
    
    Returns:
        dict: File information
    """
    import librosa
    
    try:
        # Load audio to get info
        y, sr = librosa.load(file_path, sr=None)
        
        info = {
            'duration': len(y) / sr,
            'sample_rate': sr,
            'n_samples': len(y),
            'file_size': os.path.getsize(file_path),
            'channels': 1 if y.ndim == 1 else y.shape[0]
        }
        
        return info
    
    except Exception as e:
        return {'error': str(e)}

def validate_audio_file(file_path):
    """
    Validate that the uploaded file is a valid audio file.
    
    Args:
        file_path: Path to the audio file
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        import librosa
        
        # Try to load the file
        y, sr = librosa.load(file_path, sr=None)
        
        # Check if file contains data
        if len(y) == 0:
            return False, "Audio file contains no data"
        
        # Check duration (minimum 0.1 seconds)
        if len(y) / sr < 0.1:
            return False, "Audio file is too short (minimum 0.1 seconds)"
        
        # Check sample rate
        if sr < 1000:
            return False, "Sample rate is too low"
        
        return True, "Valid audio file"
    
    except Exception as e:
        return False, f"Invalid audio file: {str(e)}"
