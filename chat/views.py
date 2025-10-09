

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.http import JsonResponse, StreamingHttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
from rest_framework import generics
import json, difflib, re
from queue import Queue
from .models import ( Message, ContactInfo, WebsiteRegistration, Chat, BotResponse)
from .serializers import MessageSerializer, WebsiteRegistrationSerializer

from .models import WebsiteRegistration, BotResponse



# ================= CONTACT INFO EXTRACTION =================
def extract_contact_info(text: str):
    mobile_pattern = r"\b\d{10}\b"
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    mobile = re.search(mobile_pattern, text)
    mobile = mobile.group(0) if mobile else None
    email_match = re.search(email_pattern, text)
    email = email_match.group(0) if email_match else None
    if email:
        try:
            validate_email(email)
        except ValidationError:
            email = None
    return mobile, email

# ================= FRONT VIEWS =================
def chat_view(request):
    website_id = request.GET.get('website_id', 'local')
    return render(request, "chat.html", {"website_id": website_id})

# ================= WEBSITE ADMIN REGISTER =================
def website_admin_register(request):
    if request.method == "POST":
        url = (request.POST.get("website_url") or "").strip()
        email = (request.POST.get("email") or "").strip()
        pwd = (request.POST.get("password") or "").strip()

        if not url or not email or not pwd:
            messages.error(request, "All fields are required for registration.")
            return redirect("website_admin_login")

        if WebsiteRegistration.objects.filter(website_url__iexact=url).exists():
            messages.error(request, "Website already registered.")
            return redirect("website_admin_login")
        if WebsiteRegistration.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("website_admin_login")

        website_id = get_random_string(10)
        website = WebsiteRegistration(
            website_id=website_id,
            website_url=url,
            email=email,
            password=make_password(pwd)
        )
        website.save()
        messages.success(request, "Registration successful! Please login now.")
        return redirect("website_admin_login")
    return redirect("website_admin_login")

# ================= WEBSITE ADMIN LOGIN =================
def website_admin_login(request):
    if request.method == "POST":
        site_input = (request.POST.get("website_url") or "").strip()
        pwd = (request.POST.get("password") or "").strip()

        if not site_input or not pwd:
            messages.error(request, "Please provide website URL/ID and password.")
            return render(request, "chat/website_admin_login.html")

        website = WebsiteRegistration.objects.filter(website_url__iexact=site_input).first()
        if not website:
            website = WebsiteRegistration.objects.filter(website_id__iexact=site_input).first()
        if not website:
            messages.error(request, "Website not found.")
            return render(request, "chat/website_admin_login.html", {"website_url": site_input})

        if check_password(pwd, website.password):
            request.session["website_admin_id"] =  website.website_id
            request.session["website_admin_url"] = website.website_url
            request.session["website_admin_login_at"] = str(timezone.now())
            return redirect("admin_panel")
        else:
            messages.error(request, "Invalid password.")
            return render(request, "chat/website_admin_login.html", {"website_url": site_input})

    return render(request, "chat/website_admin_login.html")

# ================= WEBSITE ADMIN LOGOUT =================
def website_admin_logout(request):
    request.session.flush()
    messages.info(request, "Logged out.")
    return redirect("website_admin_login")

# ================= ADMIN PANEL (Protected) =================
def admin_panel_view(request):
    website_id = request.session.get("website_admin_id")
    if not website_id:
        return redirect("website_admin_login")

    try:
        # Use custom string field, not auto-increment PK
        website = WebsiteRegistration.objects.get(website_id=website_id)
    except WebsiteRegistration.DoesNotExist:
        request.session.flush()
        return redirect("website_admin_login")

    contacts = ContactInfo.objects.filter(
        website=website
    ).prefetch_related("messages").order_by("-created_at")

    return render(request, 'chat/admin_panel.html', {
    "contacts": contacts,
    "website": website,
    "website_id": website.website_id  # ✅ ye hona chahiye
})
# ================= SSE STREAM =================
# Website-wise admin subscribers
subscribers_admin = {}  # { website_id: set(Queue) }
subscribers_user = {}   # { contact_id: set(Queue) }

# ===================================================
# ✅ Broadcast for Admin (Website-wise isolation)
# ===================================================
def _broadcast_admin(payload: dict, website_id=None):
    if not website_id:
        return
    if website_id not in subscribers_admin:
        return

    dead = []
    for q in list(subscribers_admin[website_id]):
        try:
            q.put(payload, timeout=0.1)
        except Exception:
            dead.append(q)
    for q in dead:
        subscribers_admin[website_id].discard(q)

