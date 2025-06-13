from django.db import models

# bot/models.py

class TelegramUser(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=150, null=True, blank=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    full_name = models.CharField(max_length=150, null=True, blank=True)  # Foydalanuvchi kiritgan ism
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    language = models.CharField(max_length=5, null=True, blank=True)
    is_registered = models.BooleanField(default=False)  # ✅ yangi
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username or str(self.chat_id)

