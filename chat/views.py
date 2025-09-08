
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.http import JsonResponse, StreamingHttpResponse
from rest_framework import generics
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth, ExtractYear

import json, difflib, re
from queue import Queue

from .models import Message, ContactInfo
from .serializers import MessageSerializer

# ================= KEYWORD BOT =================
import difflib

RESPONSES = {
    # ===== GREETINGS =====
    "hello": "Hello! Welcome to Urgent IT Solution. How can we assist you today?",
    "hi": "Hi there! Urgent IT Solution at your service—what can we do for you?",
    "hey": "Hey! You’ve reached Urgent IT Solution—how can we help?",
    "good morning": "Good morning! How can we help you today?",
    "good afternoon": "Good afternoon! How can we assist you right now?",
    "good evening": "Good evening! What IT support can we offer this evening?",

    # ===== GOODBYE =====
    "bye": "Goodbye! Have a great day.",
    "goodbye": "Hope to talk to you soon! 😊",
     "okey": "if any query so please tell me ! 😊",

    # ===== CONTACT & SUPPORT =====
    "call support": "Feel free to contact our support via phone or WhatsApp at +91 7408142576.",
    "support": "We provide 24/7 technical support. Please describe your issue and we’ll be right on it.",
    "cont": "Reach us at +91 7408142576 or urgentitsolution@gmail.com",
    "call": "Feel free to contact our support via phone or WhatsApp...",
    "email": "You can email us at urgentitsolution@gmail.com",
    "location": "Our main office is in Noida, Uttar Pradesh, India. We serve clients across the country.",
    "hours": "We are available 24/7. You can reach us anytime.",
    "emergency": "If it’s urgent, please contact our support number immediately.",

    # ===== SERVICES =====
    "services": "We specialize in Web Design, Digital Marketing, Mobile App Development, and Custom Software Solutions.",
    "website": "Yes, we build responsive websites, landing pages, and e-commerce platforms tailored for businesses of all sizes.",
    "website designing": "We provide professional, mobile-friendly website designing services at affordable prices.",
    "seo": "Yes, we provide SEO optimization services to improve your website's ranking.",
    "digital marketing": "We offer SEO, SEM, Social Media Marketing (SMM), and PPC services.",
    "branding": "We offer logo design, branding, and identity services for your company.",
    "hosting": "We provide fast and secure web hosting for all our clients.",
    "portfolio": "Check out our projects here: https://urgentitsolution.com/portfolio",
    "software": "We develop custom software and mobile/web applications trusted for quality and affordability.",
    "app development": "We provide mobile and web app development tailored to your business needs.",

    # ===== ABOUT & COURSES =====
    "about": "Urgent IT Solution is a trusted IT and digital marketing company based in Noida, delivering affordable, high-quality solutions across India.",
    "courses": "We offer placement-oriented courses in Digital Marketing, Web Development, and related areas.",
    "placement": "We provide career-oriented IT courses with placement assistance.",

    # ===== QUOTES & PAYMENTS =====
    "pricing": "Pricing depends on project complexity. Please contact us for a customized quote.",
    "quote": "To get a quote, please provide details of your project requirements.",
    "payment": "We accept payments via Bank Transfer, UPI, and PayPal.",

    # ===== ISSUES & TECH HELP =====
    "bug": "We can help fix bugs. Please provide the details of the issue.",
    "issue": "Sorry to hear that. Can you explain the problem?",
    "update": "We regularly update our software for security and new features.",
    "maintenance": "Scheduled maintenance happens on weekends. We notify users beforehand.",
    "login": "If you're facing login issues, try resetting your password.",
    "signup": "Sign up using your email or mobile number.",
    "reset password": "To reset your password, click on 'Forgot Password' at login.",

    # ===== THANKS =====
    "thank you": "You're welcome! 😊",
    "thanks": "No problem at all—we're here to help.",

    # ===== PROMPTS / EXTRAS =====
    "consultation": "Would you like to schedule a free consultation to discuss your project?",
    "promotion": "Interested in boosting your business online? Ask us about our digital marketing plans!",
    "default": "Sorry, I didn't understand that. Can you please rephrase your question?"
}


