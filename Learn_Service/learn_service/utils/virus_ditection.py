"""
Security Validators for File Uploads

This module extends the file validation system with security-focused validators to detect
malicious content, viruses, and potentially harmful features in uploaded files.
"""

# import os
# import io
# import re
# import zipfile
# import tempfile
# import subprocess
# import logging
# from typing import List, Dict, Set, Optional, Union, Any
# from django.core.files.uploadedfile import UploadedFile

# # Configure logging
# logger = logging.getLogger(__name__)


# class SecurityValidator:
#     """Base class for security validators that can be added to AbstractFileValidator."""
    
#     def validate(self, file_obj: UploadedFile) -> None:
#         """
#         Validate the file for security threats.
        
#         Args:
#             file_obj: The uploaded file object
            
#         Raises:
#             FileValidationError: If security validation fails
#         """
#         raise NotImplementedError("Subclasses must implement validate method")


# class AntivirusValidator(SecurityValidator):
#     """
#     Validator that scans files for viruses using ClamAV.
    
#     Requires ClamAV daemon to be running on the system.
#     """
    
#     def __init__(
#         self,
#         clamd_socket: str = '/var/run/clamav/clamd.sock',
#         use_pyclamd: bool = True,
#         fallback_to_command: bool = True,
#         clamd_timeout: int = 30
#     ):
#         """
#         Initialize antivirus validator.
        
#         Args:
#             clamd_socket: Path to ClamAV daemon socket
#             use_pyclamd: Whether to use pyclamd library (if available)
#             fallback_to_command: Whether to fall back to command line if pyclamd fails
#             clamd_timeout: Timeout for ClamAV scan in seconds
#         """
#         self.clamd_socket = clamd_socket
#         self.use_pyclamd = use_pyclamd
#         self.fallback_to_command = fallback_to_command
#         self.clamd_timeout = clamd_timeout
        
#         # Try to import pyclamd if requested
#         self.pyclamd = None
#         if use_pyclamd:
#             try:
#                 import pyclamd
#                 self.pyclamd = pyclamd
#             except ImportError:
#                 logger.warning("pyclamd not installed, falling back to command line")
    
#     def validate(self, file_obj: UploadedFile) -> None:
#         """Scan file for viruses using ClamAV."""
#         from django.core.exceptions import ValidationError
        
#         # Try pyclamd method first if available
#         if self.pyclamd and self.use_pyclamd:
#             try:
#                 # Initialize ClamAV daemon
#                 cd = self.pyclamd.ClamdUnixSocket(filename=self.clamd_socket)
                
#                 # Make sure the daemon is available
#                 if not cd.ping():
#                     logger.warning("ClamAV daemon is not responding")
#                     if not self.fallback_to_command:
#                         raise ValidationError("Antivirus service is not available")
#                 else:
#                     # Scan the file
#                     file_obj.seek(0)
#                     file_content = file_obj.read()
#                     file_obj.seek(0)
                    
#                     # Create a temporary file for scanning
#                     with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#                         temp_file.write(file_content)
#                         temp_path = temp_file.name
                    
#                     try:
#                         scan_result = cd.scan_file(temp_path)
#                         if scan_result:
#                             # If scan_result is not None, a virus was found
#                             virus_name = scan_result[temp_path][1]
#                             raise ValidationError(f"Virus detected: {virus_name}")
#                     finally:
#                         # Clean up temporary file
#                         try:
#                             os.unlink(temp_path)
#                         except:
#                             pass
                    
#                     return
#             except Exception as e:
#                 logger.error(f"Error using pyclamd: {str(e)}")
#                 if not self.fallback_to_command:
#                     raise ValidationError(f"Antivirus scan failed: {str(e)}")
        
#         # Fall back to command line
#         if not self.pyclamd or self.fallback_to_command:
#             try:
#                 # Create a temporary file for scanning
#                 file_obj.seek(0)
#                 with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#                     temp_file.write(file_obj.read())
#                     temp_path = temp_file.name
#                 file_obj.seek(0)
                
#                 try:
#                     # Run ClamAV scan on the temporary file
#                     result = subprocess.run(
#                         ['clamscan', '--no-summary', temp_path],
#                         capture_output=True,
#                         text=True,
#                         timeout=self.clamd_timeout
#                     )
                    
#                     # Check if a virus was found
#                     if result.returncode == 1:
#                         # Extract virus name from output
#                         output = result.stdout
#                         virus_match = re.search(r'.*: (.*) FOUND', output)
#                         virus_name = virus_match.group(1) if virus_match else "Unknown"
#                         raise ValidationError(f"Virus detected: {virus_name}")
                        
