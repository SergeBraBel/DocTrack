from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
import os


class ReportRecipient(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
class Business(models.Model):
    STATUS_CHOICES = [
        ('collecting', 'Coletando documentos'),
        ('finalized', 'Finalizado'),
    ]
    business_text = models.CharField(max_length=200, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='businesses_owned')
    pub_date = models.DateTimeField("date published", default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='collecting')

    def __str__(self):
        return self.business_text

class Document(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Não aprovado'),
        ('approved', 'Aprovado'),
    ]
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='documents')
    document_text = models.CharField(max_length=200)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='documents_owned')
    upload_responsible = models.ForeignKey(  # Кто должен загрузить документ
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="responsible_for_upload"
    )

    approval_responsible = models.ForeignKey(  # Кто должен согласовать документ
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="responsible_for_approval"
    )
    pub_date = models.DateTimeField("date published", default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')  # Добавляем статус
    last_approved_date = models.DateTimeField(null=True, blank=True)  # Дата последнего согласования
    last_approved_by = models.ForeignKey(  # Кто согласовал документ
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_documents"
    )

    def last_file_uploaded(self):
        last_file = self.files.order_by('-pub_date').first()
        return last_file.pub_date if last_file else None

    def approve(self, user):
        """Метод для согласования документа."""
        self.status = 'approved'
        self.last_approved_date = timezone.now()
        self.last_approved_by = user
        self.save()

    def save(self, *args, **kwargs):
        """Обновляем last_approved_date и last_approved_by только при смене статуса на 'approved'."""
        if self.status == 'pending':
            self.last_approved_date = None
            self.last_approved_by = None
        super().save(*args, **kwargs)

    # Shows up in the admin list
    def __str__(self):
        return f"{self.document_text} ({self.get_status_display()})"

def business_directory_path(instance, filename):
    """Формируем путь: media/business_name/filename"""
    return os.path.join(f"businesses/{instance.document.business.business_text}", filename)
class DocumentFile(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=business_directory_path)  # Поле для хранения файла
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='files_owned')
    pub_date = models.DateTimeField("date published", default=timezone.now)

    def __str__(self):
        return self.file.name

class Comment(models.Model) :
    text = models.TextField(
        validators=[MinLengthValidator(3, "O comentário deve ter mais de 3 caracteres")]
    )

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='comments')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        if len(self.text) < 15 : return self.text
        return self.text[:11] + ' ...'