# ===================================================
# ✅ Broadcast for User (as per contact_id)
# ===================================================
def _broadcast_user(contact_id, payload: dict):
    if contact_id not in subscribers_user:
        return

    dead = []
    for q in list(subscribers_user[contact_id]):
        try:
            q.put(payload, timeout=0.1)
        except Exception:
            dead.append(q)
    for q in dead:
        subscribers_user[contact_id].discard(q)

# ===================================================
# ✅ Admin Stream (per-website connection)
# ===================================================
def lead_stream(request):
    website_id = request.GET.get("website_id")
    if not website_id:
        return JsonResponse({"error": "Missing website_id"}, status=400)

    def event_stream():
        q = Queue()
        subscribers_admin.setdefault(website_id, set()).add(q)
        try:
            yield "event: ping\ndata: {}\n\n"
            while True:
                data = q.get()
                yield f"data: {json.dumps(data)}\n\n"
        except GeneratorExit:
            pass
        finally:
            subscribers_admin[website_id].discard(q)

    resp = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    resp["Cache-Control"] = "no-cache"
    return resp

# ===================================================
# ✅ User Stream (per-contact)
# ===================================================
def user_stream(request, contact_id):
    def event_stream():
        q = Queue()
        subscribers_user.setdefault(int(contact_id), set()).add(q)
        try:
            yield "event: ping\ndata: {}\n\n"
            while True:
                data = q.get()
                yield f"data: {json.dumps(data)}\n\n"
        except GeneratorExit:
            pass
        finally:
            subscribers_user[int(contact_id)].discard(q)

    resp = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    resp["Cache-Control"] = "no-cache"
    return resp

# ===================================================
# ✅ CONTACT / CHAT LOGIC
# ===================================================
SERVER_START_TIME = timezone.now()

# def _get_or_create_contact(request, website_id=None) -> tuple:
#     if not request.session.session_key:
#         request.session.create()

#     contact_id = request.session.get("contact_id")
#     session_start = request.session.get("session_start")

#     website = None
#     if website_id:
#         website = WebsiteRegistration.objects.filter(website_id=website_id).first()

#     contact = ContactInfo.objects.filter(id=contact_id).first() if contact_id else None

#     if (not contact) or (not session_start) or (timezone.datetime.fromisoformat(session_start) < SERVER_START_TIME):
#         contact = ContactInfo.objects.create(contact_type="temp", website=website)
#         request.session["contact_id"] = contact.id
#         request.session["session_start"] = str(SERVER_START_TIME)
#         request.session["ask_count"] = 0
#         request.session["contact_saved"] = False

#     chat = Chat.objects.filter(contact=contact).last()
#     if not chat:
#         chat = Chat.objects.create(
#             chat_id=f"CHAT-{contact.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
#             contact=contact
#         )

#     return contact, chat

