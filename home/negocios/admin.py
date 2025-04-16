from django.contrib import admin
from .models import Business, Document, DocumentFile, ReportRecipient

@admin.register(ReportRecipient)
class ReportRecipientAdmin(admin.ModelAdmin):
    list_display = ('email',)
    search_fields = ('email',)

class DocumentFileInline(admin.TabularInline):  # или admin.StackedInline
    model = DocumentFile
    extra = 1  # Количество пустых форм для добавления файлов

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('id', 'business_text', 'pub_date')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'business', 'owner', 'status', 'pub_date')
    list_filter = ('status',)  # Фильтр по статусу
    inlines = [DocumentFileInline]  # Добавляем inline для файлов
