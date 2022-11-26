from django.core.mail import EmailMessage

from backend import settings


class Utils():
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            from_email=settings.EMAIL_HOST_USER,
            to=[data['to_email']]
        )
        print('hello')
        email.send()