#                     # Check for other errors
#                     if result.returncode > 1:
#                         logger.error(f"ClamAV scan failed with code {result.returncode}: {result.stderr}")
#                         raise ValidationError("Antivirus scan failed")
#                 finally:
#                     # Clean up temporary file
#                     try:
#                         os.unlink(temp_path)
#                     except:
#                         pass
#             except subprocess.TimeoutExpired:
#                 raise ValidationError("Antivirus scan timed out")
#             except Exception as e:
#                 logger.error(f"Error running ClamAV: {str(e)}")
#                 raise ValidationError(f"Antivirus scan failed: {str(e)}")


# class ExecutableContentValidator(SecurityValidator):
#     """Validator that checks for executable content in files."""
    
#     def __init__(
#         self,
#         block_executable_content: bool = True,
#         block_scripts: bool = True,
#         block_macro_enabled: bool = True,
#         suspect_extensions: Optional[List[str]] = None,
#         suspect_mime_patterns: Optional[List[str]] = None
#     ):
#         """
#         Initialize executable content validator.
        
#         Args:
#             block_executable_content: Whether to block executable files
#             block_scripts: Whether to block script files
#             block_macro_enabled: Whether to block Office files with macros
#             suspect_extensions: List of suspicious file extensions to block
#             suspect_mime_patterns: List of suspicious MIME type patterns to block
#         """
#         self.block_executable_content = block_executable_content
#         self.block_scripts = block_scripts
#         self.block_macro_enabled = block_macro_enabled
        
#         # Default suspicious extensions
#         self.suspect_extensions = suspect_extensions or [
#             'exe', 'dll', 'bat', 'cmd', 'ps1', 'vbs', 'js', 'jar', 'msi',
#             'com', 'scr', 'hta', 'cpl', 'msc', 'reg', 'vb', 'vbe', 'ws', 'wsf',
#             'msh', 'msh1', 'msh2', 'psc1', 'psc2'
#         ]
        
#         # Default suspicious MIME patterns
#         self.suspect_mime_patterns = suspect_mime_patterns or [
#             r'application/x-executable',
#             r'application/x-msdownload',
#             r'application/x-dosexec',
#             r'application/x-msdos-program',
#             r'application/x-ms-shortcut',
#             r'application/x-msi',
#             r'application/x-script',
#             r'application/vbs',
#             r'application/javascript'
#         ]
        
#         # Compile regex patterns
#         self.mime_patterns = [re.compile(pattern) for pattern in self.suspect_mime_patterns]
    
#     def validate(self, file_obj: UploadedFile) -> None:
#         """Check file for executable content."""
#         from django.core.exceptions import ValidationError
        
#         # Check file extension
#         if self.block_executable_content:
#             file_ext = os.path.splitext(file_obj.name)[1].lower().lstrip('.')
#             if file_ext in self.suspect_extensions:
#                 raise ValidationError(f"File type '{file_ext}' is not allowed due to security restrictions")
        
#         # Check MIME type using python-magic
#         try:
#             import magic
#             file_obj.seek(0)
#             file_content = file_obj.read(2048)  # Read first 2KB for MIME detection
#             file_obj.seek(0)
            
#             mime_magic = magic.Magic(mime=True)
#             detected_mime = mime_magic.from_buffer(file_content)
            
#             # Check against suspicious MIME patterns
#             for pattern in self.mime_patterns:
#                 if pattern.match(detected_mime):
#                     raise ValidationError(f"File with MIME type '{detected_mime}' is not allowed due to security restrictions")
#         except ImportError:
#             logger.warning("python-magic not installed, skipping MIME type security check")
        
#         # Check for Office files with macros
#         if self.block_macro_enabled:
#             file_ext = os.path.splitext(file_obj.name)[1].lower()
#             if file_ext in ['.docm', '.xlsm', '.pptm', '.dotm', '.xltm', '.potm']:
#                 raise ValidationError("Office files with macros are not allowed due to security restrictions")
            
