from django.urls import path,  reverse_lazy
from . import views
from .views import (
    BusinessListView, BusinessDetailView, BusinessCreateView, BusinessUpdateView, BusinessDeleteView,
    DocumentListView, DocumentDetailView, DocumentCreateView, DocumentUpdateView, DocumentDeleteView, DocumentFileUpdateView,
    DocumentFileDeleteView, DocumentFileCreateView, download_all_files, BusinessCreateViewProdutor, BusinessCreateViewEmpresa,
    CommentCreateView, CommentDeleteView, DocumentStatusUpdateView, assign_upload_responsible, assign_approval_responsible, ReportPreviewView )
from django.views.generic import TemplateView
app_name = 'negocios'

urlpatterns = [
    # Business URLs
    path('', BusinessListView.as_view(), name='business_list'),
    path('<int:pk>/delete/', BusinessDeleteView.as_view(), name='business_delete'),
    path('create/', BusinessCreateView.as_view(), name='business_create'),
    path('create_produtor/', BusinessCreateViewProdutor.as_view(), name='business_create_produtor'),
    path('create_empresa/', BusinessCreateViewEmpresa.as_view(), name='business_create_empresa'),
    path('<int:pk>/update/', BusinessUpdateView.as_view(), name='business_update'),
    path('<int:pk>/', BusinessDetailView.as_view(), name='business_detail'),


    # Document URLs
    path('documents/', DocumentListView.as_view(), name='document_list'),
    path('documents/<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('documents/create/', DocumentCreateView.as_view(), name='document_create'),
    path('documents/<int:pk>/update/', DocumentUpdateView.as_view(), name='document_update'),
    path('documents/<int:pk>/delete/', DocumentDeleteView.as_view(), name='document_delete'),

# Document File URLs
    path('documents/files/<int:pk>/update/', DocumentFileUpdateView.as_view(), name='document_file_update'),
    path('documents/files/<int:pk>/delete/', DocumentFileDeleteView.as_view(), name='document_file_delete'),
    path('documents/<int:pk>/add-file/', DocumentFileCreateView.as_view(), name='document_file_upload'),

    path('business/<int:business_id>/download/', download_all_files, name='download_all_files'),

    path('document/<int:pk>/comment',
        views.CommentCreateView.as_view(), name='document_comment_create'),
    path('comment/<int:pk>/delete',
        views.CommentDeleteView.as_view(success_url=reverse_lazy('forums:all')), name='document_comment_delete'),
    path('document/<int:pk>/update-status/', DocumentStatusUpdateView.as_view(), name='document_status_update'),
    # path('document/<int:pk>/', document_detail, name='document_detail'),
    path('document/<int:pk>/assign-upload/', assign_upload_responsible, name='document_assign_upload_responsible'),
    path('document/<int:pk>/assign-approval/', assign_approval_responsible,
         name='document_assign_approval_responsible'),
    path('report-preview/', ReportPreviewView.as_view(), name='report_preview'),


]