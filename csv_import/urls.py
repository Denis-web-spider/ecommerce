from django.urls import path

from .views import CsvImportView

urlpatterns = [
    path('', CsvImportView.as_view(), name='csv_import')
]
