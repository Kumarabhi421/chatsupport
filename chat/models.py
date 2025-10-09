
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

# ===========================
# 🔑 Website Registration (Multi-Website Support)
# ===========================
class WebsiteRegistration(models.Model):
    website_id = models.CharField(max_length=12, primary_key=True, blank=True)  # ✅ string primary key
    website_url = models.URLField(unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.website_id:
            rand = get_random_string(6).upper()
            self.website_id = f"WEB-{rand}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.website_url} ({self.website_id})"


# ===========================
# 🧑 Contact / Visitor Info
# ===========================
class ContactInfo(models.Model):
    CONTACT_TYPE_CHOICES = [
        ("phone", "Phone"),
        ("email", "Email"),
        ("both", "Phone + Email"),
        ("temp", "Temporary"),
    ]

    website = models.ForeignKey(
        WebsiteRegistration,
        to_field="website_id",  # ✅ use string primary key
        on_delete=models.CASCADE,
        related_name="contacts",
        null=True,
        blank=True
    )
    token_number = models.CharField(max_length=30, unique=True, db_index=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPE_CHOICES, default="temp")
    contact_value = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=255, null=True, blank=True)

    mobile = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    page_views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(default=timezone.now)
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.TextField(blank=True, null=True)
    is_seen = models.BooleanField(default=False)

    def _generate_token(self):
        dt = timezone.now().strftime("%Y%m%d")
        rand = get_random_string(5).upper()
        return f"VIS-{dt}-{rand}"

    def save(self, *args, **kwargs):
        if not self.token_number:
            self.token_number = self._generate_token()

        if self.mobile and self.email:
            self.contact_type = "both"
            self.contact_value = f"{self.mobile} | {self.email}"
        elif self.mobile:
            self.contact_type = "phone"
            self.contact_value = self.mobile
        elif self.email:
            self.contact_type = "email"
            self.contact_value = self.email
        else:
            self.contact_type = "temp"
            self.contact_value = self.token_number

        self.last_active = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.contact_value or self.token_number} ({self.ip_address or 'No IP'})"

    @staticmethod
    def total_visitors():
        return ContactInfo.objects.count()

    @staticmethod
    def total_leads():
        return ContactInfo.objects.exclude(contact_type="temp").count()

    @staticmethod
    def visitors_by_day(days=7):
        today = timezone.now().date()
        data = []
        for i in range(days - 1, -1, -1):
            day = today - timezone.timedelta(days=i)
            count = ContactInfo.objects.filter(created_at__date=day).count()
            data.append({"date": str(day), "count": count})
        return data


# ===========================
# 💬 Chat & Messages
# ===========================
class Chat(models.Model):
    chat_id = models.CharField(max_length=100, unique=True)
    contact = models.ForeignKey(ContactInfo, on_delete=models.CASCADE, related_name="chats")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.chat_id}"

    @staticmethod
    def total_chats():
        return Chat.objects.count()


class Message(models.Model):
    SENDER_CHOICES = [
        ("user", "User"),
        ("bot", "Bot"),
        ("admin", "Admin"),
        ("system", "System"),
    ]
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES, default="user")
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender}: {self.text[:40]}"

    @staticmethod
    def total_messages():
        return Message.objects.count()

    @staticmethod
    def unread_messages():
        return Message.objects.filter(is_read=False).count()


# ===========================
# 📊 Page Views & Visitor Logs
# ===========================
class PageView(models.Model):
    contact = models.ForeignKey(ContactInfo, on_delete=models.CASCADE, related_name="pageviews")
    url = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.contact} visited {self.url}"


class VisitorLog(models.Model):
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.ip_address} ({self.timestamp})"





class BotResponse(models.Model):
    website = models.ForeignKey(
        WebsiteRegistration,
        to_field="website_id",  # ✅ string ForeignKey
        on_delete=models.CASCADE,
        related_name="bot_responses"
    )
    keyword = models.CharField(max_length=100, db_index=True)
    reply = models.TextField()

    class Meta:
        unique_together = ("website", "keyword")
        ordering = ["keyword"]

    def __str__(self):
        return f"[{self.website.website_id}] {self.keyword}"
