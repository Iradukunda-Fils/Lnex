# from abc import ABC, abstractmethod
# import subprocess
# from typing import Optional, Union, Protocol
# import os
# import logging
# from pathlib import Path

# # ================================
# # 1. Interfaces (Dependency Inversion)
# # ================================
# class DurationCalculatable(Protocol):
#     """Protocol (Interface) for duration calculation strategies."""
#     def calculate(self, source: Union[str, os.PathLike, bytes]) -> Optional[float]:
#         ...

# class MediaReader(Protocol):
#     """Protocol for reading media metadata."""
#     def read_duration(self) -> Optional[float]:
#         ...

# # ================================
# # 2. Strategy Pattern (Open/Closed)
# # ================================
# class DurationCalculator:
#     """Context class that delegates to strategy implementations."""
#     def __init__(self, strategy: DurationCalculatable):
#         self._strategy = strategy

#     def get_duration(self, source: Union[str, os.PathLike, bytes]) -> Optional[float]:
#         return self._strategy.calculate(source)

# # ================================
# # 3. Concrete Strategies
# # ================================
# class FFmpegDurationCalculator(DurationCalculatable):
#     """High-accuracy strategy using FFmpeg."""
#     def __init__(self, ffprobe_path: str = "ffprobe"):
#         self.ffprobe_path = ffprobe_path

#     def calculate(self, source: Union[str, os.PathLike, bytes]) -> Optional[float]:
#         try:
#             cmd = [
#                 self.ffprobe_path,
#                 "-v", "error",
#                 "-show_entries", "format=duration",
#                 "-of", "default=noprint_wrappers=1:nokey=1",
#                 "-i", str(source) if not isinstance(source, bytes) else "-"
#             ]
#             result = subprocess.run(
#                 cmd,
#                 input=source if isinstance(source, bytes) else None,
#                 capture_output=True,
#                 text=True,
#                 check=True
#             )
#             return float(result.stdout.strip())
#         except (subprocess.CalledProcessError, ValueError) as e:
#             logging.warning(f"FFprobe failed: {e}")
#             return None

# class HeaderDurationCalculator(DurationCalculatable):
#     """Fallback strategy parsing file headers."""
#     def calculate(self, source: Union[str, os.PathLike, bytes]) -> Optional[float]:
#         try:
#             with MediaFile(source) as media:
#                 return media.read_duration()
#         except Exception as e:
#             logging.warning(f"Header parsing failed: {e}")
#             return None

# # ================================
# # 4. Factory Pattern
# # ================================
# class DurationCalculatorFactory:
#     """Creates appropriate calculator based on system capabilities."""
#     @staticmethod
#     def create(ffmpeg_preferred: bool = True) -> DurationCalculator:
#         if ffmpeg_preferred and FFmpegDurationCalculator.is_available():
#             return DurationCalculator(FFmpegDurationCalculator())
#         return DurationCalculator(HeaderDurationCalculator())

#     @staticmethod
#     def create_ffmpeg() -> DurationCalculator:
#         return DurationCalculator(FFmpegDurationCalculator())

#     @staticmethod
#     def create_header_based() -> DurationCalculator:
#         return DurationCalculator(HeaderDurationCalculator())

# # ================================
# # 5. Adapter Pattern (Media Abstraction)
# # ================================
# class MediaFile:
#     """Uniform interface for file/bytes/file-like objects."""
#     def __init__(self, source: Union[str, os.PathLike, bytes]):
#         self.source = source
#         self._file = None

#     def __enter__(self) -> MediaReader:
#         if isinstance(self.source, (str, os.PathLike)):
#             self._file = open(self.source, 'rb')
#         elif isinstance(self.source, bytes):
#             from io import BytesIO
#             self._file = BytesIO(self.source)
#         else:  # Assume file-like
#             self._file = self.source
#             self._file.seek(0)
#         return self

#     def read_duration(self) -> Optional[float]:
#         """Placeholder for actual format-specific parsing."""
#         # Implement MP3/MP4/WAV/etc. header parsing here
#         return None

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if self._file and not hasattr(self.source, 'read'):
#             self._file.close()

# # ================================
# # 6. Usage Example
# # ================================
# if __name__ == "__main__":
#     # Configure logging
#     logging.basicConfig(level=logging.INFO)

#     # Factory creates the best available calculator
#     calculator = DurationCalculatorFactory.create()

#     # Example usage
#     duration = calculator.get_duration("./video.mp4")
#     print(f"Duration: {duration:.2f}s")