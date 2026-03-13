"""Unit tests for FileStorageService."""
import pytest
import os
import tempfile
import shutil
from io import BytesIO
from werkzeug.datastructures import FileStorage
from app.services.file_storage_service import FileStorageService


@pytest.fixture
def temp_upload_dir():
    """Create a temporary directory for file uploads."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def file_service(temp_upload_dir):
    """Create a FileStorageService instance with temporary directory."""
    return FileStorageService(
        upload_folder=temp_upload_dir,
        base_url='http://localhost:5000'
    )


def create_mock_file(filename: str, content: bytes, content_type: str) -> FileStorage:
    """Helper function to create a mock FileStorage object."""
    return FileStorage(
        stream=BytesIO(content),
        filename=filename,
        content_type=content_type
    )


class TestFileTypeValidation:
    """Tests for file type validation."""
    
    def test_validate_allowed_image_png(self, file_service):
        """Test that PNG images are accepted."""
        file = create_mock_file('test.png', b'fake image data', 'image/png')
        is_valid, error = file_service.validate_file_type(file)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_allowed_image_jpeg(self, file_service):
        """Test that JPEG images are accepted."""
        file = create_mock_file('test.jpg', b'fake image data', 'image/jpeg')
        is_valid, error = file_service.validate_file_type(file)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_allowed_image_gif(self, file_service):
        """Test that GIF images are accepted."""
        file = create_mock_file('test.gif', b'fake image data', 'image/gif')
        is_valid, error = file_service.validate_file_type(file)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_allowed_pdf(self, file_service):
        """Test that PDF files are accepted."""
        file = create_mock_file('test.pdf', b'fake pdf data', 'application/pdf')
        is_valid, error = file_service.validate_file_type(file)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_allowed_audio_mpeg(self, file_service):
        """Test that MPEG audio files are accepted."""
        file = create_mock_file('test.mp3', b'fake audio data', 'audio/mpeg')
        is_valid, error = file_service.validate_file_type(file)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_allowed_audio_wav(self, file_service):
        """Test that WAV audio files are accepted."""
        file = create_mock_file('test.wav', b'fake audio data', 'audio/wav')
        is_valid, error = file_service.validate_file_type(file)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_disallowed_file_type(self, file_service):
        """Test that disallowed file types are rejected."""
        file = create_mock_file('test.exe', b'fake exe data', 'application/x-msdownload')
        is_valid, error = file_service.validate_file_type(file)
        
        assert is_valid is False
        assert 'not allowed' in error.lower()
        assert 'application/x-msdownload' in error
    
    def test_validate_missing_content_type(self, file_service):
        """Test that files without content type are rejected."""
        file = create_mock_file('test.txt', b'fake data', None)
        is_valid, error = file_service.validate_file_type(file)
        
        assert is_valid is False
        assert 'could not be determined' in error.lower()


class TestFileSizeValidation:
    """Tests for file size validation."""
    
    def test_validate_file_within_limit(self, file_service):
        """Test that files under 10MB are accepted."""
        # Create 5MB file
        content = b'x' * (5 * 1024 * 1024)
        file = create_mock_file('test.png', content, 'image/png')
        
        is_valid, error = file_service.validate_file_size(file)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_file_at_limit(self, file_service):
        """Test that files exactly at 10MB limit are accepted."""
        # Create exactly 10MB file
        content = b'x' * (10 * 1024 * 1024)
        file = create_mock_file('test.png', content, 'image/png')
        
        is_valid, error = file_service.validate_file_size(file)
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_file_exceeds_limit(self, file_service):
        """Test that files over 10MB are rejected."""
        # Create 11MB file
        content = b'x' * (11 * 1024 * 1024)
        file = create_mock_file('test.png', content, 'image/png')
        
        is_valid, error = file_service.validate_file_size(file)
        
        assert is_valid is False
        assert 'exceeds maximum' in error.lower()
        assert '10mb' in error.lower()
    
    def test_validate_empty_file(self, file_service):
        """Test that empty files are accepted (edge case)."""
        file = create_mock_file('test.png', b'', 'image/png')
        
        is_valid, error = file_service.validate_file_size(file)
        
        assert is_valid is True
        assert error == ""
    
    def test_file_pointer_reset_after_validation(self, file_service):
        """Test that file pointer is reset to beginning after size check."""
        content = b'test content'
        file = create_mock_file('test.png', content, 'image/png')
        
        file_service.validate_file_size(file)
        
        # File pointer should be at beginning
        assert file.tell() == 0
        # Should be able to read full content
        assert file.read() == content


class TestUniqueFilenameGeneration:
    """Tests for unique filename generation."""
    
    def test_generate_filename_with_extension(self, file_service):
        """Test that generated filename includes original extension."""
        filename = file_service.generate_unique_filename('test.png')
        
        assert filename.endswith('.png')
        assert len(filename) > len('.png')  # Has UUID prefix
    
    def test_generate_filename_preserves_extension_case(self, file_service):
        """Test that extension is normalized to lowercase."""
        filename = file_service.generate_unique_filename('test.PNG')
        
        assert filename.endswith('.png')
    
    def test_generate_filename_without_extension(self, file_service):
        """Test filename generation for files without extension."""
        filename = file_service.generate_unique_filename('testfile')
        
        assert '.' not in filename
        assert len(filename) == 36  # UUID length
    
    def test_generate_filename_multiple_dots(self, file_service):
        """Test filename with multiple dots uses last extension."""
        filename = file_service.generate_unique_filename('my.test.file.jpg')
        
        assert filename.endswith('.jpg')
    
    def test_generate_unique_filenames_are_different(self, file_service):
        """Test that multiple calls generate different filenames."""
        filename1 = file_service.generate_unique_filename('test.png')
        filename2 = file_service.generate_unique_filename('test.png')
        
        assert filename1 != filename2
    
    def test_generate_filename_secures_unsafe_characters(self, file_service):
        """Test that unsafe characters are removed from filename."""
        filename = file_service.generate_unique_filename('../../../etc/passwd.png')
        
        # Should not contain path traversal
        assert '..' not in filename
        assert '/' not in filename
        assert filename.endswith('.png')


class TestStoreFile:
    """Tests for complete file storage workflow."""
    
    def test_store_valid_file(self, file_service, temp_upload_dir):
        """Test successful file storage."""
        content = b'test image content'
        file = create_mock_file('test.png', content, 'image/png')
        
        success, result, metadata = file_service.store_file(file)
        
        assert success is True
        assert result.startswith('http://localhost:5000/uploads/')
        assert metadata['type'] == 'image/png'
        assert metadata['size'] == len(content)
        assert 'filename' in metadata
        
        # Verify file was actually saved
        saved_filename = metadata['filename']
        saved_path = os.path.join(temp_upload_dir, saved_filename)
        assert os.path.exists(saved_path)
        
        # Verify content matches
        with open(saved_path, 'rb') as f:
            assert f.read() == content
    
    def test_store_file_invalid_type(self, file_service):
        """Test that invalid file types are rejected."""
        file = create_mock_file('test.exe', b'fake exe', 'application/x-msdownload')
        
        success, error, metadata = file_service.store_file(file)
        
        assert success is False
        assert 'not allowed' in error.lower()
        assert metadata == {}
    
    def test_store_file_exceeds_size_limit(self, file_service):
        """Test that oversized files are rejected."""
        # Create 11MB file
        content = b'x' * (11 * 1024 * 1024)
        file = create_mock_file('test.png', content, 'image/png')
        
        success, error, metadata = file_service.store_file(file)
        
        assert success is False
        assert 'exceeds maximum' in error.lower()
        assert metadata == {}
    
    def test_store_file_without_filename(self, file_service):
        """Test storing file without original filename."""
        content = b'test content'
        file = create_mock_file(None, content, 'image/png')
        
        success, result, metadata = file_service.store_file(file)
        
        assert success is True
        assert 'filename' in metadata
    
    def test_store_multiple_files_unique_names(self, file_service, temp_upload_dir):
        """Test that multiple files get unique names."""
        file1 = create_mock_file('test.png', b'content1', 'image/png')
        file2 = create_mock_file('test.png', b'content2', 'image/png')
        
        success1, url1, metadata1 = file_service.store_file(file1)
        success2, url2, metadata2 = file_service.store_file(file2)
        
        assert success1 is True
        assert success2 is True
        assert metadata1['filename'] != metadata2['filename']
        assert url1 != url2
        
        # Both files should exist
        assert os.path.exists(os.path.join(temp_upload_dir, metadata1['filename']))
        assert os.path.exists(os.path.join(temp_upload_dir, metadata2['filename']))


class TestErrorHandling:
    """Tests for error handling scenarios."""
    
    def test_invalid_upload_folder_creates_directory(self):
        """Test that service creates upload folder if it doesn't exist."""
        temp_dir = tempfile.mkdtemp()
        upload_path = os.path.join(temp_dir, 'uploads', 'nested')
        
        try:
            service = FileStorageService(upload_folder=upload_path)
            assert os.path.exists(upload_path)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_store_file_with_read_only_directory(self, file_service, temp_upload_dir):
        """Test error handling when directory is not writable."""
        # Make directory read-only
        os.chmod(temp_upload_dir, 0o444)
        
        try:
            file = create_mock_file('test.png', b'content', 'image/png')
            success, error, metadata = file_service.store_file(file)
            
            # Should fail gracefully
            assert success is False
            assert 'failed to save' in error.lower()
            assert metadata == {}
        finally:
            # Restore permissions for cleanup
            os.chmod(temp_upload_dir, 0o755)
    
    def test_validate_file_type_with_none_file(self, file_service):
        """Test validation handles None content_type gracefully."""
        file = create_mock_file('test.txt', b'content', None)
        is_valid, error = file_service.validate_file_type(file)
        
        assert is_valid is False
        assert error != ""
