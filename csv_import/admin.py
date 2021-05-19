from django.contrib import admin

from .models import Csv

class CsvAdmin(admin.ModelAdmin):

    list_display = ['id', 'file_name', 'uploaded', 'activated']
    list_display_links = ['id', 'file_name', 'uploaded', 'activated']
    search_fields = ['id', 'file_name']
    list_filter = ['uploaded', 'activated']

admin.site.register(Csv, CsvAdmin)