# ===================================================
# ✅ CHAT API
# ===================================================
# ================= CHAT API =================
@csrf_exempt
def get_response(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_message = (data.get('message') or "").strip()
    website_id = data.get("website_id")
    sender = (data.get('sender') or 'user').lower()
    contact, chat = _get_or_create_contact(request, website_id=website_id)

    # ================= User Message =================
    if user_message:
        msg = Message.objects.create(sender=sender, text=user_message, chat=chat)
        payload_user = {
            "id": msg.id,
            "contact_id": contact.id,
            "token": f"TKN-{contact.id}",
            "sender": sender,
            "text": user_message,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
        }
        # ✅ Broadcast only to admins of this website
        _broadcast_admin(payload_user, website_id=website_id)

    # ================= Contact Info Check =================
    if not request.session.get("contact_saved", False):
        mobile, email = extract_contact_info(user_message)
        if mobile or email:
            if mobile:
                contact.mobile = mobile
                contact.contact_type = "phone"
                contact.contact_value = mobile
            elif email:
                contact.email = email
                contact.contact_type = "email"
                contact.contact_value = email
            contact.save()
            request.session["contact_saved"] = True
            reply = "✅ Thanks! Your contact info has been saved — we’ll contact you shortly."
        else:
            ask_count = request.session.get("ask_count", 0)
            if ask_count < 3:
                request.session["ask_count"] = ask_count + 1
                reply = "🙏 Please share your phone or email so we can assist you better."
            else:
                request.session["contact_saved"] = True
                reply = "Alright 👍 let's continue."
    else:
        reply = _best_reply(user_message.lower(), website_id=website_id)

    # ================= Bot Reply =================
    bot_msg = Message.objects.create(sender="bot", text=reply, chat=chat)
    payload_bot = {
        "id": bot_msg.id,
        "contact_id": contact.id,
        "token": f"TKN-{contact.id}",
        "sender": "bot",
        "text": reply,
        "timestamp": bot_msg.timestamp.strftime("%Y-%m-%d %H:%M"),
    }

    _broadcast_admin(payload_bot, website_id=website_id)
    _broadcast_user(contact.id, payload_bot)

    return JsonResponse({
        "reply": reply,
        "contact_id": contact.id,
        "token": f"TKN-{contact.id}"
    })


# ================= ADMIN REPLY =================
@csrf_exempt
def admin_reply(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    contact_id = data.get("contact_id")
    token = data.get("token") or data.get("token_number")
    message = (data.get("message") or "").strip()
    website_id = data.get("website_id")

    if not (contact_id or token) or not message:
        return JsonResponse({"error": "Missing contact_id/token or message"}, status=400)

    contact = None

    # ✅ Fetch contact by ID + website
    if contact_id:
        contact = ContactInfo.objects.filter(
            id=int(contact_id),
            website__website_id=website_id
        ).first()

    # ✅ Fetch contact by Token + website
    elif token:
        if isinstance(token, str) and token.upper().startswith("TKN-"):
            try:
                possible_id = int(token.split("-", 1)[1])
                contact = ContactInfo.objects.filter(
                    id=possible_id,
                    website__website_id=website_id
                ).first()
            except Exception:
                pass

        if not contact:
            contact = ContactInfo.objects.filter(
                token_number=token,
                website__website_id=website_id
            ).first()

    if not contact:
        return JsonResponse({"error": "Contact not found"}, status=404)

    # ✅ Create admin message
    chat = Chat.objects.filter(contact=contact).last()
    if not chat:
        chat = Chat.objects.create(
            chat_id=f"CHAT-{contact.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            contact=contact
        )

    msg = Message.objects.create(sender="admin", text=message, chat=chat)
    payload = {
        "id": msg.id,
        "contact_id": contact.id,
        "token": f"TKN-{contact.id}",
        "sender": "admin",
        "text": message,
        "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
    }

    _broadcast_admin(payload, website_id=website_id)
    _broadcast_user(contact.id, payload)

    return JsonResponse({"status": "success", "message_id": msg.id})


# alias
admin_send_message = admin_reply

# ================= MESSAGES API =================
class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        website_id = self.request.GET.get("website_id")
        qs = Message.objects.all().order_by('-timestamp')
        if website_id:
            qs = qs.filter(chat__contact__website_id=website_id)
        return qs

# ================= CONTACT API =================
@csrf_exempt
@csrf_exempt
def save_contact(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request"}, status=405)

    try:
        if request.content_type and "application/json" in request.content_type:
            data = json.loads(request.body or "{}")
            contact_value = data.get("contact_value")
            contact_type = data.get("contact_type", "temp")
            website_id = data.get("website_id")
        else:
            contact_value = request.POST.get("contact_value")
            contact_type = request.POST.get("contact_type", "temp")
            website_id = request.POST.get("website_id")
    except json.JSONDecodeError:
        contact_value, contact_type, website_id = None, "temp", None

    contact, chat = _get_or_create_contact(request, website_id=website_id)

    if contact_value:
        if contact_type == "phone":
            contact.mobile = contact_value
        elif contact_type == "email":
            contact.email = contact_value

        contact.contact_value = contact_value
        contact.contact_type = contact_type

        if website_id:
            website = WebsiteRegistration.objects.filter(website_id=website_id).first()
            if website:
                contact.website = website

        contact.save()
        request.session["contact_saved"] = True

    return JsonResponse({"status": "success", "id": contact.id, "token": f"TKN-{contact.id}"})


def get_contacts(request):
    website_id = request.GET.get("website_id")
    contacts_qs = ContactInfo.objects.all().order_by("-created_at")
    if website_id:
        contacts_qs = contacts_qs.filter(website__website_id=website_id)

    contacts = list(contacts_qs.values(
        "id", "token_number", "mobile", "email", "contact_value", "created_at", "is_seen"
    ))

    for c in contacts:
        c["token"] = c.get("token_number") or f"TKN-{c['id']}"

    return JsonResponse({"contacts": contacts})


def get_messages(request, contact_id):
    website_id = request.GET.get("website_id")

    try:
        contact_qs = ContactInfo.objects.filter(id=contact_id)
        if website_id:
            contact_qs = contact_qs.filter(website__website_id=website_id)

        contact = contact_qs.first()
        if not contact:
            return JsonResponse({"error": "Contact not found"}, status=404)

        messages_qs = Message.objects.filter(chat__contact=contact).order_by("timestamp")
        data = [
            {
                "id": msg.id,
                "sender": msg.sender.lower(),
                "text": msg.text,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
            }
            for msg in messages_qs
        ]
        return JsonResponse({
            "messages": data,
            "token": f"TKN-{contact.id}",
            "token_number": contact.token_number,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# ================= STATS API =================

from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime
from calendar import monthrange
from .models import ContactInfo, Message

def stats(request):
    website_id = request.GET.get("website_id")
    
    # ✅ Base querysets
    contacts_qs = ContactInfo.objects.all()
    messages_qs = Message.objects.all()

    if website_id:
        contacts_qs = contacts_qs.filter(website__website_id=website_id)
        messages_qs = messages_qs.filter(chat__contact__website__website_id=website_id)

    # ✅ Totals
    total_contacts = contacts_qs.count()
    total_messages = messages_qs.count()
    total_visitors = contacts_qs.values("contact_value").distinct().count()
    total_chats = messages_qs.values("chat__contact_id").distinct().count()

    page_views_agg = contacts_qs.aggregate(total=Sum('page_views'))
    total_pageviews = page_views_agg.get('total') or 0

    sender_stats = list(messages_qs.values("sender").annotate(total=Count("id")))

    # ================= Monthly Data =================
    now = timezone.now()
    months, visitors_data, chats_data, page_views_dist = [], [], [], []

    # Build last 6 months dynamically
    for i in range(5, -1, -1):
        # Get first and last day of month
        year = now.year
        month = now.month - i
        if month <= 0:
            month += 12
            year -= 1
        start_date = datetime(year, month, 1)
        end_day = monthrange(year, month)[1]
        end_date = datetime(year, month, end_day, 23, 59, 59)

        label = f"{year}-{month:02d}"
        months.append(label)

        # Visitors in month
        visitors_count = contacts_qs.filter(
            created_at__gte=start_date, created_at__lte=end_date
        ).count()
        visitors_data.append(visitors_count)

        # Messages in month
        chats_count = messages_qs.filter(
            timestamp__gte=start_date, timestamp__lte=end_date
        ).count()
        chats_data.append(chats_count)

        # Page views in month
        pv_count = contacts_qs.filter(
            created_at__gte=start_date, created_at__lte=end_date
        ).aggregate(total=Sum('page_views'))['total'] or 0
        page_views_dist.append(pv_count)

    # ✅ Feedback % calculation
    feedback_percent = (min(100, (total_contacts * 10) // total_messages) if total_messages else 0)

    # ✅ Return JSON
    return JsonResponse({
        "total_visitors": total_visitors,
        "total_chats": total_chats,
        "page_views_total": total_pageviews,
        "feedback_percent": feedback_percent,
        "contacts": total_contacts,
        "messages": total_messages,
        "sender_stats": sender_stats,
        "months": months,
        "visitors_data": visitors_data,
        "chats_data": chats_data,
        "page_views_dist": page_views_dist,
    })


# ================= ADMIN PANEL =================
def admin_panel(request):
    websites = WebsiteRegistration.objects.all()
    
    # Example: first website ko default select kar rahe hain
    selected_website = websites.first() if websites.exists() else None
    website_id = selected_website.website_id if selected_website else ""

    context = {
        "websites": websites,
        "website_id": website_id,   # ✅ Inject website_id to template
    }
    return render(request, "admin_panel.html", context)


# ================= WEBSITE SAVE =================
@csrf_exempt
def save_website(request):
    if request.method == "POST":
        website_url = request.POST.get("website_url")
        email = request.POST.get("email")
        password = request.POST.get("password")
        if not website_url or not email or not password:
            return JsonResponse({"status": "error", "message": "All fields required"}, status=400)
        website = WebsiteRegistration.objects.create(
            website_url=website_url,
            email=email,
            password=make_password(password)
        )
        return redirect("admin_panel")
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)




# ================= KEYWORD BOT =================
def _best_reply(user_message, website_id):
    """
    Get the best bot reply based on website_id
    Uses both exact keyword + fuzzy matching
    """

    # ✅ Step 1: Check exact BotResponse keyword match
    response = BotResponse.objects.filter(
        website__website_id=website_id,
        keyword__icontains=user_message
    ).first()
    if response:
        return response.reply

    # ✅ Step 2: Collect all website-specific bot responses
    responses = {}
    if website_id:
        try:
            website = WebsiteRegistration.objects.get(website_id=website_id)
            responses = {
                r.keyword.lower(): r.reply
                for r in website.bot_responses.all()
            }
        except WebsiteRegistration.DoesNotExist:
            pass

    # ✅ Step 3: If still no responses found → fallback defaults
    if not responses:
        responses = {
            "hello": "Hello! How can we help?",
            "hi": "Hi there! How can we assist you?",
            "contact": "You can contact us at info@urgentitsolution.com",
        }

    # ✅ Step 4: Fuzzy match (similar keywords)
    match = difflib.get_close_matches(user_message.lower(), responses.keys(), n=1, cutoff=0.6)
    if match:
        return responses[match[0]]

    # ✅ Step 5: Substring check
    for key, reply in responses.items():
        if key in user_message.lower():
            return reply

    # ✅ Step 6: Final fallback
    return "Hello! How can I help you?"

@csrf_exempt
def save_bot_response(request):
    if request.method == "POST":
        keyword = request.POST.get("keyword", "").strip()
        reply = request.POST.get("reply", "").strip()
        website_id = request.POST.get("website_id", "").strip()

        if not all([keyword, reply, website_id]):
            return JsonResponse({"status": "error", "msg": "सभी फील्ड भरें"})

        try:
            website = WebsiteRegistration.objects.get(website_id=website_id)
        except WebsiteRegistration.DoesNotExist:
            return JsonResponse({"status": "error", "msg": "Website नहीं मिला"})

        # Save or update bot response
        BotResponse.objects.update_or_create(
            website=website,
            keyword=keyword,
            defaults={"reply": reply}
        )

        return JsonResponse({"status": "success", "msg": "Bot response Succesfully saved "})

    return JsonResponse({"status": "error", "msg": "Invalid request"}, status=405)




import requests
from django.utils import timezone
from .models import WebsiteRegistration, ContactInfo, Chat
from django.conf import settings

# ================================
# Helper: Get Client IP
# ================================
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

# ================================
# Helper: Get Location from IP
# ================================
def get_location_from_ip(ip):
    # 1️⃣ Try Google API
    try:
        geo_url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={settings.GOOGLE_MAPS_API_KEY}"
        payload = {"considerIp": True}
        res = requests.post(geo_url, json=payload, timeout=5).json()
        if "location" in res:
            lat = res["location"]["lat"]
            lng = res["location"]["lng"]
            # Reverse Geocode
            rev_res = requests.get(
                f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={settings.GOOGLE_MAPS_API_KEY}",
                timeout=5
            ).json()
            address = rev_res["results"][0]["formatted_address"] if rev_res.get("results") else "Unknown"
            return {"lat": lat, "lng": lng, "address": address}
    except Exception as e:
        print("Google API failed:", e)

    # 2️⃣ Fallback ipinfo.io
    try:
        res = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5).json()
        city = res.get("city")
        region = res.get("region")
        country = res.get("country")
        address = ", ".join(filter(None, [city, region, country])) or "Unknown"
        return {"lat": None, "lng": None, "address": address}
    except Exception as e:
        print("Fallback failed:", e)
        return {"lat": None, "lng": None, "address": "Unknown"}

# ================================
# Main: Get or Create Contact + Chat
# ================================
def _get_or_create_contact(request, website_id=None):
    if not request.session.session_key:
        request.session.create()

    contact_id = request.session.get("contact_id")
    session_start = request.session.get("session_start")

    # Website instance
    website = WebsiteRegistration.objects.filter(website_id=website_id).first() if website_id else None

    # Existing contact
    contact = ContactInfo.objects.filter(id=contact_id).first() if contact_id else None

    # Create new contact if not found or old session
    if not contact or not session_start:
        contact = ContactInfo.objects.create(contact_type="temp", website=website)
        request.session["contact_id"] = contact.id
        request.session["session_start"] = str(timezone.now())
        request.session["ask_count"] = 0
        request.session["contact_saved"] = False

        # IP and Location
        ip = get_client_ip(request)
        contact.ip_address = ip
        location = get_location_from_ip(ip)
        if location:
            contact.latitude = location.get("lat")
            contact.longitude = location.get("lng")
            contact.location_name = location.get("address") or "Unknown"

        contact.save()

    # Chat create if not exist
    chat = Chat.objects.filter(contact=contact).last()
    if not chat:
        chat = Chat.objects.create(
            chat_id=f"CHAT-{contact.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            contact=contact,
            ip_address=contact.ip_address,
        )

    return contact, chat
