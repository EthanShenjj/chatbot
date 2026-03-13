"""Upload routes for file handling."""
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import RequestEntityTooLarge
from app.services.file_storage_service import FileStorageService
import os
import sys

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

bp = Blueprint('upload', __name__, url_prefix='/api')

# Initialize file storage service
file_storage_service = FileStorageService(
    upload_folder=Config.UPLOAD_FOLDER,
    base_url=os.getenv('BASE_URL', 'http://localhost:5000')
)


@bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload with validation.
    
    Accepts multipart/form-data with 'file' field.
    Returns public URL within 2 seconds when validation passes.
    Returns structured error response for validation failures.
    
    Requirements: 3.3, 3.4
    """
    # Check if file is present in request
    if 'file' not in request.files:
        return jsonify({
            'error': 'No file provided',
            'code': 'NO_FILE'
        }), 400
    
    file = request.files['file']
    
    # Check if file has a filename
    if file.filename == '':
        return jsonify({
            'error': 'No file selected',
            'code': 'NO_FILE'
        }), 400
    
    # Store file with validation
    success, result, metadata = file_storage_service.store_file(file)
    
    if not success:
        # Determine error code based on error message
        error_code = 'INVALID_FILE_TYPE' if 'type' in result.lower() else 'FILE_TOO_LARGE'
        
        return jsonify({
            'error': result,
            'code': error_code
        }), 400
    
    # Return success response with public URL
    return jsonify({
        'url': result,
        'filename': metadata['filename'],
        'size': metadata['size'],
        'type': metadata['type']
    }), 200


@bp.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    """Handle file size exceeding Flask's MAX_CONTENT_LENGTH."""
    return jsonify({
        'error': 'File size exceeds maximum allowed size of 10MB',
        'code': 'FILE_TOO_LARGE'
    }), 413