#             # Check if .docx, .xlsx, etc. files contain macros (VBA)
#             if file_ext in ['.docx', '.xlsx', '.pptx']:
#                 try:
#                     file_obj.seek(0)
#                     with zipfile.ZipFile(file_obj, 'r') as zip_ref:
#                         file_list = zip_ref.namelist()
#                         # Check for VBA content
#                         if any('vbaProject.bin' in f for f in file_list):
#                             raise ValidationError("Office file contains macros, which are not allowed due to security restrictions")
#                 except zipfile.BadZipFile:
#                     # If not a valid ZIP file, it's not a valid Office file either
#                     raise ValidationError("Invalid Office file format")
#                 finally:
#                     file_obj.seek(0)


# class ArchiveContentValidator(SecurityValidator):
#     """Validator that checks archive files for suspicious content."""
    
#     def __init__(
#         self,
#         max_depth: int = 5,
#         max_files: int = 100,
#         max_size_ratio: float = 10.0,
#         block_nested_archives: bool = True,
#         block_suspicious_extensions: bool = True,
#         suspicious_extensions: Optional[List[str]] = None
#     ):
#         """
#         Initialize archive content validator.
        
#         Args:
#             max_depth: Maximum recursion depth for nested archives
#             max_files: Maximum number of files allowed in archive
#             max_size_ratio: Maximum ratio of uncompressed to compressed size
#             block_nested_archives: Whether to block archives containing other archives
#             block_suspicious_extensions: Whether to block archives with suspicious files
#             suspicious_extensions: List of suspicious file extensions to block
#         """
#         self.max_depth = max_depth
#         self.max_files = max_files
#         self.max_size_ratio = max_size_ratio
#         self.block_nested_archives = block_nested_archives
#         self.block_suspicious_extensions = block_suspicious_extensions
        
#         # Default suspicious extensions
#         self.suspicious_extensions = suspicious_extensions or [
#             'exe', 'dll', 'bat', 'cmd', 'ps1', 'vbs', 'js', 'jar', 'msi',
#             'com', 'scr', 'hta', 'cpl', 'msc', 'reg', 'vb', 'vbe', 'ws', 'wsf',
#             'msh', 'msh1', 'msh2', 'psc1', 'psc2'
#         ]
    
#     def validate(self, file_obj: UploadedFile) -> None:
#         """Check archive file for suspicious content."""
#         from django.core.exceptions import ValidationError
        
#         file_ext = os.path.splitext(file_obj.name)[1].lower().lstrip('.')
        
#         # Only process archive files
#         if file_ext not in ['zip', 'tar', 'gz', 'tgz', 'bz2', 'tbz2', '7z', 'rar']:
#             return
        
#         # Process ZIP files
#         if file_ext == 'zip':
#             try:
#                 file_obj.seek(0)
#                 with zipfile.ZipFile(file_obj, 'r') as zip_ref:
#                     # Check number of files
#                     file_list = zip_ref.namelist()
#                     if len(file_list) > self.max_files:
#                         raise ValidationError(f"Archive contains {len(file_list)} files, exceeding maximum of {self.max_files}")
                    
#                     # Check for suspicious extensions
#                     if self.block_suspicious_extensions:
#                         for file_path in file_list:
#                             file_name = os.path.basename(file_path)
#                             if file_name:  # Ignore directories
#                                 suspect_ext = os.path.splitext(file_name)[1].lower().lstrip('.')
#                                 if suspect_ext in self.suspicious_extensions:
#                                     raise ValidationError(f"Archive contains potentially harmful file: {file_name}")
                    
#                     # Check for nested archives
#                     if self.block_nested_archives:
#                         archive_extensions = ['zip', 'tar', 'gz', 'tgz', 'bz2', 'tbz2', '7z', 'rar']
#                         for file_path in file_list:
#                             file_name = os.path.basename(file_path)
#                             if file_name:  # Ignore directories
#                                 nested_ext = os.path.splitext(file_name)[1].lower().lstrip('.')
#                                 if nested_ext in archive_extensions:
#                                     raise ValidationError(f"Archive contains nested archive: {file_name}, which is not allowed")
                    
#                     # Check compression ratio (protection against zip bombs)
#                     try:
#                         compressed_size = file_obj.size
#                         uncompressed_size = sum(zip_info.file_size for zip_info in zip_ref.infolist())
                        
#                         if compressed_size > 0 and uncompressed_size / compressed_size > self.max_size_ratio:
#                             raise ValidationError(
#                                 f"Archive has suspicious compression ratio ({uncompressed_size / compressed_size:.1f}), "
#                                 f"exceeding maximum ratio of {self.max_size_ratio}"
#                             )
#                     except Exception as e:
#                         logger.warning(f"Failed to check compression ratio: {str(e)}")
            
