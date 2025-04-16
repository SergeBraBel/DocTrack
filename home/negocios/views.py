from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Business, Document, DocumentFile, Comment
from django.forms import inlineformset_factory
from django.urls import reverse_lazy, reverse
from .forms import DocumentForm, DocumentFileForm, BusinessForm, CommentForm
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
import os
import zipfile
from django.http import HttpResponse
from .document_lists import DOCUMENT_LIST_PRODUTOR, DOCUEMNT_LIST_EMPRESA
from django.utils.timezone import now
from .owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.timezone import now
from negocios.utils.reports import generate_report_body

# Список всех бизнесов
class BusinessListView(OwnerListView):
    model = Business
    template_name = 'negocios/business_list.html'
    context_object_name = 'businesses'

    def get_queryset(self):
        # Сортировка бизнесов по дате в обратном порядке
        return Business.objects.all().order_by('-pub_date')  # Используем `-` для обратного порядка
    def post(self, request, *args, **kwargs):
        business_id = request.POST.get('business_id')
        business = get_object_or_404(Business, id=business_id)

        # Переключаем статус
        if business.status == 'collecting':
            business.status = 'finalized'
        else:
            business.status = 'collecting'
        business.save()

        return redirect('negocios:business_list')



# Создание нового бизнеса
class BusinessCreateView(OwnerCreateView):
    model = Business
    form_class = BusinessForm
    template_name = 'negocios/business_form.html'  # Шаблон для формы
    # fields = ['business_text']  # Поля, которые будут отображаться в форме
    success_url = reverse_lazy('negocios:business_list')  # Перенаправление после успешного создания

class BusinessCreateViewProdutor(BusinessCreateView):

    def form_valid(self, form):
        response = super().form_valid(form)
        # Создаём стандартные документы
        for doc_text in DOCUMENT_LIST_PRODUTOR:
            Document.objects.create(business=self.object, document_text=doc_text, owner=self.request.user)
        return response
class BusinessCreateViewEmpresa(BusinessCreateView):

    def form_valid(self, form):
        response = super().form_valid(form)
        # Создаём стандартные документы
        for doc_text in DOCUEMNT_LIST_EMPRESA:
            Document.objects.create(business=self.object, document_text=doc_text)
        return response


# Обновление существующего бизнеса
class BusinessUpdateView(OwnerUpdateView):
    model = Business
    template_name = 'negocios/business_form.html'  # Шаблон для формы
    fields = ['business_text']  # Поля, которые будут отображаться в форме
    success_url = reverse_lazy('negocios:business_list')  # Перенаправление после успешного обновления

class BusinessDetailView(OwnerDetailView):
    model = Business
    template_name = 'negocios/business_detail.html'
    context_object_name = 'business'  # Теперь в шаблоне будет `business`

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = self.object.documents.all()  # Передаём связанные документы
        return context

class BusinessDeleteView(OwnerDeleteView):
    model = Business  # Указываем модель, которую будем удалять
    template_name = 'negocios/business_confirm_delete.html'  # Шаблон для подтверждения удаления
    success_url = reverse_lazy('negocios:business_list')  # URL для перенаправления после успешного удаления

# Document Views
class DocumentListView(OwnerListView):
    model = Document
    template_name = 'negocios/document_list.htmll'
    context_object_name = 'documents'



class DocumentDetailView(OwnerDetailView):
    model = Document
    template_name = 'negocios/document_detail.html'
    context_object_name = 'document'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Проверяем, какой метод вызвал запрос
        print(f"Request method: {self.request.method}")
        business_id = self.request.GET.get('business_id')
        context['business_id'] = business_id
        DocumentFileFormSet = inlineformset_factory(Document, DocumentFile, form=DocumentFileForm, extra=1)
        context['formset'] = DocumentFileFormSet(self.request.POST, self.request.FILES)
        document = self.object
        # Расчёт количества дней
        delta = now().date() - document.pub_date.date()
        context['days_since_creation'] = delta.days
        # Добавляем комментарии
        context['comments'] = Comment.objects.filter(document=self.object).order_by('-updated_at')
        context['comment_form'] = CommentForm()
        # Получаем всех пользователей (если нужно для выбора ответственного)
        context['users'] = User.objects.all()
        context['files'] = document.files.all()

        return context




class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm  # Используем кастомную форму
    template_name = 'negocios/document_form.html'  # Укажите имя вашего шаблона
    # success_url = reverse_lazy('negocios:business_list')  # Укажите URL для перенаправления после успешного создания
    def get_success_url(self):
        """Перенаправляет на детали бизнеса после создания документа"""
        return reverse('negocios:business_detail', kwargs={'pk': self.object.business.pk})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем business_id из параметров запроса
        business_id = self.request.GET.get('business_id')
        if business_id:
            context['business_id'] = business_id  # Передаем в контекст для шаблона

        # Создаем formset для DocumentFile
        DocumentFileFormSet = inlineformset_factory(
            Document, DocumentFile, form=DocumentFileForm, extra=1
        )
        if self.request.POST:
            context['formset'] = DocumentFileFormSet(self.request.POST, self.request.FILES)
        else:
            context['formset'] = DocumentFileFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        print(context.keys())
        formset = context['formset']
        # Получаем business_id и устанавливаем его перед сохранением
        business_id = self.request.GET.get('business_id')
        business = get_object_or_404(Business, id=business_id)  # Проверяем, что бизнес существует
        form.instance.business = business  # Привязываем документ к бизнесу
        form.instance.owner = self.request.user  # Устанавливаем владельца документа

        if formset.is_valid():
            self.object = form.save()
            # Присваиваем owner каждому файлу в formset
            formset.instance = self.object
            instances = formset.save(commit=False)  # Останавливаем автоматическое сохранение

            for instance in instances:
                instance.owner = self.request.user  # Устанавливаем владельца файла
                instance.save()  # Сохраняем каждый файл вручную

            formset.save_m2m()  # Сохраняем связи many-to-many, если есть

            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = Document
    template_name = 'negocios/document_form.html'
    form_class = DocumentForm  # Используем кастомную форму

    def get_success_url(self):
        if self.object.business:  # Check if business exists
            return reverse_lazy('negocios:business_detail', kwargs={'pk': self.object.business.id})
        return reverse_lazy('negocios:business_list')  # Fallback if business doesn't exist

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # DocumentFileFormSet = inlineformset_factory(Document, DocumentFile, form=DocumentFileForm, fields=('file',),can_delete=True, extra=1)
        DocumentFileFormSet = inlineformset_factory(Document, DocumentFile, form=DocumentFileForm, extra=1)
        # Создаем formset в любом случае
        if self.request.POST:
            formset = DocumentFileFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            formset = DocumentFileFormSet(instance=self.object)

        context['formset'] = formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))



