import logging.config
from django.conf import settings
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from ..files.process_file import *
from unittest.mock import patch, MagicMock
import hashlib
import logging
import time

test_logger = logging.getLogger("tests")

class LoggedTestCase(TestCase):
    def setUp(self):
        self._start_time = time.time()
        test_logger.info(f"Running: {self.__class__.__name__}.{self._testMethodName}")

    def tearDown(self):
        duration = time.time() - self._start_time
        method = self._testMethodName
        class_name = self.__class__.__name__
        result = getattr(self, '_outcome', None)

        errors_logged = False

        if result:
            # Log errors
            for test, exc_info in result.errors:
                if exc_info:
                    test_logger.error(f"{class_name}.{method} - ERROR: {exc_info[1]} - Duration: {duration:.2f}s")
                    errors_logged = True

            # Log failures
            for test, exc_info in result.failures:
                if exc_info:
                    test_logger.error(f"{class_name}.{method} - FAILURE: {exc_info[1]} - Duration: {duration:.2f}s")
                    errors_logged = True

        if not errors_logged:
            test_logger.info(f"{class_name}.{method} - PASSED - Duration: {duration:.2f}s")

    def test_sample(self):
        # Example test to check logging
        test_logger.info("Inside test_sample")
        self.assertEqual(4, 1)


class FileProcessorTestCase(LoggedTestCase):

    def setUp(self):
        super().setUp()
        self.test_content = b"Test content"
        self.uploaded_file = SimpleUploadedFile("test.txt", self.test_content)
    

    def test_valid_file_initialization(self):
        processor = FileProcessor(self.uploaded_file)
        self.assertIsNotNone(processor.file)

    def test_invalid_file_initialization(self):
        with self.assertRaises(ValueError):
            FileProcessor(None)
        with self.assertRaises(TypeError):
            FileProcessor("not_a_file")

    def test_get_file_size(self):
        processor = FileProcessor(self.uploaded_file)
        size = processor._get_file_size()
        self.assertEqual(size, len(self.test_content))

    def test_get_extension(self):
        processor = FileProcessor(self.uploaded_file)
        ext = processor._get_extension()
        self.assertEqual(ext, ".txt")

    def test_calculate_checksum_sha256(self):
        # Patch chunks to simulate Django File chunks()
        self.uploaded_file.chunks = lambda chunk_size: [self.test_content]
        processor = FileProcessor(self.uploaded_file)

        expected_hash = hashlib.sha256(self.test_content).hexdigest()
        self.assertEqual(processor._calculate_checksum(), expected_hash)

    # def test_detect_mime_type_with_magic(self):
    #     # Patch libmagic's Magic
    #     with patch("utils.process_file.Magic") as mock_magic:
            
    
    @patch("utils.process_file.Magic")
    def test_detect_mime_type_with_magic(self, mock_magic):
        mock_instance = mock_magic.return_value
        mock_instance.from_buffer.return_value = "text/plain"
        processor = FileProcessor(self.uploaded_file)
        mime_type = processor._detect_mime_type()
        self.assertEqual(mime_type, "text/plain")
        mock_instance.from_buffer.assert_called()

    def test_detect_mime_type_fallback(self):
        fallback_file = SimpleUploadedFile("test.pdf", b"Fake PDF content")
        fallback_file.chunks = lambda chunk_size: [b"Fake PDF content"]

        with patch("utils.process_file.Magic", side_effect=Exception("Magic failed")):
            processor = FileProcessor(fallback_file)
            mime_type = processor._detect_mime_type()
            self.assertEqual(mime_type, "application/pdf")

    def test_get_metadata_success(self):
        self.uploaded_file.chunks = lambda chunk_size: [self.test_content]
        processor = FileProcessor(self.uploaded_file)
        metadata = processor.get_metadata()

        self.assertEqual(metadata["size"], len(self.test_content))
        self.assertEqual(metadata["extension"], ".txt")
        self.assertEqual(metadata["mime_type"], "text/plain")
        self.assertTrue(metadata["checksum"])

    def test_extract_text_not_implemented(self):
        processor = FileProcessor(self.uploaded_file)
        with self.assertRaises(NotImplementedError):
            processor.extract_text()


class TestPDFProcessor(TestCase):
    def setUp(self):
        # Creating a fake PDF file content
        self.pdf_content = b"%PDF-1.4\n%..."
        self.pdf_file = SimpleUploadedFile("test.pdf", self.pdf_content)

    def test_extract_text(self):
        processor = PDFProcessor(self.pdf_file)

        # Mocking PyPDF2's PdfReader
        with patch("PyPDF2.PdfReader") as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Some PDF text"
            mock_reader.return_value.pages = [mock_page]
            
            text = processor.extract_text()
            
            self.assertEqual(text, "Some PDF text")
            mock_reader.assert_called_once_with(self.pdf_file)

    @patch("PyPDF2.PdfReader", side_effect=ImportError)
    def test_extract_text_import_error(self, mock_pdfreader):
        processor = PDFProcessor(self.pdf_file)
        text = processor.extract_text()
        self.assertIsNone(text)
        

class TestImageProcessor(TestCase):
    def setUp(self):
        # Creating a fake image file (simulated bytes for testing)
        self.image_content = BytesIO()
        self.image_content.write(b'\x89PNG\r\n\x1a\n')  # Fake PNG header
        self.image_content.seek(0)
        self.image_file = SimpleUploadedFile("test_image.png", self.image_content.read())

    def test_get_metadata_with_dimensions(self):
        processor = ImageProcessor(self.image_file)
        
        # Mocking _get_image_dimensions to return a tuple
        with patch.object(processor, "_get_image_dimensions", return_value=(800, 600)):
            metadata = processor.get_metadata()
            self.assertIn("dimensions", metadata)
            self.assertEqual(metadata["dimensions"], (800, 600))

    @patch("PIL.Image.open", side_effect=ImportError)
    def test_get_metadata_image_import_error(self, mock_image):
        processor = ImageProcessor(self.image_file)
        metadata = processor.get_metadata()
        self.assertNotIn("dimensions", metadata)
        
        
