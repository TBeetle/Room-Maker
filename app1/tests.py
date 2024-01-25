from django.test import TestCase
from django.contrib.auth.models import User
from app1.models import UploadedFile

class TestUploadedFile(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create(username="testuser")

    def test_user_upload_path(self):
        # Create an instance of UploadedFile
        uploaded_file = UploadedFile(
            user=self.user,
            file_name="example.txt"  # Replace with the desired filename
        )

        # Call the user_upload_path function to get the actual path
        actual_path = uploaded_file.file.field.upload_to(uploaded_file, "example.txt")

        # Define the expected path based on the structure defined in your user_upload_path function
        expected_path = f"imported_files/{self.user.username}/example.txt"

        # Assert that the actual path matches the expected path
        self.assertEqual(actual_path, expected_path)

