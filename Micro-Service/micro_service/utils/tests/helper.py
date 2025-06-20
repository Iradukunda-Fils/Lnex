import os
from pathlib import Path
from typing import List, Union
from django.test import TestCase
# Import the function to be tested
from ..helper import create_dirs_or_files  # Adjust 'your_module'
from django.conf import settings


class CreateDirsOrFilesTests(TestCase):
    """
    Test suite for the create_dirs_or_files function.
    """

    def setUp(self):
        """Set up test environment: Create a temporary test directory."""
        self.test_root = Path(settings.BASE_DIR, 'utils/tests', "test_root").resolve()
        self.test_root.mkdir(exist_ok=True)  # Ensure test root exists
        self.addCleanup(self.remove_test_root)  # Clean up after tests

    def remove_test_root(self):
        """Remove the test root directory and its contents."""
        if self.test_root.exists():
            for item in self.test_root.rglob("*"):  # Corrected
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
            self.test_root.rmdir()

    def test_create_single_directory(self):
        """Test creating a single directory."""
        path = self.test_root / "new_dir"
        created_path = create_dirs_or_files(path)
        self.assertEqual(created_path, path)
        self.assertTrue(path.exists())
        self.assertTrue(path.is_dir())

    def test_create_multiple_directories(self):
        """Test creating multiple directories."""
        paths = [self.test_root / "dir1", self.test_root / "dir2", self.test_root / "dir3"]
        created_paths = create_dirs_or_files(paths)
        self.assertEqual(created_paths, paths)
        for p in paths:
            self.assertTrue(p.exists())
            self.assertTrue(p.is_dir())

    def test_create_single_file(self):
        """Test creating a single file."""
        path = self.test_root / "new_file.txt"
        created_path = create_dirs_or_files(path, create_file=True)
        self.assertEqual(created_path, path)
        self.assertTrue(path.exists())
        self.assertTrue(path.is_file())

    def test_create_multiple_files(self):
        """Test creating multiple files."""
        paths = [self.test_root / "file1.txt", self.test_root / "file2.txt"]
        created_paths = create_dirs_or_files(paths, create_file=True)
        self.assertEqual(created_paths, paths)
        for p in paths:
            self.assertTrue(p.exists())
            self.assertTrue(p.is_file())

    def test_create_directory_exists_ok(self):
        """Test creating a directory that already exists with path_exists_ok=True."""
        path = self.test_root / "existing_dir"
        path.mkdir(exist_ok=True)
        created_path = create_dirs_or_files(path, path_exist_ok=True)
        self.assertEqual(created_path, path)
        self.assertTrue(path.exists())
        self.assertTrue(path.is_dir())

    def test_create_directory_exists_not_ok(self):
        """Test creating a directory that already exists with path_exists_ok=False."""
        path = self.test_root / "existing_dir_fail"
        path.mkdir(exist_ok=True)
        with self.assertRaises(FileExistsError):
            create_dirs_or_files(path, path_exist_ok=False)

    def test_create_file_exists_not_ok(self):
        """Test creating a file that already exists with path_exists_ok=False."""
        path = self.test_root / "existing_file_fail.txt"
        path.touch()
        with self.assertRaises(FileExistsError):
            create_dirs_or_files(path, create_file=True, path_exist_ok=False)

    def test_create_file_with_content(self):
        """Test creating a file with content."""
        path = self.test_root / "content_file.txt"
        content = "Test content\nLine 2"
        created_path = create_dirs_or_files(path, create_file=True, file_content=content)
        self.assertEqual(created_path, path)
        self.assertTrue(path.exists())
        self.assertTrue(path.is_file())
        self.assertEqual(path.read_text(), content)

    def test_create_multiple_files_with_content(self):
        """Test creating multiple files with different content."""
        paths = [self.test_root / "content_file1.txt", self.test_root / "content_file2.txt"]
        contents = ["Content 1", "Content 2"]
        create_dirs_or_files(paths, create_file=True, file_content="\n".join(contents))  # Pass all content
        for i, p in enumerate(paths):
            self.assertEqual(p.read_text(), contents[i])

    def test_create_file_no_extension(self):
        """Test creating a file with no extension and require_extension=True."""
        path = self.test_root / "no_extension"
        with self.assertRaises(ValueError):
            create_dirs_or_files(path, create_file=True, require_extension=True)

    def test_create_file_no_extension_ok(self):
        """Test creating a file with no extension and require_extension=False."""
        path = self.test_root / "no_extension_ok"
        created_path = create_dirs_or_files(path, create_file=True, require_extension=False)
        self.assertEqual(created_path, path)
        self.assertTrue(path.exists())
        self.assertTrue(path.is_file())

    def test_create_directory_with_parents(self):
        """Test creating a directory with parent directories."""
        path = self.test_root / "parent_dir" / "sub_dir" / "final_dir"
        created_path = create_dirs_or_files(path, parents=True)
        self.assertEqual(created_path, path)
        self.assertTrue(path.exists())
        self.assertTrue(path.is_dir())
        self.assertTrue((self.test_root / "parent_dir").exists())
        self.assertTrue((self.test_root / "parent_dir" / "sub_dir").exists())

    def test_create_file_with_parents(self):
        """Test creating a file with parent directories."""
        path = self.test_root / "parent_dir_file" / "sub_dir_file" / "final_file.txt"
        created_path = create_dirs_or_files(path, create_file=True, parents=True)
        self.assertEqual(created_path, path)
        self.assertTrue(path.exists())
        self.assertTrue(path.is_file())
        self.assertTrue((self.test_root / "parent_dir_file").exists())
        self.assertTrue((self.test_root / "parent_dir_file" / "sub_dir_file").exists())
