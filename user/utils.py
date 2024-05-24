from user.models import User
from django.conf import settings
from django.template.loader import get_template, render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives

def send_email_token(obj, token):
    try:
        subject = 'Welcome to Software Marketplace App'
        username = obj['username']
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [obj['email'], ]
        #print(email_from, recipient_list, token)
        message = f'Hi {username}, thank you for registering.\nPlease verify your email by clicking on the link below\nhttp://localhost:8000/user/verify/{token}'
        send_mail(subject, message, email_from, recipient_list)
        '''html_message = render_to_string('templates/email.html', {'username': username, 'token': token, 'domain': 'http://localhost:8000'})
        msg = EmailMultiAlternatives(subject, message, email_from, recipient_list)
        msg.attach_alternative(html_message, "text/html")
        msg.send()'''
    except Exception as e:
        print(e)
        return False