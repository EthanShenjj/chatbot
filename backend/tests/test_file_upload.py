"""Tests for file upload functionality."""
import pytest
import io
import os
from werkzeug.datastructures import FileStorage


class TestFileUploadEndpoint:
    """Test file upload API endpoint."""
    
    def test_upload_valid_image(self, client):
        """Test uploading a valid image file."""
        # Create a fake PNG file
        data = {
            'file': (io.BytesIO(b'fake png content'), 'test.png', 'image/png')
        }
        
        response = client.post(
            '/api/upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'url' in json_data
        assert 'filename' in json_data
        assert 'size' in json_data
        assert 'type' in json_data
        assert json_data['type'] == 'image/png'
    
    def test_upload_no_file(self, client):
        """Test upload request without file."""
        response = client.post('/api/upload')
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data['code'] == 'NO_FILE'
    
    def test_upload_invalid_file_type(self, client):
        """Test uploading an invalid file type."""
        data = {
            'file': (io.BytesIO(b'fake content'), 'test.txt', 'text/plain')
        }
        
        response = client.post(
            '/api/upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data['code'] == 'INVALID_FILE_TYPE'
    
    def test_upload_file_too_large(self, client):
        """Test uploading a file that exceeds size limit."""
        # Create a file larger than 10MB
        large_content = b'x' * (11 * 1024 * 1024)
        data = {
            'file': (io.BytesIO(large_content), 'large.png', 'image/png')
        }
        
        response = client.post(
            '/api/upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Flask returns 413 for files exceeding MAX_CONTENT_LENGTH
        assert response.status_code == 413
        json_data = response.get_json()
        assert json_data['code'] == 'FILE_TOO_LARGE'


class TestFileStorageService:
    """Test file storage service."""
    
    def test_validate_allowed_file_types(self):
        """Test that all allowed file types are accepted."""
        from app.services.file_storage_service import FileStorageService
        
        service = FileStorageService(upload_folder='test_uploads')
        
        allowed_types = [
            'image/png', 'image/jpeg', 'image/gif',
            'application/pdf', 'audio/mpeg', 'audio/wav'
        ]
        
        for mime_type in allowed_types:
            file = FileStorage(
                stream=io.BytesIO(b'test'),
                filename='test.file',
                content_type=mime_type
            )
            is_valid, error = service.validate_file_type(file)
            assert is_valid, f"{mime_type} should be valid but got error: {error}"
    
    def test_unique_filename_generation(self):
        """Test that unique filenames are generated."""
        from app.services.file_storage_service import FileStorageService
        
        service = FileStorageService(upload_folder='test_uploads')
        
        filename1 = service.generate_unique_filename('test.png')
        filename2 = service.generate_unique_filename('test.png')
        
        assert filename1 != filename2
        assert filename1.endswith('.png')
        assert filename2.endswith('.png')