def _best_reply(user_message: str) -> str:
    if not user_message:
        return "Hello! How can I help you?"

    user_message = user_message.lower().strip()

    # Fuzzy match (best effort)
    match = difflib.get_close_matches(user_message, RESPONSES.keys(), n=1, cutoff=0.6)
    if match:
        return RESPONSES[match[0]]

    # Substring check (agar keyword sentence me ho)
    for key, reply in RESPONSES.items():
        if key in user_message:
            return reply

    return RESPONSES["default"]


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

# ================== GEO LOCATION (IP → City/Country) ==================
# Uses: django-ipware + geoip2. Falls back gracefully if DB not available.
from django.conf import settings
try:
    from ipware import get_client_ip
except Exception:
    # Minimal fallback if ipware not installed (still works, less accurate)
    def get_client_ip(request):
        return request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR")), True

try:
    import geoip2.database
    _GEOIP_READER = None
except Exception:
    geoip2 = None
    _GEOIP_READER = None

def _get_geo_from_ip(ip: str):
    """
    Returns dict: {"ip", "country", "city", "lat", "lon"}
    If lookup fails, returns keys with None (ip included).
    """
    if not ip or ip == "unknown":
        return {"ip": ip, "country": None, "city": None, "lat": None, "lon": None}

    # If geoip2 not available or DB path missing, fail soft
    if geoip2 is None:
        return {"ip": ip, "country": None, "city": None, "lat": None, "lon": None}

    global _GEOIP_READER
    try:
        if _GEOIP_READER is None:
            db_path = getattr(settings, "GEOIP_DB_PATH", None)
            if not db_path:
                # try a common fallback path; still safe if not present
                db_path = "/usr/local/share/GeoIP/GeoLite2-City.mmdb"
            _GEOIP_READER = geoip2.database.Reader(str(db_path))

        resp = _GEOIP_READER.city(ip)
        return {
            "ip": ip,
            "country": resp.country.name,
            "city": resp.city.name,
            "lat": resp.location.latitude,
            "lon": resp.location.longitude,
        }
    except Exception:
        return {"ip": ip, "country": None, "city": None, "lat": None, "lon": None}

# ================= VIEWS =================
def chat_view(request):
    return render(request, 'chat.html')

def admin_panel_view(request):
    contacts = ContactInfo.objects.prefetch_related("messages").all().order_by("-created_at")
    return render(request, 'chat/admin_panel.html', {"contacts": contacts})

# ================= SSE STREAM =================
subscribers_admin = set()
subscribers_user = {}

def _broadcast_admin(payload: dict):
    dead = []
    for q in list(subscribers_admin):
        try:
            q.put(payload, timeout=0.1)
        except Exception:
            dead.append(q)
    for q in dead:
        subscribers_admin.discard(q)

def _broadcast_user(contact_id: int, payload: dict):
    try:
        contact_key = int(contact_id)
    except Exception:
        return
    if contact_key in subscribers_user:
        dead = []
        for q in list(subscribers_user[contact_key]):
            try:
                q.put(payload, timeout=0.1)
            except Exception:
                dead.append(q)
        for q in dead:
            subscribers_user[contact_key].discard(q)

def lead_stream(request):
    def event_stream():
        q = Queue()
        subscribers_admin.add(q)
        try:
            yield "event: ping\ndata: {}\n\n"
            while True:
                data = q.get()
                yield f"data: {json.dumps(data)}\n\n"
        except GeneratorExit:
            pass
        finally:
            subscribers_admin.discard(q)

    resp = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    resp["Cache-Control"] = "no-cache"
    return resp

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

# ================= CONTACT / CHAT LOGIC =================
SERVER_START_TIME = timezone.now()

