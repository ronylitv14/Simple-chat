from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Thread(models.Model):
    participants = models.ManyToManyField(User, related_name="participants", blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    text = models.TextField()
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='thread')
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def clean(self):
        if not self.thread.participants.filter(id=self.sender.id).exists():
            raise ValidationError("Sender must be a participant of the thread.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Message from {self.sender.username} in {self.thread}'
