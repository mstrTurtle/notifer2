from django.db import models

# Create your models here.

class Message(models.Model):
    send_time = models.DateTimeField()
    email_title = models.TextField()
    email_content = models.TextField()
    status = models.TextField()

    def __str__(self):
        return f"Message {self.email_title} {self.status} at {self.send_time}"

    def __lt__(self, other):
        return self.send_time < other.send_time


class Event(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    detail = models.TextField()
    event_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Event at {self.event_time} said {self.detail} for {self.message}"