#             except zipfile.BadZipFile:
#                 raise ValidationError("Invalid or corrupted ZIP file")
#             finally:
#                 file_obj.seek(0)
        
#         # For other archive types, we would need to use external tools like libarchive
#         # or command-line utilities like tar, unrar, etc.
#         # This is left as an extension point


# class DeepScanSecurityValidator(SecurityValidator):
#     """
#     Deep scan validator that uses multiple security tools and techniques.
    
#     This validator combines multiple security checks and can use external tools.
#     """
    
#     def __init__(
#         self,
#         use_yara: bool = True,
#         yara_rules_path: Optional[str] = None,
#         use_sandbox: bool = False,
#         sandbox_timeout: int = 60,
#         check_file_entropy: bool = True,
#         high_entropy_threshold: float = 7.0,
#         check_metadata: bool = True
#     ):
#         """
#         Initialize deep scan security validator.
        
#         Args:
#             use_yara: Whether to use YARA rules for scanning
#             yara_rules_path: Path to YARA rules directory
#             use_sandbox: Whether to use sandbox execution (requires external setup)
#             sandbox_timeout: Timeout for sandbox execution in seconds
#             check_file_entropy: Whether to check file entropy
#             high_entropy_threshold: Threshold for high entropy (7.0-8.0 is suspicious)
#             check_metadata: Whether to check file metadata
#         """
#         self.use_yara = use_yara
#         self.yara_rules_path = yara_rules_path
#         self.use_sandbox = use_sandbox
#         self.sandbox_timeout = sandbox_timeout
#         self.check_file_entropy = check_file_entropy
#         self.high_entropy_threshold = high_entropy_threshold
#         self.check_metadata = check_metadata
        
#         # Initialize YARA if requested
#         self.yara = None
#         if use_yara:
#             try:
#                 import yara
#                 self.yara = yara
                
#                 # Compile YARA rules if path is provided
#                 self.yara_rules = None
#                 if yara_rules_path and os.path.isdir(yara_rules_path):
#                     try:
#                         self.yara_rules = yara.compile(filepaths={
#                             os.path.splitext(rule)[0]: os.path.join(yara_rules_path, rule)
#                             for rule in os.listdir(yara_rules_path)
#                             if rule.endswith('.yar') or rule.endswith('.yara')
#                         })
#                     except Exception as e:
#                         logger.error(f"Failed to compile YARA rules: {str(e)}")
#             except ImportError:
#                 logger.warning("yara-python not installed, YARA scanning will be disabled")
    
#     def validate(self, file_obj: UploadedFile) -> None:
#         """Perform deep security scan on file."""
#         from django.core.exceptions import ValidationError
        
#         # YARA scanning
#         if self.use_yara and self.yara and self.yara_rules:
#             try:
#                 file_obj.seek(0)
#                 file_content = file_obj.read()
#                 file_obj.seek(0)
                
#                 # Scan with YARA rules
#                 matches = self.yara_rules.match(data=file_content)
#                 if matches:
#                     rule_names = [match.rule for match in matches]
#                     raise ValidationError(f"File matched security rules: {', '.join(rule_names)}")
#             except Exception as e:
#                 logger.error(f"YARA scan failed: {str(e)}")
        
#         # Entropy check (detect encrypted/obfuscated content)
#         if self.check_file_entropy:
#             try:
#                 import math
                
#                 file_obj.seek(0)
#                 data = file_obj.read()
#                 file_obj.seek(0)
                
#                 if len(data) > 0:
#                     # Calculate Shannon entropy
#                     entropy = 0
#                     byte_counts = {}
#                     for byte in data:
#                         byte_counts[byte] = byte_counts.get(byte, 0) + 1
                    
#                     for count in byte_counts.values():
#                         probability = count / len(data)
#                         entropy -= probability * math.log2(probability)
                    
#                     # High entropy could indicate encrypted/compressed/obfuscated data
#                     if entropy > self.high_entropy_threshold:
#                         logger.warning(f"File has high entropy: {entropy:.2f}")
#                         # This is just a warning, not necessarily an error
#                         # raise ValidationError(f"File has suspiciously high entropy ({entropy:.2f}), possible encrypted or obfuscated content")
#             except Exception as e:
#                 logger.error(f"Entropy check failed: {str(e)}")
        
#         # Metadata check
#         if self.check_metadata:
#             try:
#                 import exifread
                
#                 file_obj.seek(0)
#                 tags = exifread.process_file(file_obj, details=False)
#                 file_obj.seek(0)
                
