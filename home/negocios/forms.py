from django import forms
from .models import Document, DocumentFile, Business
from django.forms.widgets import ClearableFileInput
from django.core import validators
from django.contrib.auth import get_user_model

User = get_user_model()
class CustomClearableFileInput(ClearableFileInput):
    initial_text = "Arquivo atual:"  # Меняем "Currently:"
    input_text = "Novo arquivo"  # Меняем "Change:"
    # template_name = 'widgets/custom_clearable_file_input.html' # Создай свой шаблон чтобы убрать Escolher arquivo


class BusinessForm(forms.ModelForm):

    class Meta:
        model = Business
        fields = ['business_text']  # Укажите поля, которые должны быть в форме
        labels = {
            'business_text': 'Nome do Negócio:',
            'delete': 'Remover negocio',
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        if not obj.owner_id:  # Добавляем владельца, если его нет
            obj.owner = self.initial.get('owner')
        if commit:
            obj.save()
        return obj
class DocumentForm(forms.ModelForm):
    upload_responsible = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Responsável pelo upload"
    )
    approval_responsible = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Responsável pela aprovação"
    )
    class Meta:
        model = Document
        fields = ['document_text', 'upload_responsible', 'approval_responsible']  # Укажите поля, которые должны быть в форме
        labels = {
            'document_text': 'Nome do documento:',
            'delete': 'Remover arquivo',
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        if not obj.owner_id:  # Добавляем владельца, если его нет
            obj.owner = self.initial.get('owner')
        if commit:
            obj.save()
        return obj

class DocumentFileForm(forms.ModelForm):
    class Meta:
        model = DocumentFile
        fields = ['file']  # Укажите поля, которые должны быть в форме
        labels = {
            'file': '',
            'delete': 'Remover arquivo',
        }
        widgets = {
            'file': CustomClearableFileInput(),  # Используем наш кастомный виджет
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        if not obj.owner_id:  # Добавляем владельца, если его нет
            obj.owner = self.initial.get('owner')
        if commit:
            obj.save()
        return obj

# strip means to remove whitespace from the beginning and the end before storing the column
class CommentForm(forms.Form):
    comment = forms.CharField(required=True, max_length=500, min_length=3, strip=True, label="Comentário",)


