from negocios.models import Business, Document, Comment

def generate_report_body():
    businesses = Business.objects.all()
    email_body = "   quando o aplicativo for implementado o email vai ser enviado diariamente deste jeito\n Bom dia!\n \nSegue lista de documentos pendentes:\n\n"
    has_pending_documents = False

    for business in businesses:
        pending_documents = Document.objects.filter(business=business, status='pending')

        if pending_documents.exists():
            has_pending_documents = True
            email_body += f" 📂  Negócio: {business.business_text}\n"

            for doc in pending_documents:
                upload_responsible = doc.upload_responsible.username if doc.upload_responsible else "Não atribuído"
                approval_responsible = doc.approval_responsible.username if doc.approval_responsible else "Não atribuído"

                email_body += (f"  📄 - {doc.document_text} (Criado: {doc.pub_date.strftime('%d/%m/%Y')})"
                               f"     👤 Responsável por Upload: {upload_responsible}"
                               f"     👤Responsável por Aprovação: {approval_responsible}\n")

                comments = Comment.objects.filter(document=doc).order_by("created_at")
                if comments.exists():
                    email_body += "    💬 Comentários:\n"
                    for comment in comments:
                        email_body += f"      - {comment.text} (de {comment.owner.username}, {comment.created_at.strftime('%d/%m/%Y %H:%M')})\n"

                last_file = doc.files.order_by('-pub_date').first()
                if last_file:
                    email_body += f"    📎 Último arquivo anexado: {last_file.pub_date.strftime('%d/%m/%Y %H:%M')}\n"

                email_body += "\n"

    return email_body, has_pending_documents
