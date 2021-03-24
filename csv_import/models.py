from django.db import models

class Csv(models.Model):
    file_name = models.FileField(upload_to='csv', verbose_name='Csv файл')
    uploaded = models.DateTimeField(auto_now_add=True, verbose_name='Загружен')
    activated = models.BooleanField(default=False, verbose_name='Активирован')

    def __str__(self):
        return f'Csv файл -- {self.id}'
