import os
import logging
import tempfile
import uuid
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple, BinaryIO, Union
from pathlib import Path

import ffmpeg
import numpy as np
from PIL import Image
import librosa
import matplotlib.pyplot as plt
from django.core.files import File
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.utils import timezone

# Configure logging
logger = logging.getLogger(__name__)


class ProcessingError(Exception):
    """Base exception for all processing errors"""
    pass


class FileReadError(ProcessingError):
    """Exception raised when file can't be read"""
    pass


class FormatError(ProcessingError):
    """Exception raised when file format is invalid"""
    pass


class ProcessingFailedError(ProcessingError):
    """Exception raised when processing operation fails"""
    pass


class Processor(ABC):
    """
    Abstract base class for all media processors.
    
    This class defines the common interface and shared functionality
    for processing different types of media files in Django.
    """
    
    # Default supported file extensions
    SUPPORTED_EXTENSIONS = []
    
    def __init__(self, file_obj: Union[File, UploadedFile], 
                 output_dir: Optional[str] = None,
                 **kwargs):
        """
        Initialize the processor with a Django File object.
        
        Args:
            file_obj: Django File or UploadedFile object
            output_dir: Directory for processed output files (defaults to MEDIA_ROOT/processed)
            **kwargs: Additional processor-specific parameters
        """
        self.file_obj = file_obj
        self.filename = getattr(file_obj, 'name', str(uuid.uuid4()))
        self.file_extension = self._get_extension(self.filename)
        self.output_dir = output_dir or os.path.join(settings.MEDIA_ROOT, 'processed')
        self.temp_file = None
        self.processing_started = None
        self.processing_completed = None
        self.metadata = {}
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Validate file format
        self._validate_format()
        
        # Store additional parameters
        self.params = kwargs
        
        logger.debug(f"Initialized {self.__class__.__name__} for file: {self.filename}")
    
    def _get_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        return os.path.splitext(filename)[1].lower().lstrip('.')
    
    def _validate_format(self) -> None:
        """Validate if file extension is supported."""
        if self.SUPPORTED_EXTENSIONS and self.file_extension not in self.SUPPORTED_EXTENSIONS:
            supported = ', '.join(self.SUPPORTED_EXTENSIONS)
            raise FormatError(
                f"Unsupported file format: .{self.file_extension}. "
                f"Supported formats: {supported}"
            )
    
    def _prepare_file(self) -> str:
        """
        Prepare file for processing by creating a temporary file.
        
        Returns:
            Path to the temporary file
        """
        try:
            # Create a named temporary file with the correct extension
            suffix = f".{self.file_extension}"
            self.temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            
            # Write the file content to the temporary file
            if hasattr(self.file_obj, 'temporary_file_path'):
                # For TemporaryUploadedFile (large files)
                temp_path = self.file_obj.temporary_file_path()
                with open(temp_path, 'rb') as src:
                    with open(self.temp_file.name, 'wb') as dst:
                        for chunk in iter(lambda: src.read(4096), b''):
                            dst.write(chunk)
            else:
                # For InMemoryUploadedFile (small files) or regular File objects
                self.file_obj.seek(0)
                with open(self.temp_file.name, 'wb') as dst:
                    for chunk in self.file_obj.chunks():
                        dst.write(chunk)
            
            logger.debug(f"Prepared temporary file: {self.temp_file.name}")
            return self.temp_file.name
        
        except Exception as e:
            if self.temp_file and os.path.exists(self.temp_file.name):
                os.unlink(self.temp_file.name)
            logger.error(f"Error preparing file: {str(e)}")
            raise FileReadError(f"Failed to read file: {str(e)}")
    
    def _cleanup(self) -> None:
        """Clean up temporary files."""
        if self.temp_file and os.path.exists(self.temp_file.name):
            try:
                os.unlink(self.temp_file.name)
                logger.debug(f"Cleaned up temporary file: {self.temp_file.name}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {str(e)}")
    
    def generate_output_path(self, suffix: str = "", extension: Optional[str] = None) -> str:
        """
        Generate path for an output file.
        
        Args:
            suffix: String to append to the base filename
            extension: File extension for the output (defaults to input file extension)
            
        Returns:
            Full path to the output file
        """
        base = os.path.splitext(os.path.basename(self.filename))[0]
        ext = extension or self.file_extension
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        filename = f"{base}_{suffix}_{timestamp}.{ext}" if suffix else f"{base}_{timestamp}.{ext}"
        return os.path.join(self.output_dir, filename)
    
    def save_to_django_file(self, file_path: str, delete_after: bool = True) -> File:
        """
        Convert a processed file to a Django File object.
        
        Args:
            file_path: Path to the file to convert
            delete_after: Whether to delete the file after conversion
            
        Returns:
            Django File object
        """
        try:
            with open(file_path, 'rb') as f:
                name = os.path.basename(file_path)
                django_file = File(f, name=name)
                # Read the content to create a proper File object
                content = django_file.read()
                django_file.seek(0)
            
            if delete_after:
                os.unlink(file_path)
                
            return django_file
        except Exception as e:
            logger.error(f"Error converting to Django File: {str(e)}")
            raise ProcessingFailedError(f"Failed to create Django File: {str(e)}")
    
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from the file.
        
        Returns:
            Dictionary containing file metadata
        """
        try:
            file_path = self._prepare_file()
            result = ffmpeg.probe(file_path)
            self.metadata = {
                'format': result.get('format', {}),
                'streams': result.get('streams', []),
                'filename': self.filename,
                'file_size': result.get('format', {}).get('size', 0)
            }
            return self.metadata
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            raise ProcessingFailedError(f"Failed to extract metadata: {str(e)}")
        finally:
            self._cleanup()
    
    @abstractmethod
    def process(self, **kwargs) -> Any:
        """
        Process the file according to implementation in derived classes.
        
        Args:
            **kwargs: Processing options specific to the media type
            
        Returns:
            Result of the processing operation
        """
        self.processing_started = timezone.now()
        logger.info(f"Starting processing for {self.filename}")


class VideoProcessor(Processor):
    """
    Processor for video files with video-specific operations.
    """
    
    SUPPORTED_EXTENSIONS = ['mp4', 'avi', 'mov', 'mkv', 'webm']
    
    def __init__(self, file_obj: Union[File, UploadedFile], **kwargs):
        """
        Initialize the video processor.
        
        Args:
            file_obj: Django File or UploadedFile object
            **kwargs: Additional processor-specific parameters
        """
        super().__init__(file_obj, **kwargs)
        # Video-specific attributes
        self.resolution = None
        self.duration = None
        self.fps = None
    
    def process(self, **kwargs) -> Dict[str, Any]:
        """
        Generic processing method for video files.
        By default, extracts metadata and basic information.
        
        Args:
            **kwargs: Processing options
            
        Returns:
            Dictionary with processing results
        """
        super().process(**kwargs)
        
        try:
            metadata = self.extract_metadata()
            
            # Extract video-specific information
            video_stream = next((s for s in metadata['streams'] if s.get('codec_type') == 'video'), None)
            if video_stream:
                self.resolution = (
                    int(video_stream.get('width', 0)), 
                    int(video_stream.get('height', 0))
                )
                self.fps = eval(video_stream.get('r_frame_rate', '0/1'))
            
            # Extract duration
            self.duration = float(metadata['format'].get('duration', 0))
            
            result = {
                'metadata': metadata,
                'duration': self.duration,
                'resolution': self.resolution,
                'fps': self.fps
            }
            
            self.processing_completed = timezone.now()
            logger.info(f"Completed basic video processing for {self.filename}")
            return result
            
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            raise ProcessingFailedError(f"Failed to process video: {str(e)}")
        finally:
            self._cleanup()
    
    def extract_frame(self, time_position: float) -> File:
        """
        Extract a frame at the specified time position.
        
        Args:
            time_position: Time in seconds
            
        Returns:
            Django File object containing the extracted frame
        """
        logger.info(f"Extracting frame at {time_position}s from {self.filename}")
        output_path = self.generate_output_path(f"frame_{int(time_position)}", "jpg")
        
        try:
            file_path = self._prepare_file()
            
            # Extract frame using ffmpeg
            (
                ffmpeg
                .input(file_path, ss=time_position)
                .output(output_path, vframes=1)
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.debug(f"Frame extracted to {output_path}")
            return self.save_to_django_file(output_path)
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {str(e)}")
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise ProcessingFailedError(f"Failed to extract frame: {str(e)}")
        finally:
            self._cleanup()
    
    def extract_frames(self, 
                      interval: float = 1.0, 
                      max_frames: Optional[int] = None,
                      resize: Optional[Tuple[int, int]] = None) -> List[File]:
        """
        Extract multiple frames at regular intervals.
        
        Args:
            interval: Time interval between frames in seconds
            max_frames: Maximum number of frames to extract
            resize: Optional tuple of (width, height) to resize frames
            
        Returns:
            List of Django File objects containing extracted frames
        """
        logger.info(f"Extracting frames at {interval}s intervals from {self.filename}")
        
        try:
            # Extract metadata if not already done
            if not self.metadata:
                self.extract_metadata()
            
            if not self.duration:
                video_stream = next((s for s in self.metadata['streams'] if s.get('codec_type') == 'video'), None)
                self.duration = float(self.metadata['format'].get('duration', 0))
            
            # Calculate frame positions
            frame_positions = np.arange(0, self.duration, interval)
            if max_frames and len(frame_positions) > max_frames:
                frame_positions = frame_positions[:max_frames]
            
            frames = []
            for pos in frame_positions:
                frame = self.extract_frame(pos)
                
                # Resize if requested
                if resize and frame:
                    # Need to process image with PIL
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp:
                        temp_path = temp.name
                        with open(temp_path, 'wb') as f:
                            frame.seek(0)
                            f.write(frame.read())
                    
                    # Resize with PIL
                    with Image.open(temp_path) as img:
                        img = img.resize(resize)
                        img.save(temp_path)
                    
                    # Convert back to Django file
                    frame = self.save_to_django_file(temp_path)
                
                frames.append(frame)
            
            logger.info(f"Extracted {len(frames)} frames from {self.filename}")
            return frames
            
        except Exception as e:
            logger.error(f"Multiple frame extraction failed: {str(e)}")
            raise ProcessingFailedError(f"Failed to extract frames: {str(e)}")
        finally:
            self._cleanup()
    
    def compress_video(self, 
                       target_size_mb: float = 10.0,
                       preset: str = 'medium') -> File:
        """
        Compress a video to target file size.
        
        Args:
            target_size_mb: Target size in megabytes
            preset: FFmpeg compression preset (slower = better quality)
            
        Returns:
            Django File object containing the compressed video
        """
        logger.info(f"Compressing video {self.filename} to {target_size_mb}MB")
        output_path = self.generate_output_path("compressed", self.file_extension)
        
        try:
            file_path = self._prepare_file()
            
            # Extract metadata if not already done
            if not self.metadata:
                self.extract_metadata()
            
            # Calculate target bitrate based on duration and target size
            if not self.duration:
                self.duration = float(self.metadata['format'].get('duration', 0))
            
            # Convert MB to bits (1MB = 8,000,000 bits)
            target_size_bits = target_size_mb * 8 * 1000 * 1000
            bitrate = int(target_size_bits / self.duration)
            
            # Compress using ffmpeg
            (
                ffmpeg
                .input(file_path)
                .output(output_path, 
                        **{'b:v': f"{bitrate}", 'preset': preset})
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.debug(f"Video compressed to {output_path}")
            return self.save_to_django_file(output_path)
            
        except Exception as e:
            logger.error(f"Video compression failed: {str(e)}")
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise ProcessingFailedError(f"Failed to compress video: {str(e)}")
        finally:
            self._cleanup()
    
    def create_thumbnail(self, 
                        time_position: Optional[float] = None, 
                        size: Tuple[int, int] = (320, 180)) -> File:
        """
        Create a thumbnail from the video.
        
        Args:
            time_position: Time position in seconds (defaults to 10% of duration)
            size: Thumbnail dimensions as (width, height)
            
        Returns:
            Django File object containing the thumbnail
        """
        try:
            # Extract metadata if not already done
            if not self.metadata:
                self.extract_metadata()
            
            if not self.duration:
                self.duration = float(self.metadata['format'].get('duration', 0))
            
            # Default to 10% of the video duration if time_position not specified
            if time_position is None:
                time_position = self.duration * 0.1
            
            logger.info(f"Creating thumbnail at {time_position}s from {self.filename}")
            output_path = self.generate_output_path("thumbnail", "jpg")
            
            file_path = self._prepare_file()
            
            # Create thumbnail using ffmpeg
            (
                ffmpeg
                .input(file_path, ss=time_position)
                .filter('scale', size[0], size[1])
                .output(output_path, vframes=1)
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.debug(f"Thumbnail created at {output_path}")
            return self.save_to_django_file(output_path)
            
        except Exception as e:
            logger.error(f"Thumbnail creation failed: {str(e)}")
            raise ProcessingFailedError(f"Failed to create thumbnail: {str(e)}")
        finally:
            self._cleanup()


class AudioProcessor(Processor):
    """
    Processor for audio files with audio-specific operations.
    """
    
    SUPPORTED_EXTENSIONS = ['mp3', 'wav', 'ogg', 'flac', 'm4a']
    
    def __init__(self, file_obj: Union[File, UploadedFile], **kwargs):
        """
        Initialize the audio processor.
        
        Args:
            file_obj: Django File or UploadedFile object
            **kwargs: Additional processor-specific parameters
        """
        super().__init__(file_obj, **kwargs)
        # Audio-specific attributes
        self.duration = None
        self.sample_rate = None
        self.channels = None
    
    def process(self, **kwargs) -> Dict[str, Any]:
        """
        Generic processing method for audio files.
        By default, extracts metadata and basic information.
        
        Args:
            **kwargs: Processing options
            
        Returns:
            Dictionary with processing results
        """
        super().process(**kwargs)
        
        try:
            metadata = self.extract_metadata()
            
            # Extract audio-specific information
            audio_stream = next((s for s in metadata['streams'] if s.get('codec_type') == 'audio'), None)
            if audio_stream:
                self.sample_rate = int(audio_stream.get('sample_rate', 0))
                self.channels = int(audio_stream.get('channels', 0))
            
            # Extract duration
            self.duration = float(metadata['format'].get('duration', 0))
            
            result = {
                'metadata': metadata,
                'duration': self.duration,
                'sample_rate': self.sample_rate,
                'channels': self.channels
            }
            
            self.processing_completed = timezone.now()
            logger.info(f"Completed basic audio processing for {self.filename}")
            return result
            
        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            raise ProcessingFailedError(f"Failed to process audio: {str(e)}")
        finally:
            self._cleanup()
    
    def generate_waveform(self, 
                         width: int = 1000, 
                         height: int = 200,
                         color: str = '#3498db') -> File:
        """
        Generate a waveform image from the audio file.
        
        Args:
            width: Width of the waveform image
            height: Height of the waveform image
            color: Color of the waveform in hex format
            
        Returns:
            Django File object containing the waveform image
        """
        logger.info(f"Generating waveform for {self.filename}")
        output_path = self.generate_output_path("waveform", "png")
        
        try:
            file_path = self._prepare_file()
            
            # Load audio using librosa
            y, sr = librosa.load(file_path, sr=None)
            
            # Set up the figure with the specified dimensions
            plt.figure(figsize=(width/100, height/100), dpi=100)
            plt.axis('off')  # Hide the axes
            
            # Plot the waveform
            plt.plot(np.linspace(0, len(y)/sr, len(y)), y, color=color)
            
            # Adjust limits
            plt.ylim(-1, 1)
            plt.tight_layout(pad=0)
            
            # Save the figure
            plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
            plt.close()
            
            logger.debug(f"Waveform generated at {output_path}")
            return self.save_to_django_file(output_path)
            
        except Exception as e:
            logger.error(f"Waveform generation failed: {str(e)}")
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise ProcessingFailedError(f"Failed to generate waveform: {str(e)}")
        finally:
            self._cleanup()
    
    def generate_spectrogram(self, 
                            width: int = 1000, 
                            height: int = 500) -> File:
        """
        Generate a spectrogram image from the audio file.
        
        Args:
            width: Width of the spectrogram image
            height: Height of the spectrogram image
            
        Returns:
            Django File object containing the spectrogram image
        """
        logger.info(f"Generating spectrogram for {self.filename}")
        output_path = self.generate_output_path("spectrogram", "png")
        
        try:
            file_path = self._prepare_file()
            
            # Load audio using librosa
            y, sr = librosa.load(file_path, sr=None)
            
            # Set up the figure with the specified dimensions
            plt.figure(figsize=(width/100, height/100), dpi=100)
            plt.axis('off')  # Hide the axes
            
            # Compute and display the spectrogram
            S = librosa.feature.melspectrogram(y=y, sr=sr)
            S_dB = librosa.power_to_db(S, ref=np.max)
            librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel')
            
            # Save the figure
            plt.tight_layout(pad=0)
            plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
            plt.close()
            
            logger.debug(f"Spectrogram generated at {output_path}")
            return self.save_to_django_file(output_path)
            
        except Exception as e:
            logger.error(f"Spectrogram generation failed: {str(e)}")
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise ProcessingFailedError(f"Failed to generate spectrogram: {str(e)}")
        finally:
            self._cleanup()
    
    def convert_format(self, target_format: str, quality: str = 'high') -> File:
        """
        Convert audio to a different format.
        
        Args:
            target_format: Target audio format (e.g., 'mp3', 'wav')
            quality: Quality level ('low', 'medium', 'high')
            
        Returns:
            Django File object containing the converted audio
        """
        if target_format not in self.SUPPORTED_EXTENSIONS:
            raise FormatError(f"Unsupported target format: {target_format}")
        
        logger.info(f"Converting {self.filename} to {target_format}")
        output_path = self.generate_output_path("converted", target_format)
        
        try:
            file_path = self._prepare_file()
            
            # Define quality settings
            quality_settings = {
                'low': {'audio_bitrate': '64k'},
                'medium': {'audio_bitrate': '128k'},
                'high': {'audio_bitrate': '256k'}
            }
            
            settings = quality_settings.get(quality, quality_settings['medium'])
            
            # Convert using ffmpeg
            (
                ffmpeg
                .input(file_path)
                .output(output_path, **settings)
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.debug(f"Audio converted to {output_path}")
            return self.save_to_django_file(output_path)
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {str(e)}")
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise ProcessingFailedError(f"Failed to convert audio: {str(e)}")
        finally:
            self._cleanup()
    
    def trim_audio(self, start_time: float, end_time: float) -> File:
        """
        Trim audio to the specified time range.
        
        Args:
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Django File object containing the trimmed audio
        """
        logger.info(f"Trimming {self.filename} from {start_time}s to {end_time}s")
        output_path = self.generate_output_path("trimmed", self.file_extension)
        
        try:
            file_path = self._prepare_file()
            
            # Extract metadata if not already done
            if not self.metadata:
                self.extract_metadata()
            
            if not self.duration:
                self.duration = float(self.metadata['format'].get('duration', 0))
            
            # Validate time range
            if start_time < 0 or end_time > self.duration or start_time >= end_time:
                raise ValueError(f"Invalid time range: {start_time}s - {end_time}s")
            
            # Trim using ffmpeg
            (
                ffmpeg
                .input(file_path, ss=start_time, to=end_time)
                .output(output_path, c='copy')
                .overwrite_output()
                .run(quiet=True)
            )
            
            logger.debug(f"Audio trimmed to {output_path}")
            return self.save_to_django_file(output_path)
            
        except Exception as e:
            logger.error(f"Audio trimming failed: {str(e)}")
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise ProcessingFailedError(f"Failed to trim audio: {str(e)}")
        finally:
            self._cleanup()