class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    template_name = 'negocios/document_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Предполагается, что у документа есть связь с бизнесом
        context['business'] = self.object.business
        return context

    def get_success_url(self):
        business = self.object.business  # Используем правильное поле
        if business:
            return reverse_lazy('negocios:business_detail', kwargs={'pk': business.id})
        return reverse_lazy('negocios:business_list')  # Запасной вариант



class DocumentFileCreateView(LoginRequiredMixin, CreateView):
    model = DocumentFile
    form_class = DocumentFileForm
    template_name = 'negocios/document_file_form.html'

    def get_context_data(self, **kwargs):
        """Добавляем document в контекст"""
        context = super().get_context_data(**kwargs)
        context['document'] = get_object_or_404(Document, pk=self.kwargs.get('pk'))
        return context

    def form_valid(self, form):
        """Привязываем файл к документу перед сохранением"""
        document_id = self.kwargs.get('pk')
        form.instance.document_id = document_id
        form.instance.owner = self.request.user  # Устанавливаем владельца файла
        return super().form_valid(form)

    def get_success_url(self):
        """После загрузки файла перенаправляем обратно в детали документа"""
        # return reverse_lazy('negocios:document_detail', kwargs={'pk': self.kwargs.get('pk')})
        return reverse_lazy('negocios:document_detail', kwargs={'pk': self.object.document.pk})



class DocumentFileUpdateView(LoginRequiredMixin, UpdateView):
    model = DocumentFile
    form_class = DocumentFileForm
    template_name = 'negocios/document_file_form.html'

    def get_context_data(self, **kwargs):
        """Добавляем document в контекст, корректно получая его через связанный DocumentFile"""
        context = super().get_context_data(**kwargs)
        document_file = self.get_object()  # Получаем текущий файл
        context['document'] = document_file.document  # Берём связанный документ
        return context

    def get_success_url(self):
        return reverse_lazy('negocios:document_detail', kwargs={'pk': self.object.document.pk})


class DocumentFileDeleteView(LoginRequiredMixin, DeleteView):
    model = DocumentFile
    template_name = 'negocios/document_file_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('negocios:document_detail', kwargs={'pk': self.object.document.pk})


def download_all_files(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    files = DocumentFile.objects.filter(document__business=business)

    # Создаем архив во временной памяти
    zip_filename = f"{business.business_text}_files.zip"
    response = HttpResponse(content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="{zip_filename}"'

    with zipfile.ZipFile(response, 'w') as zip_file:
        for file in files:
            if file.file:  # Проверяем, есть ли файл
                file_path = file.file.path  # Физический путь к файлу
                file_name = os.path.basename(file_path)  # Имя файла
                zip_file.write(file_path, file_name)

    return response

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Document, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, document=f)
        comment.save()
        return redirect(reverse('negocios:document_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "negocios/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        if self.object.document:
            return reverse('negocios:document_detail', args=[self.object.document.id])
        return reverse('negocios:document_list')  # Подставь URL на список документов


class DocumentStatusUpdateView(View):
    def post(self, request, pk):
        document = get_object_or_404(Document, id=pk)
        new_status = request.POST.get('status')

        if new_status in ['pending', 'approved']:  # Проверяем корректность
            document.status = new_status
            document.save()

        return redirect('negocios:document_detail', pk=pk)




def assign_upload_responsible(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if request.user != document.owner:
        messages.error(request, "Você não tem permissão para designar um responsável pelo upload.")
        return redirect('negocios:document_detail', pk=pk)

    if request.method == "POST":
        user_id = request.POST.get("upload_responsible")
        user = get_object_or_404(User, pk=user_id)
        document.upload_responsible = user
        document.save()
        messages.success(request, f"Responsável pelo upload designado: {user.username}")

    return redirect('negocios:document_detail', pk=pk)


def assign_approval_responsible(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if request.user != document.owner:
        messages.error(request, "Você não tem permissão para designar um responsável pela aprovação.")
        return redirect('negocios:document_detail', pk=pk)

    if request.method == "POST":
        user_id = request.POST.get("approval_responsible")
        user = get_object_or_404(User, pk=user_id)
        document.approval_responsible = user
        document.save()
        messages.success(request, f"Responsável pela aprovação designado: {user.username}")

    return redirect('negocios:document_detail', pk=pk)


class ReportPreviewView(LoginRequiredMixin, TemplateView):
    template_name = 'negocios/report_preview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email_body, has_data = generate_report_body()
        context['report'] = email_body
        context['has_data'] = has_data
        return context