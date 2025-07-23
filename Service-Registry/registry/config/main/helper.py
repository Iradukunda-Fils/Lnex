from pathlib import Path
from utils.helper import create_dirs_or_files
import logging

settings_log = logging.getLogger('settings')


def ensure_env_file(env_file: str) -> None:
    """
    Ensures that the .env file exists, creates it if missing using the utility function.
    Logs all operations.
    """
    try:
        # Create the file and its parent directories if it doesn't exist
        created_path = create_dirs_or_files(
            path_input=env_file,
            create_file=True,
            file_content="KEY=value\n",  # Default content
            parents=True,
            require_extension=True,
            path_exist_ok=False
        )

        settings_log.info(f"Created new environment file: {created_path}")

    except FileExistsError:
        settings_log.info(f"Environment file already exists: {env_file}")
    except PermissionError as pe:
        settings_log.error(f"Permission denied while creating env file: {env_file} | {pe}")
    except ValueError as ve:
        settings_log.error(f"Invalid env file path: {env_file} | {ve}")
    except Exception as e:
        settings_log.error(f"Unexpected error while handling env file: {env_file} | {e}")

        