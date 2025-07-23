# # ❌ Using real storage in tests
# def test_upload(self):
#     client.post('/upload', {'file': SimpleUploadedFile(...)})
#     # Leaves files in storage

# # ✅ Use memory storage for tests
# from django.test import override_settings

# @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
# class FileTests(TestCase):
#     def setUp(self):
#         self.storage = default_storage._wrapped  # Access real storage