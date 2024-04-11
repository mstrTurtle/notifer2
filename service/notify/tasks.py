# tasks.py

from django_q.tasks import async_task
from .models import Message, Event
from django.core.mail import send_mail
from django.utils import timezone

def send_notification(message_id):
    print('in send_notification')
    try:
        message = Message.objects.get(id=message_id)
        send_mail(
            'Notification',
            message.email_content,
            '769711153@qq.com',  # Replace with actual sender email
            ['769711153@qq.com'],  # Replace with actual recipient email
            fail_silently=False,
        )
        Event.objects.create(message=message)
    except Message.DoesNotExist:
        raise Message.DoesNotExist

def check_and_send_notifications():
    print('in check_and_send_notifications')
    current_time = timezone.now()
    current_minute = current_time.strftime('%Y-%m-%d %H:%M')
    
    messages_to_send = Message.objects.filter(send_time=current_minute)
    
    for message in messages_to_send:
        async_task(send_notification, message.id)


