


# from django.db import models
# from django.utils import timezone
# from django.utils.crypto import get_random_string


# class ContactInfo(models.Model):
#     """
#     Stores user contact/session information.
#     """
#     CONTACT_TYPE_CHOICES = [
#         ('phone', 'Phone'),
#         ('email', 'Email'),
#         ('both', 'Phone + Email'),
#         ('temp', 'Temporary'),
#     ]

#     token_number = models.CharField(
#         max_length=30, unique=True, db_index=True, blank=True,
#         help_text="Unique token for each session/user"
#     )
#     session_key = models.CharField(
#         max_length=40, blank=True, null=True, db_index=True,
#         help_text="Django session key"
#     )
#     contact_type = models.CharField(
#         max_length=10, choices=CONTACT_TYPE_CHOICES, default="temp"
#     )
#     contact_value = models.CharField(
#         max_length=255, blank=True, null=True,
#         help_text="Primary identifier (phone/email/both/temp)"
#     )

#     # ---- Tracking fields ----
#     ip_address = models.GenericIPAddressField(blank=True, null=True)
#     location_city = models.CharField(max_length=100, blank=True, null=True)
#     location_region = models.CharField(max_length=100, blank=True, null=True)
#     location_country = models.CharField(max_length=100, blank=True, null=True)

#     mobile = models.CharField(max_length=15, blank=True, null=True)
#     email = models.EmailField(blank=True, null=True)
#     page_views = models.PositiveIntegerField(default=0, help_text="Number of pages visited")

#     created_at = models.DateTimeField(auto_now_add=True)
#     last_active = models.DateTimeField(default=timezone.now)
#     is_seen = models.BooleanField(default=False)

#     # ---- helper fields for analytics ----
#     user_agent = models.CharField(max_length=255, blank=True, null=True)
#     referrer = models.CharField(max_length=255, blank=True, null=True)

#     def _generate_token(self):
#         """Generate unique session token."""
#         dt = timezone.now().strftime("%Y%m%d")
#         rand = get_random_string(5).upper()
#         return f"UTS-{dt}-{rand}"

#     def save(self, *args, **kwargs):
#         """Auto-generate token and detect contact type before saving."""
#         if not self.token_number:
#             self.token_number = self._generate_token()

#         if self.mobile and self.email:
#             self.contact_type = "both"
#             self.contact_value = f"{self.mobile} | {self.email}"
#         elif self.mobile:
#             self.contact_type = "phone"
#             self.contact_value = self.mobile
#         elif self.email:
#             self.contact_type = "email"
#             self.contact_value = self.email
#         else:
#             self.contact_type = "temp"
#             self.contact_value = self.token_number  # fallback

#         # update last active
#         self.last_active = timezone.now()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         who = self.mobile or self.email or self.token_number or 'Unknown'
#         loc = self.location_city or self.location_country or 'No Location'
#         return f"{who} ({self.ip_address or 'No IP'} | {loc})"

#     # --------------------
#     # 🔥 Helper methods for dashboard stats
#     # --------------------
#     @staticmethod
#     def total_visitors():
#         return ContactInfo.objects.count()

#     @staticmethod
#     def total_leads():
#         return ContactInfo.objects.exclude(contact_type="temp").count()

#     @staticmethod
#     def visitors_by_day(days=7):
#         """Return visitors count for last `days` days (list)."""
#         today = timezone.now().date()
#         data = []
#         for i in range(days - 1, -1, -1):
#             day = today - timezone.timedelta(days=i)
#             count = ContactInfo.objects.filter(created_at__date=day).count()
#             data.append({"date": str(day), "count": count})
#         return data


# class Message(models.Model):
#     """
#     Stores chat messages (User, Bot, Admin, System).
#     """
#     SENDER_CHOICES = [
#         ('user', '🧑 User'),
#         ('bot', '🤖 Bot'),
#         ('admin', '🛠 Admin'),
#         ('system', '⚙ System'),
#     ]

#     contact = models.ForeignKey(
#         ContactInfo,
#         on_delete=models.CASCADE,
#         related_name="messages",
#         null=True,
#         blank=True,
#     )
#     sender = models.CharField(max_length=20, choices=SENDER_CHOICES, default="user")
#     text = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)

#     class Meta:
#         ordering = ['timestamp']

#     def __str__(self):
#         icon = dict(self.SENDER_CHOICES).get(self.sender, "💬")
#         return f"{icon} [{self.sender}] {self.text[:40]}..."

#     # --------------------
#     # 🔥 Helper methods for dashboard stats
#     # --------------------
#     @staticmethod
#     def total_messages():
#         return Message.objects.count()

#     @staticmethod
#     def total_chats():
#         return Message.objects.filter(sender="user").count()

#     @staticmethod
#     def unread_messages():
#         return Message.objects.filter(is_read=False).count()





from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

# ===========================
# 🔑 Website Registration (Multi-Website Support)
# ===========================
class WebsiteRegistration(models.Model):
    website_id = models.CharField(max_length=12, unique=True, db_index=True, blank=True)
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



# ===========================
# 🤖 Bot Responses (Per Website)
# ===========================
class BotResponse(models.Model):
    website = models.ForeignKey(
        WebsiteRegistration,
        on_delete=models.CASCADE,
        related_name="bot_responses"
    )
    keyword = models.CharField(max_length=100, db_index=True)
    reply = models.TextField()

    class Meta:
        unique_together = ("website", "keyword")  # har website ka keyword unique ho
        ordering = ["keyword"]

    def __str__(self):
        return f"[{self.website.website_id}] {self.keyword}"

