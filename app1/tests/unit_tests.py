from django.test import TestCase
from django.contrib.auth.models import User
from app1.models import UploadedFile
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.conf import settings
from app1.models import StyleSettings, DefaultStyleSettings

class TestUploadedFile(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create(username="testuser")

    # Unit Test
    def test_user_upload_path_txt(self):
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
        print(actual_path)
        print(expected_path)
    
    def test_user_upload_path_csv(self):
        # Create an instance of UploadedFile
        uploaded_file = UploadedFile(
            user=self.user,
            file_name="example.csv"  # Replace with the desired filename
        )

        # Call the user_upload_path function to get the actual path
        actual_path = uploaded_file.file.field.upload_to(uploaded_file, "example.csv")

        # Define the expected path based on the structure defined in your user_upload_path function
        expected_path = f"imported_files/{self.user.username}/example.csv"

        # Assert that the actual path matches the expected path
        self.assertEqual(actual_path, expected_path)
    
    def test_user_upload_path_xlsx(self):
        # Create an instance of UploadedFile
        uploaded_file = UploadedFile(
            user=self.user,
            file_name="example.xlsx"  # Replace with the desired filename
        )

        # Call the user_upload_path function to get the actual path
        actual_path = uploaded_file.file.field.upload_to(uploaded_file, "example.xlsx")

        # Define the expected path based on the structure defined in your user_upload_path function
        expected_path = f"imported_files/{self.user.username}/example.xlsx"

        # Assert that the actual path matches the expected path
        self.assertEqual(actual_path, expected_path)
    
    def test_invalid_file_extension(self):
        #file_with_invalid_extension = SimpleUploadedFile("file.xyz", b"content", content_type="text/plain")
        #uploaded_file = SimpleUploadedFile(user=self.user, file=file_with_invalid_extension)
        uploaded_file = UploadedFile(user=self.user,file_name="example.xyz")
        #actual_path = uploaded_file.file.field.upload_to(uploaded_file, "example.xyz")
        with self.assertRaises(ValidationError):
            uploaded_file.full_clean()  # This should raise a ValidationError because of the invalid extension

class TestStyleSettings(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")

    def test_default_style_settings(self):
        style_settings = StyleSettings(user=self.user)
        style_settings.save()
        self.assertEqual(style_settings.font_type, 'Computer Modern')
        self.assertEqual(style_settings.wall_color, 'black')

    def test_invalid_color_choice(self):
        style_settings = StyleSettings(user=self.user, wall_color='ultraviolet')  # Not a valid choice
        with self.assertRaises(ValidationError):
            style_settings.full_clean()

    def test_create_default_style_settings(self):
        default_style = DefaultStyleSettings(user=self.user)
        default_style.save()
        self.assertEqual(default_style.font_type, 'Computer Modern')

class TestPropertyModifications(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.style_settings = StyleSettings.objects.create(user=self.user)

    def test_property_changes(self):
        # Change some properties
        self.style_settings.font_type = 'Arial'
        self.style_settings.font_color = 'green'
        self.style_settings.save()

        # Reload from database
        updated_settings = StyleSettings.objects.get(id=self.style_settings.id)
        self.assertEqual(updated_settings.font_type, 'Arial')
        self.assertEqual(updated_settings.font_color, 'green')

class TestDefaultValues(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")

    def test_default_settings(self):
        style_settings = StyleSettings.objects.create(user=self.user)
        self.assertEqual(style_settings.font_type, 'Computer Modern')
        self.assertEqual(style_settings.font_color, 'black')
        self.assertEqual(style_settings.orientation, 'portrait')
        self.assertEqual(style_settings.wall_color, 'black')

class TestRelationshipIntegrity(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.style_settings = StyleSettings.objects.create(user=self.user)

    def test_user_deletion_cascade(self):
        # Deleting the user should also delete the associated StyleSettings
        user_id = self.user.id
        self.user.delete()

        with self.assertRaises(StyleSettings.DoesNotExist):
            StyleSettings.objects.get(user_id=user_id)