#                 # Look for suspicious metadata
#                 suspicious_tags = []
#                 for tag, value in tags.items():
#                     # Check for script-like content in EXIF data
#                     if any(script_indicator in str(value).lower() for script_indicator in 
#                            ['script', 'eval(', 'exec(', '<script', 'function(', 'javascript:']):
#                         suspicious_tags.append(tag)
                
#                 if suspicious_tags:
#                     raise ValidationError(f"File contains suspicious metadata in tags: {', '.join(suspicious_tags)}")
#             except ImportError:
#                 logger.warning("exifread not installed, metadata check disabled")
#             except Exception as e:
#                 logger.error(f"Metadata check failed: {str(e)}")
        
#         # Sandbox execution (would require external setup)
#         if self.use_sandbox:
#             # This is a placeholder for integration with external sandboxing solutions
#             # like Cuckoo Sandbox, CAPE, or cloud services like VirusTotal
#             logger.warning("Sandbox analysis is configured but not implemented")


# class PolyglotFileValidator(SecurityValidator):
#     """
#     Validator that checks for polyglot files that could be interpreted in multiple ways.
    
#     Polyglot files can bypass security checks by appearing as one file type while
#     containing executable code in another format.
#     """
    
#     def __init__(self):
#         """Initialize polyglot file validator."""
#         pass
    
#     def validate(self, file_obj: UploadedFile) -> None:
#         """Check for polyglot file characteristics."""
#         from django.core.exceptions import ValidationError
        
#         file_obj.seek(0)
#         header = file_obj.read(256)  # Read first 256 bytes for signatures
#         file_obj.seek(0)
        
#         # Check for known polyglot patterns
        
#         # PDF/PE polyglot
#         if b'%PDF' in header and b'MZ' in header:
#             raise ValidationError("Detected potential PDF/PE polyglot file")
        
#         # JPG/JAR polyglot
#         if header.startswith(b'\xff\xd8') and b'PK\x03\x04' in header:
#             raise ValidationError("Detected potential JPG/JAR polyglot file")
        
#         # GIF/JS polyglot
#         if header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
#             if b'<script' in header or b'eval(' in header:
#                 raise ValidationError("Detected potential GIF/JavaScript polyglot file")
        
#         # Check for common file signature mismatches
#         file_ext = os.path.splitext(file_obj.name)[1].lower()
        
#         # JPG should start with FF D8
#         if file_ext == '.jpg' or file_ext == '.jpeg':
#             if not header.startswith(b'\xff\xd8'):
#                 raise ValidationError("JPG file has invalid signature")
        
#         # PNG should start with 89 50 4E 47
#         elif file_ext == '.png':
#             if not header.startswith(b'\x89PNG'):
#                 raise ValidationError("PNG file has invalid signature")
        
#         # GIF should start with GIF87a or GIF89a
#         elif file_ext == '.gif':
#             if not (header.startswith(b'GIF87a') or header.startswith(b'GIF89a')):
#                 raise ValidationError("GIF file has invalid signature")
        
#         # PDF should start with %PDF
#         elif file_ext == '.pdf':
#             if not b'%PDF' in header[:10]:
#                 raise ValidationError("PDF file has invalid signature")


# # Update AbstractFileValidator to incorporate security validators
# def extend_abstract_file_validator():
    """
    Add this code to the AbstractFileValidator class to incorporate security validators.
    
    Example:
    ```python
    class AbstractFileValidator(ABC):
        def __init__(self, ..., security_validators=None):
            # Existing initialization code...
            self.security_validators = security_validators or []
            
        def validate(self, file_obj: UploadedFile) -> None:
            # Run security validators first
            for validator in self.security_validators:
                validator.validate(file_obj)
                
            # Continue with regular validation...
            # ...
    ```
    """
#     pass


# # Example usage:
# def create_secure_pdf_validator():
    """Example of creating a secure PDF validator with security checks."""
    # from file_validation import PDFValidator, AbstractFileValidator
    
    # # Create security validators
    # antivirus = AntivirusValidator()
    # executable_check = ExecutableContentValidator()
    # polyglot_check = PolyglotFileValidator()
    
    # # Create PDF validator with security validators
    # pdf_validator = PDFValidator(
    #     max_size_mb=10,
    #     max_pages=100,
    #     allow_javascript=False,
    #     security_validators=[antivirus, executable_check, polyglot_check]
    # )
    
    # return pdf_validator