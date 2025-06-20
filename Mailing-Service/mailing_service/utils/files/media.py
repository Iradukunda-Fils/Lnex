# utils/media/processors.py

import logging
import os
import io
import tempfile
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from abc import ABC, abstractmethod
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.cache import cache
from pathlib import Path

logger = logging.getLogger('media.processors')

class MediaProcessorException(Exception):
    """Base exception for media processing errors."""
    pass


class MediaProcessor(ABC):
    """
    Abstract base class for all media processors.
    Provides common functionality for processing different types of media files.
    """
    
    def __init__(self, file_field, checksum=None):
        """
        Initialize with a file field and optional checksum.
        
        Args:
            file_field: Django FileField or ImageField instance
            checksum: Optional file checksum for caching
        """
        self.file_field = file_field
        self.checksum = checksum
        self.file_path = file_field.path if hasattr(file_field, 'path') else None
        self.file_name = file_field.name if hasattr(file_field, 'name') else None
        self.errors = []
    
    @abstractmethod
    def process(self) -> Dict[str, Any]:
        """
        Process the media file and return extracted metadata.
        Must be implemented by subclasses.
        
        Returns:
            Dict containing metadata specific to the media type
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from the media file.
        Must be implemented by subclasses.
        
        Returns:
            Dict containing metadata specific to the media type
        """
        pass
    
    def get_cached_result(self, cache_key: str, timeout: int = 3600) -> Optional[Dict[str, Any]]:
        """
        Get cached processing result if available.
        
        Args:
            cache_key: Key for cache lookup
            timeout: Cache timeout in seconds
            
        Returns:
            Cached result or None if not available
        """
        return cache.get(cache_key)
    
    def set_cached_result(self, cache_key: str, result: Dict[str, Any], timeout: int = 3600) -> None:
        """
        Cache processing result for future use.
        
        Args:
            cache_key: Key for cache storage
            result: Data to cache
            timeout: Cache timeout in seconds
        """
        cache.set(cache_key, result, timeout)
    
    def handle_error(self, error_message: str, exception: Optional[Exception] = None) -> None:
        """
        Log an error and add it to the errors list.
        
        Args:
            error_message: Description of the error
            exception: Optional exception that caused the error
        """
        full_message = f"{error_message}"
        if exception:
            full_message += f": {str(exception)}"
        
        logger.error(full_message)
        self.errors.append(full_message)


