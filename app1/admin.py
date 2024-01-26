from django.contrib import admin

from .models import UploadedFile, ConvertedFile


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    pass

@admin.register(ConvertedFile)
class ConvertedFileAdmin(admin.ModelAdmin):
    pass