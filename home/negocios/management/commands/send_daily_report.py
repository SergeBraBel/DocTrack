from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
import sys
from negocios.utils.reports import generate_report_body
sys.path.append("C:/Users/sdemi/PycharmProjects/Barter/home")
from negocios.models import Business, Document, Comment, ReportRecipient


class Command(BaseCommand):
    help = "Envia boletim informativo diário sobre documentos não aprovados"

    def handle(self, *args, **kwargs):
        recipients = ReportRecipient.objects.values_list("email", flat=True) if ReportRecipient.objects.exists() else settings.DAILY_REPORT_RECIPIENTS

        if not recipients:
            self.stdout.write(self.style.WARNING("A lista de destinatários está vazia!"))
            return

        email_body, has_pending_documents = generate_report_body()
        subject = "📢 Relatório diário sobre documentos não aprovados"

        if has_pending_documents:
            send_mail(subject, email_body, settings.DEFAULT_FROM_EMAIL, recipients, fail_silently=False)
            self.stdout.write(self.style.SUCCESS("O envio foi feito com sucesso!"))
        else:
            self.stdout.write(self.style.WARNING("Não há documentos descoordenados. O mailing não foi enviado."))

#
# class Command(BaseCommand):
#     help = "Envia boletim informativo diário sobre documentos não aprovados"
#
#     def handle(self, *args, **kwargs):
#         # Получаем список e-mail'ов из базы или settings
#         recipients = ReportRecipient.objects.values_list("email",
#                                                          flat=True) if ReportRecipient.objects.exists() else settings.DAILY_REPORT_RECIPIENTS
#
#         if not recipients:
#             self.stdout.write(self.style.WARNING("A lista de destinatários está vazia!"))
#             return
#
#         businesses = Business.objects.all()
#         email_subject = "📢 Relatório diário sobre documentos não aprovados"
#         email_body = "Bom dia!\n\nSegue lista de documentos não aprovados:\n\n"
#
#         has_pending_documents = False
#         for business in businesses:
#             pending_documents = Document.objects.filter(business=business, status='pending')
#
#             if pending_documents.exists():
#                 has_pending_documents = True
#                 email_body += f"📌 Negócio: {business.business_text}\n"
#
#                 for doc in pending_documents:
#                     # Получаем ответственных за загрузку и согласование
#                     upload_responsible = doc.upload_responsible.username if doc.upload_responsible else "Não atribuído"
#                     approval_responsible = doc.approval_responsible.username if doc.approval_responsible else "Não atribuído"
#
#                     # Добавляем информацию в отчет
#                     email_body += (f"  - {doc.document_text} (Criado: {doc.pub_date.strftime('%d/%m/%Y')})\n"
#                                    f"    📌 Responsável por Upload: {upload_responsible}\n"
#                                    f"    ✅ Responsável por Aprovação: {approval_responsible}\n")
#
#                     # Добавляем комментарии
#                     comments = Comment.objects.filter(document=doc).order_by("created_at")
#                     if comments.exists():
#                         email_body += "    💬 Comentários:\n"
#                         for comment in comments:
#                             email_body += f"      - {comment.text} (de {comment.owner.username}, {comment.created_at.strftime('%d/%m/%Y %H:%M')})\n"
#
#                     # Проверяем, есть ли прикрепленные файлы
#                     last_file = doc.files.order_by('-pub_date').first()
#                     if last_file:
#                         email_body += f"    📎 Último arquivo anexado: {last_file.pub_date.strftime('%d/%m/%Y %H:%M')}\n"
#
#                     email_body += "\n"
#
#         if has_pending_documents:
#             send_mail(
#                 email_subject,
#                 email_body,
#                 settings.DEFAULT_FROM_EMAIL,
#                 recipients,
#                 fail_silently=False,
#             )
#             self.stdout.write(self.style.SUCCESS("O envio foi feito com sucesso!"))
#         else:
#             self.stdout.write(self.style.WARNING("Não há documentos descoordenados. O mailing não foi enviado."))
#
