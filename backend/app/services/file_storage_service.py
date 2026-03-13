"""File storage service for handling file uploads and validation."""
import os
import uuid
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


class FileStorageService:
    """Service for handling file storage operations."""
    
    # Allowed MIME types as per requirements
    ALLOWED_TYPES = {
        'image/png',
        'image/jpeg',
        'image/gif',
        'application/pdf',
        'audio/mpeg',
        'audio/wav'
    }
    
    # Maximum file size: 10MB
    MAX_SIZE = 10 * 1024 * 1024
    
    def __init__(self, upload_folder: str, base_url: str = 'http://localhost:5000'):
        """
        Initialize the file storage service.
        
        Args:
            upload_folder: Directory path where files will be stored
            base_url: Base URL for generating public file URLs
        """
        self.upload_folder = upload_folder
        self.base_url = base_url.rstrip('/')
        
        # Create upload folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
    
    def validate_file_type(self, file: FileStorage) -> tuple[bool, str]:
        """
        Validate file type against allowed formats.
        
        Args:
            file: File to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file.content_type:
            return False, "File type could not be determined"
        
        if file.content_type not in self.ALLOWED_TYPES:
            return False, f"File type {file.content_type} is not allowed"
        
        return True, ""
    
    def validate_file_size(self, file: FileStorage) -> tuple[bool, str]:
        """
        Validate file size does not exceed 10MB limit.
        
        Args:
            file: File to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Seek to end to get file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if size > self.MAX_SIZE:
            size_mb = size / (1024 * 1024)
            return False, f"File size {size_mb:.2f}MB exceeds maximum allowed size of 10MB"
        
        return True, ""
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate unique filename using UUID + extension.
        
        Args:
            original_filename: Original filename from upload
            
        Returns:
            Unique filename string
        """
        # Secure the filename and extract extension
        secured = secure_filename(original_filename)
        
        # Get file extension
        if '.' in secured:
            extension = secured.rsplit('.', 1)[1].lower()
        else:
            extension = ''
        
        # Generate UUID-based filename
        unique_id = str(uuid.uuid4())
        
        if extension:
            return f"{unique_id}.{extension}"
        else:
            return unique_id
    
    def store_file(self, file: FileStorage) -> tuple[bool, str, dict]:
        """
        Store file to local filesystem after validation.
        
        Args:
            file: File to store
            
        Returns:
            Tuple of (success, error_or_url, metadata)
            - success: Boolean indicating if storage was successful
            - error_or_url: Error message if failed, public URL if successful
            - metadata: Dictionary with file information (filename, size, type)
        """
        # Validate file type
        is_valid, error = self.validate_file_type(file)
        if not is_valid:
            return False, error, {}
        
        # Validate file size
        is_valid, error = self.validate_file_size(file)
        if not is_valid:
            return False, error, {}
        
        # Generate unique filename
        unique_filename = self.generate_unique_filename(file.filename or 'unnamed')
        
        # Get file size for metadata
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        # Save file to disk
        try:
            file_path = os.path.join(self.upload_folder, unique_filename)
            file.save(file_path)
        except Exception as e:
            return False, f"Failed to save file: {str(e)}", {}
        
        # Generate public URL
        public_url = f"{self.base_url}/uploads/{unique_filename}"
        
        # Prepare metadata
        metadata = {
            'filename': unique_filename,
            'size': file_size,
            'type': file.content_type
        }
        
        return True, public_url, metadata
