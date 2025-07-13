import os
import environ
import os
from pathlib import Path
from typing import Union, List, Optional, Generator
import contextlib
import logging

logger = logging.getLogger('utils')

def create_dir(path: os.PathLike) -> os.PathLike:
    """Returning the created path."""
    os.makedirs(path, exist_ok=True)
    return path  # Explicitly return the path


def create_dirs_or_files(
    path_input: str | os.PathLike | List[str | os.PathLike],
    path_exist_ok: bool = False,
    create_file: bool = False,
    file_content: Optional[str] = None,
    mode: int = 0o777,
    parents: bool = False,
    require_extension: bool = True
) -> Path | List[Path]:
    """
    Create directories or files with enhanced validation and context management.
    
    Args:
        path_input: Path(s) to create (str/PathLike or list)
        path_exist_ok: Skip existing paths without error (default: False)
        create_file: Create file instead of directory (default: False)
        file_content: Content for created files (default: None)
        mode: File/directory permissions (default: 0o777)
        parents: Create parent directories (default: False)
        require_extension: Require file extension for files (default: True)
    
    Returns:
        Created Path object(s)
    
    Raises:
        ValueError: Invalid arguments or missing extension
        FileExistsError: Path exists and path_exist_ok=False
        PermissionError: Insufficient permissions
    
    Examples:
        With context manager:
        >>> with create_dirs_or_files("data.log", create_file=True) as p:
        ...     p.write_text("logs")
    """
    def _validate_file_path(path: Path) -> None:
        """Validate file path requirements."""
        if create_file:
            if require_extension and not path.suffix:
                raise ValueError(f"File path requires extension: {path}")
            if path.exists() and not path_exist_ok:
                raise FileExistsError(f"File already exists: {path}")

    @contextlib.contextmanager
    def _file_context(path: Path) -> Generator[Path, None, None]:
        """Context manager for file handling."""
        try:
            yield path
        finally:
            if file_content is not None:
                with path.open('w', encoding='utf-8') as f:
                    f.write(file_content)

    def _create_single_path(path: str | os.PathLike) -> Path:
        """Core path creation logic."""
        path_obj = Path(path)
        
        if create_file:
            _validate_file_path(path_obj)
            path_obj.parent.mkdir(mode=mode, parents=parents, exist_ok=True)
            with _file_context(path_obj) as p:
                p.touch(mode=mode, exist_ok=True)
        else:
            if path_obj.exists() and not path_exist_ok:
                raise FileExistsError(f"Path exists: {path_obj}")
            path_obj.mkdir(mode=mode, parents=parents, exist_ok=True)
        
        return path_obj

    # Handle list inputs
    if isinstance(path_input, (list, tuple)):
        return [_create_single_path(p) for p in path_input]
    
    return _create_single_path(path_input)


def load_django_environ(
    path: Union[Path, str, list[Union[Path, str]]],
    env: Optional[environ.Env] = None,
    defaults: Optional[dict] = None,
    debug: bool = False
) -> environ.Env:
    """
    Load environment variables into the current Django environment.

    Args:
        path: A single path, string, or list of paths to .env files.
        env: Optionally pass an existing instance of environ.Env.
        defaults: Optional default environment values, e.g., {"DEBUG": (bool, False)}.
        debug: Toggle debug logging.

    Returns:
        Instance of environ.Env
    """
    if not env:
        defaults = defaults or {"DEBUG": (bool, debug)}
        env = environ.Env(**defaults)

    paths = path if isinstance(path, (list, tuple)) else [path]

    for p in paths:
        p = Path(p)
        if p.exists():
            try:
                environ.Env.read_env(p)
                if debug:
                    logger.info(f"Loaded environment variables from: {p}")
            except Exception as e:
                logger.error(f"Failed to load env file {p}: {e}")
                raise
        else:
            logger.warning(f".env file not found: {p}")

    return env


    