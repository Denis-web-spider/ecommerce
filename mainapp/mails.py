from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings

def send_return_letter_mail_for_admin(return_letter):
    mail_context = {'return_letter': return_letter}

    text_mail_template = get_template('mails/return_letter_mails/return_letter_mail.txt')
    html_mail_template = get_template('mails/return_letter_mails/return_letter_mail.html')

    text_mail = text_mail_template.render(mail_context)
    html_mail = html_mail_template.render(mail_context)

    send_mail(
        subject=f'Заявление на возврат от {return_letter.first_name} {return_letter.last_name}',
        from_email=None,
        recipient_list=[settings.ADMIN_EMAIL],
        message=text_mail,
        html_message=html_mail,
    )