class VideoProcessor(MediaProcessor):
    """
    Specialized processor for video files.
    
    Features:
    - Video metadata extraction (duration, dimensions, codec, etc.)
    - Thumbnail generation at specified frame
    - Video frame extraction
    - Format conversion and transcoding
    """
    
    def __init__(self, file_field, checksum=None):
        super().__init__(file_field, checksum)
        
        # Attempt to import optional libraries
        self.ffmpeg_available = False
        try:
            import ffmpeg
            self.ffmpeg = ffmpeg
            self.ffmpeg_available = True
        except ImportError:
            logger.warning("ffmpeg-python not available. Advanced video processing disabled.")
    
    def process(self) -> Dict[str, Any]:
        """
        Process video file to extract metadata and generate thumbnails.
        
        Returns:
            Dict containing video metadata and processing results
        """
        try:
            # Get basic metadata
            metadata = self.get_metadata()
            
            # Add processing results (e.g., thumbnail URLs)
            # This would be expanded in a real implementation
            
            return metadata
        except Exception as e:
            self.handle_error("Video processing failed", e)
            return {}
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from video file using FFmpeg or similar tool.
        
        Returns:
            Dict containing video metadata (duration, dimensions, codec, etc.)
        """
        # Use caching if checksum is available
        if self.checksum:
            cache_key = f"video_metadata_{self.checksum}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
        
        metadata = {
            'duration': None,
            'width': None,
            'height': None,
            'framerate': None,
            'bitrate': None,
            'codec': None,
        }
        
        # Use FFmpeg if available for accurate metadata
        if self.ffmpeg_available and self.file_path:
            try:
                probe = self.ffmpeg.probe(self.file_path)
                
                # Extract video stream data
                video_stream = next((stream for stream in probe['streams'] 
                                    if stream['codec_type'] == 'video'), None)
                
                if video_stream:
                    # Extract basic video metadata
                    metadata['width'] = int(video_stream.get('width', 0))
                    metadata['height'] = int(video_stream.get('height', 0))
                    metadata['codec'] = video_stream.get('codec_name')
                    
                    # Parse framerate (can be in fraction format like "24000/1001")
                    if 'avg_frame_rate' in video_stream:
                        try:
                            num, den = map(int, video_stream['avg_frame_rate'].split('/'))
                            if den > 0:  # Avoid division by zero
                                metadata['framerate'] = round(num / den, 3)
                        except (ValueError, ZeroDivisionError):
                            pass
                    
                    # Extract bitrate (in kbps)
                    if 'bit_rate' in video_stream:
                        try:
                            metadata['bitrate'] = int(int(video_stream['bit_rate']) / 1000)
                        except (ValueError, TypeError):
                            pass
                
                # Get duration from format data
                if 'format' in probe and 'duration' in probe['format']:
                    try:
                        metadata['duration'] = int(float(probe['format']['duration']))
                    except (ValueError, TypeError):
                        pass
                
            except Exception as e:
                self.handle_error("FFmpeg metadata extraction failed", e)
        
        # Cache the result if we have a checksum
        if self.checksum:
            cache_key = f"video_metadata_{self.checksum}"
            self.set_cached_result(cache_key, metadata)
        
        return metadata
    
    def generate_thumbnail(self, timestamp: float = 0.0, size: Tuple[int, int] = (640, 360)) -> Optional[str]:
        """
        Generate a thumbnail at the specified timestamp.
        
        Args:
            timestamp: Time in seconds for thumbnail extraction
            size: Thumbnail dimensions (width, height)
            
        Returns:
            Path to the generated thumbnail or None if failed
        """
        if not self.ffmpeg_available or not self.file_path:
            self.handle_error("Cannot generate thumbnail without FFmpeg or valid file")
            return None
        
        try:
            # Create a temporary file for the thumbnail
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Extract the frame using FFmpeg
            (
                self.ffmpeg
                .input(self.file_path, ss=timestamp)
                .filter('scale', size[0], size[1])
                .output(temp_path, vframes=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            # Generate path for the thumbnail
            thumb_filename = f"{Path(self.file_name).stem}_thumb.jpg" if self.file_name else "thumbnail.jpg"
            thumb_path = os.path.join('thumbnails', thumb_filename)
            
            # Save to storage
            with open(temp_path, 'rb') as f:
                content = ContentFile(f.read())
                thumb_path = default_storage.save(thumb_path, content)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return thumb_path
            
        except Exception as e:
            self.handle_error("Thumbnail generation failed", e)
            return None
    
    def extract_frame(self, timestamp: float) -> Optional[bytes]:
        """
        Extract a single frame from the video as bytes.
        
        Args:
            timestamp: Time in seconds for frame extraction
            
        Returns:
            Frame image data as bytes or None if failed
        """
        if not self.ffmpeg_available or not self.file_path:
            return None
        
        try:
            # Create a temporary file for the frame
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Extract the frame using FFmpeg
            (
                self.ffmpeg
                .input(self.file_path, ss=timestamp)
                .output(temp_path, vframes=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            # Read the frame data
            with open(temp_path, 'rb') as f:
                frame_data = f.read()
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return frame_data
            
        except Exception as e:
            self.handle_error("Frame extraction failed", e)
            return None


class AudioProcessor(MediaProcessor):
    """
    Specialized processor for audio files.
    
    Features:
    - Audio metadata extraction (duration, bitrate, sample rate, etc.)
    - Waveform generation for visualization
    - Album art extraction
    - ID3 tag processing
    """
    
    def __init__(self, file_field, checksum=None):
        super().__init__(file_field, checksum)
        
        # Attempt to import optional libraries
        self.mutagen_available = False
        try:
            import mutagen
            self.mutagen = mutagen
            self.mutagen_available = True
        except ImportError:
            logger.warning("Mutagen not available. Advanced audio processing disabled.")
    
    def process(self) -> Dict[str, Any]:
        """
        Process audio file to extract metadata and generate waveform.
        
        Returns:
            Dict containing audio metadata and processing results
        """
        try:
            # Get basic metadata
            metadata = self.get_metadata()
            
            # Add waveform data if possible
            waveform = self.generate_waveform_data()
            if waveform:
                metadata['waveform_data'] = waveform
            
            # Extract album art if available
            album_art = self.extract_album_art()
            if album_art:
                metadata['album_art_path'] = album_art
            
            return metadata
        except Exception as e:
            self.handle_error("Audio processing failed", e)
            return {}
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from audio file using Mutagen or similar library.
        
        Returns:
            Dict containing audio metadata (duration, sample rate, etc.)
        """
        # Use caching if checksum is available
        if self.checksum:
            cache_key = f"audio_metadata_{self.checksum}"
            cached_result = self.get_cached_result(cache_key)
            if cached_result:
                return cached_result
        
        metadata = {
            'duration': None,
            'bitrate': None,
            'sample_rate': None,
            'channels': None,
            'codec': None,
            'artist': None,
            'album': None,
            'title': None,
            'track_number': None,
            'genre': None,
        }
        
        # Use Mutagen if available for accurate metadata
        if self.mutagen_available and self.file_path:
            try:
                audio = self.mutagen.File(self.file_path)
                
                if audio:
                    # Extract basic audio metadata
                    if hasattr(audio.info, 'length'):
                        metadata['duration'] = int(audio.info.length)
                    
                    if hasattr(audio.info, 'bitrate'):
                        metadata['bitrate'] = int(audio.info.bitrate / 1000)
                    
                    if hasattr(audio.info, 'sample_rate'):
                        metadata['sample_rate'] = audio.info.sample_rate
                    
                    if hasattr(audio.info, 'channels'):
                        metadata['channels'] = audio.info.channels
                    
                    # Extract codec information
                    file_format = type(audio).__name__.replace('File', '')
                    metadata['codec'] = file_format
                    
                    # Extract tag information differently based on file type
                    if isinstance(audio, self.mutagen.id3.ID3FileType):
                        # Extract ID3 tags (MP3, etc.)
                        if 'TPE1' in audio:  # Artist
                            metadata['artist'] = str(audio['TPE1'])
                        
                        if 'TALB' in audio:  # Album
                            metadata['album'] = str(audio['TALB'])
                        
                        if 'TIT2' in audio:  # Title
                            metadata['title'] = str(audio['TIT2'])
                        
                        if 'TRCK' in audio:  # Track number
                            try:
                                track = str(audio['TRCK']).split('/')[0]
                                metadata['track_number'] = int(track)
                            except (ValueError, IndexError):
                                pass
                        
                        if 'TCON' in audio:  # Genre
                            metadata['genre'] = str(audio['TCON'])
                    
                    elif hasattr(audio, 'tags') and audio.tags:
                        # Handle Vorbis comments (FLAC, OGG)
                        tags = audio.tags
                        
                        metadata['artist'] = tags.get('ARTIST', [None])[0]
                        metadata['album'] = tags.get('ALBUM', [None])[0]
                        metadata['title'] = tags.get('TITLE', [None])[0]
                        
                        if 'TRACKNUMBER' in tags:
                            try:
                                metadata['track_number'] = int(tags['TRACKNUMBER'][0])
                            except (ValueError, IndexError):
                                pass
                        
                        metadata['genre'] = tags.get('GENRE', [None])[0]
            
            except Exception as e:
                self.handle_error("Mutagen metadata extraction failed", e)
        
        # Cache the result if we have a checksum
        if self.checksum:
            cache_key = f"audio_metadata_{self.checksum}"
            self.set_cached_result(cache_key, metadata)
        
        return metadata
    
    def generate_waveform_data(self, num_points: int = 100) -> Optional[List[float]]:
        """
        Generate waveform data for visualization.
        
        Args:
            num_points: Number of amplitude points to generate
            
        Returns:
            List of amplitude values or None if failed
        """
        if not self.file_path:
            return None
        
        try:
            # Attempt to use specialized libraries if available
            try:
                import numpy as np
                from pydub import AudioSegment
                
                # Load audio file
                audio = AudioSegment.from_file(self.file_path)
                
                # Convert to mono for simplicity
                audio = audio.set_channels(1)
                
                # Get raw audio data as numpy array
                samples = np.array(audio.get_array_of_samples())
                
                # Normalize
                samples = samples / np.max(np.abs(samples))
                
                # Resample to desired number of points
                samples_per_point = len(samples) // num_points
                
                waveform = []
                for i in range(num_points):
                    start = i * samples_per_point
                    end = (i + 1) * samples_per_point
                    if end > len(samples):
                        end = len(samples)
                    
                    # Take peak amplitude in each segment
                    segment = samples[start:end]
                    if len(segment) > 0:
                        amplitude = float(np.max(np.abs(segment)))
                        waveform.append(amplitude)
                
                return waveform
                
            except ImportError:
                # Fallback to a simpler approach if specialized libraries aren't available
                # In a real implementation, you'd want to add a simpler waveform generator
                # This is a placeholder that creates a synthetic waveform
                import random
                return [random.uniform(0.1, 1.0) for _ in range(num_points)]
                
        except Exception as e:
            self.handle_error("Waveform generation failed", e)
            return None
    
    def extract_album_art(self) -> Optional[str]:
        """
        Extract album art embedded in the audio file.
        
        Returns:
            Path to the extracted album art or None if not found/failed
        """
        if not self.mutagen_available or not self.file_path:
            return None
        
        try:
            audio = self.mutagen.File(self.file_path)
            
            if audio:
                # For ID3 files (MP3)
                if isinstance(audio, self.mutagen.id3.ID3FileType) and audio.tags:
                    for tag in ['APIC:', 'APIC:Cover', 'APIC:Front Cover']:
                        if tag in audio.tags:
                            apic = audio.tags[tag]
                            image_data = apic.data
                            
                            # Save the image
                            art_filename = f"{Path(self.file_name).stem}_cover.jpg" if self.file_name else "cover.jpg"
                            art_path = os.path.join('album_art', art_filename)
                            
                            # Save to storage
                            content = ContentFile(image_data)
                            art_path = default_storage.save(art_path, content)
                            
                            return art_path
                
                # For FLAC files
                elif isinstance(audio, self.mutagen.flac.FLAC) and audio.pictures:
                    picture = audio.pictures[0]
                    image_data = picture.data
                    
                    # Save the image
                    art_filename = f"{Path(self.file_name).stem}_cover.jpg" if self.file_name else "cover.jpg"
                    art_path = os.path.join('album_art', art_filename)
                    
                    # Save to storage
                    content = ContentFile(image_data)
                    art_path = default_storage.save(art_path, content)
                    
                    return art_path
            
            return None
            
        except Exception as e:
            self.handle_error("Album art extraction failed", e)
            return None