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
