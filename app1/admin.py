from django.contrib import admin

from .models import UploadedFile, ConvertedFile, DefaultStyleSettings, StyleSettings


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    pass

@admin.register(ConvertedFile)
class ConvertedFileAdmin(admin.ModelAdmin):
    pass

@admin.register(DefaultStyleSettings)
class DefaultSSAdmin(admin.ModelAdmin):
    pass

@admin.register(StyleSettings)
class SSAdmin(admin.ModelAdmin):
    pass