def _get_or_create_contact(request, user_ip: str) -> ContactInfo:
    if not request.session.session_key:
        request.session.create()

    contact_id = request.session.get("contact_id")
    session_start = request.session.get("session_start")

    contact = None
    if contact_id:
        contact = ContactInfo.objects.filter(id=contact_id).first()

    if (not contact) or (not session_start) or (session_start < str(SERVER_START_TIME)):
        contact = ContactInfo.objects.create(
            ip_address=user_ip,
            session_key=request.session.session_key,
            contact_type="temp",
        )
        request.session["contact_id"] = contact.id
        request.session["session_start"] = str(SERVER_START_TIME)
        request.session["ask_count"] = 0
        request.session["contact_saved"] = False

    return contact

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
    sender = (data.get('sender') or 'user').lower()

    # --- IP + GEO (added) ---
    client_ip, _ = get_client_ip(request)
    user_ip = client_ip or request.META.get("REMOTE_ADDR", "unknown")
    geo = _get_geo_from_ip(user_ip)
    request.session["user_geo"] = geo  # handy for templates or later use

    contact = _get_or_create_contact(request, user_ip)

    # save user message
    if user_message:
        msg = Message.objects.create(sender=sender, text=user_message, contact=contact)
        payload_user = {
            "id": msg.id,
            "contact_id": contact.id,
            "token": f"TKN-{contact.id}",
            "sender": sender,
            "text": user_message,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
            # --- GEO included in SSE to admin (added) ---
            "geo": geo,
        }
        _broadcast_admin(payload_user)

    # check contact info
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
            reply = "✅ Thanks! Your contact info has been saved — we’ll contact you shortly, please share your problem below."
        else:
            ask_count = request.session.get("ask_count", 0)
            if ask_count < 3:
                request.session["ask_count"] = ask_count + 1
                reply = "🙏 Could you please share your phone or email so we can assist you better?"
            else:
                request.session["contact_saved"] = True
                reply = "Alright 👍 let's continue. How can we help you?"
    else:
        reply = _best_reply(user_message.lower()) if user_message else "Hello! How can I help you?"

    # send bot reply
    bot_msg = Message.objects.create(sender="bot", text=reply, contact=contact)
    payload_bot = {
        "id": bot_msg.id,
        "contact_id": contact.id,
        "token": f"TKN-{contact.id}",
        "sender": "bot",
        "text": reply,
        "timestamp": bot_msg.timestamp.strftime("%Y-%m-%d %H:%M"),
        # --- GEO included for both admin + user streams (added) ---
        "geo": geo,
    }
    _broadcast_admin(payload_bot)
    _broadcast_user(contact.id, payload_bot)

    return JsonResponse({
        "reply": reply,
        "contact_id": contact.id,
        "token": f"TKN-{contact.id}",
        # --- GEO included in API response (added) ---
        "geo": geo,
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

    if not (contact_id or token) or not message:
        return JsonResponse({"error": "Missing contact_id/token or message"}, status=400)

    contact = None
    if contact_id:
        contact = ContactInfo.objects.filter(id=int(contact_id)).first()
    elif token:
        if isinstance(token, str) and token.upper().startswith("TKN-"):
            try:
                possible_id = int(token.split("-", 1)[1])
                contact = ContactInfo.objects.filter(id=possible_id).first()
            except Exception:
                pass
        if not contact:
            contact = ContactInfo.objects.filter(token_number=token).first()

    if not contact:
        return JsonResponse({"error": "Contact not found"}, status=404)

    msg = Message.objects.create(sender="admin", text=message, contact=contact)
    # try to attach last known geo from session if available (non-blocking)
    geo = None
    try:
        geo = getattr(request, "session", {}).get("user_geo")
    except Exception:
        geo = None

    payload = {
        "id": msg.id,
        "contact_id": contact.id,
        "token": f"TKN-{contact.id}",
        "sender": "admin",
        "text": message,
        "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
        # --- GEO included in SSE to user + admin (added) ---
        "geo": geo,
    }
    _broadcast_user(contact.id, payload)
    _broadcast_admin(payload)

    return JsonResponse({"status": "success", "message": "Sent", "token": f"TKN-{contact.id}"})

admin_send_message = admin_reply

# ================= MESSAGES API =================
class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all().order_by('-timestamp')
    serializer_class = MessageSerializer

# ================= CONTACT API =================
@csrf_exempt
def save_contact(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request"}, status=405)

    try:
        if request.content_type and "application/json" in request.content_type:
            data = json.loads(request.body or "{}")
            contact_value = data.get("contact_value")
            contact_type = data.get("contact_type", "temp")
        else:
            contact_value = request.POST.get("contact_value")
            contact_type = request.POST.get("contact_type", "temp")
    except json.JSONDecodeError:
        contact_value, contact_type = None, "temp"

    # --- IP + GEO (added) ---
    client_ip, _ = get_client_ip(request)
    user_ip = client_ip or request.META.get("REMOTE_ADDR", "unknown")
    geo = _get_geo_from_ip(user_ip)
    request.session["user_geo"] = geo

    contact = _get_or_create_contact(request, user_ip)

    if contact_value:
        if contact_type == "phone":
            contact.mobile = contact_value
        elif contact_type == "email":
            contact.email = contact_value
        contact.contact_value = contact_value
        contact.contact_type = contact_type
        contact.save()
        request.session["contact_saved"] = True

    return JsonResponse({
        "status": "success",
        "id": contact.id,
        "token": f"TKN-{contact.id}",
        # --- GEO included in API response (added) ---
        "geo": geo,
    })

def get_contacts(request):
    contacts_qs = ContactInfo.objects.all().order_by("-created_at").values(
        "id", "token_number", "mobile", "email", "contact_value", "created_at", "is_seen"
    )
    contacts = list(contacts_qs)
    for c in contacts:
        c["token"] = c.get("token_number") or f"TKN-{c['id']}"
    return JsonResponse({"contacts": contacts})

def get_messages(request, contact_id):
    try:
        contact = ContactInfo.objects.get(id=contact_id)
        messages = Message.objects.filter(contact=contact).order_by("timestamp")
        data = [
            {
                "id": msg.id,
                "sender": msg.sender.lower(),
                "text": msg.text,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
            }
            for msg in messages
        ]
        # also return last known geo from session if present
        geo = None
        try:
            geo = request.session.get("user_geo")
        except Exception:
            geo = None

        return JsonResponse({
            "messages": data,
            "token": f"TKN-{contact.id}",
            "token_number": contact.token_number,
            "geo": geo,  # (added)
        })
    except ContactInfo.DoesNotExist:
        return JsonResponse({"error": "Contact not found"}, status=404)

# ================= STATS API =================
def stats(request):
    total_contacts = ContactInfo.objects.count()
    total_messages = Message.objects.count()
    total_visitors = ContactInfo.objects.values("contact_value").distinct().count()

    total_chats = Message.objects.values("contact_id").distinct().count()

    page_views_agg = ContactInfo.objects.aggregate(total=Sum('page_views'))
    total_pageviews = page_views_agg.get('total') or 0

    sender_stats = list(Message.objects.values("sender").annotate(total=Count("id")))

    now = timezone.now()

    visitors_by_month_qs = ContactInfo.objects.annotate(
        y=ExtractYear('created_at'), m=ExtractMonth('created_at')
    ).values('y', 'm').annotate(total=Count('id')).order_by('y', 'm')

    messages_by_month_qs = Message.objects.annotate(
        y=ExtractYear('timestamp'), m=ExtractMonth('timestamp')
    ).values('y', 'm').annotate(total=Count('id')).order_by('y', 'm')

    pageviews_by_month_qs = ContactInfo.objects.annotate(
        y=ExtractYear('created_at'), m=ExtractMonth('created_at')
    ).values('y', 'm').annotate(total=Sum('page_views')).order_by('y', 'm')

    vis_lookup = {f"{r['y']}-{int(r['m']):02d}": r['total'] for r in visitors_by_month_qs}
    msg_lookup = {f"{r['y']}-{int(r['m']):02d}": r['total'] for r in messages_by_month_qs}
    pv_lookup = {f"{r['y']}-{int(r['m']):02d}": r['total'] or 0 for r in pageviews_by_month_qs}

    months = []
    visitors_data = []
    chats_data = []
    page_views_dist = []

    for i in range(5, -1, -1):
        target = (now - timezone.timedelta(days=30 * i))
        y = target.year
        m = target.month
        label = f"{y}-{m:02d}"
        months.append(label)
        visitors_data.append(vis_lookup.get(label, 0))
        chats_data.append(msg_lookup.get(label, 0))
        page_views_dist.append(pv_lookup.get(label, 0))

    feedback_percent = 0
    if total_messages > 0:
        feedback_percent = min(100, (total_contacts * 10) // total_messages)

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
