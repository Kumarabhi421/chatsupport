
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
  
    # Greetings
    "hello": "Hello! Welcome to Urgent IT Solution. How can we assist you today?",
    "hi": "Hi there! Urgent IT Solution at your service—what can we do for you?",
    "hey": "Hey! Great to see you at Urgent IT Solution. How can we help?",
    "good morning": "Good morning! How can Urgent IT Solution assist you today?",
    "good afternoon": "Good afternoon! How may we help you with your digital solutions?",
    "good evening": "Good evening! Need help with your website or online presence?",
    
    # Company Info
    "company deatail": "We are Urgent IT Solution, providing Website Design, SEO, Digital Marketing, and E-commerce Solutions.",
    "about": "Urgent IT Solution helps businesses grow online with websites, SEO, marketing, and more.",
    "what do you do": "We provide Website Development, SEO, Social Media Marketing, and E-commerce Solutions for your business.",
    "services": "We offer Website Design, SEO, Social Media Marketing, E-commerce Solutions, and more. How can we help you today?",
    
    # Contact Info
    "contact": "You can reach us at contact@urgentitsolution.com or visit our website at https://urgentitsolution.com/",
    "email": "Our official email is contact@urgentitsolution.com. Feel free to write to us.",
    "phone": "You can call us at +91-XXXXXXXXXX for any queries.",
    "address": "We are located in Noida, Uttar Pradesh, India.",
    "location": "Our office is in Noida, Uttar Pradesh. Visit us anytime during business hours.",
    
    # Website & Technical
    "website": "You can explore our services at https://urgentitsolution.com/",
    "website design": "We create custom, responsive, and SEO-friendly websites for businesses.",
    "seo": "Our SEO strategies improve your website ranking on Google.",
    "social media marketing": "We help your brand grow on platforms like Instagram, Facebook, and LinkedIn.",
    "ecommerce": "We provide complete E-commerce solutions, including store setup and management.",
    "web development": "We develop fast, secure, and mobile-friendly websites tailored to your business.",
    "app development": "We build user-friendly mobile apps for iOS and Android platforms.",
    
    # Pricing & Quotes
    "pricing": "Our pricing depends on the service you choose. Please contact us for a quote.",
    "quote": "We can provide a customized quote based on your project requirements.",
    "cost": "The cost varies depending on your project. Contact us for detailed pricing.",
    
    # Support & Help
    "support": "Our support team is here to help. What issue are you facing?",
    "help": "How can we assist you today? We provide help with websites, SEO, and more.",
    "technical issue": "Please describe the technical issue, and our team will resolve it ASAP.",
    "troubleshoot": "We can help troubleshoot your website or digital solution problem.",
    
    # Business & Collaboration
    "partnership": "We welcome partnerships. Please contact us with your proposal.",
    "collaboration": "We are open to collaborations in IT solutions and marketing.",
    "business": "We help businesses establish and grow their online presence.",
    "startup": "We provide affordable digital solutions for startups to grow online.",
    
    # Social Media
    "instagram": "Follow us on Instagram: https://www.instagram.com/urgentitsolution1/",
    "linkedin": "Connect with us on LinkedIn: https://in.linkedin.com/company/urgentitsolution",
    "facebook": "Follow our Facebook page for updates on services and promotions.",
    "twitter": "Follow us on Twitter for latest news and tips.",
    
    # Working Hours
    "hours": "We are available Monday to Saturday, 9 AM to 6 PM.",
    "open": "Our office is open from 9 AM to 6 PM, Monday to Saturday.",
    "closing": "We close at 6 PM, but you can reach us anytime via email.",
    
    # Miscellaneous
    "thank you": "You're welcome! Happy to assist you.",
    "thanks": "Thanks for reaching out! How else can we help?",
    "bye": "Goodbye! Have a great day.",
    "see you": "See you soon! Contact us anytime.",
    "ok": "Alright! Let us know if you need any further assistance.",
    "sure": "Sure! How can we assist you further?",
    "yes": "Great! Please tell us more about your requirement.",
    "no": "No problem! Let us know if you change your mind.",
    
    # FAQ style
    "how to contact": "You can contact us via email, phone, or our website contact form.",
    "how to get a quote": "Provide your project details via email or form, and we'll send a customized quote.",
    "how to start": "Reach out to us with your requirements, and our team will guide you step by step.",
    "do you provide maintenance": "Yes, we offer website maintenance and SEO services after launch.",
    "can you build ecommerce": "Absolutely! We provide end-to-end E-commerce solutions.",
    "do you offer hosting": "Yes, we provide hosting and domain registration along with website services.",
    
    # Engagement
    "latest projects": "You can check our latest projects on our website portfolio section.",
    "testimonials": "Visit our testimonials page to see what our clients say about us.",
    "portfolio": "We have a portfolio of websites, SEO projects, and marketing campaigns. Check online.",
    
    # User Guidance
    "how to order": "Contact us with your project details, and we'll guide you on placing an order.",
    "how long takes": "Project duration depends on complexity. Usually 1-4 weeks for websites.",
    "payment methods": "We accept online bank transfer, UPI, and other digital payments.",
    
    # Greetings variations
    "hola": "Hola! Welcome to Urgent IT Solution.",
    "greetings": "Greetings! How may we help your business grow online?",
    
    # Extra polite responses
    "please": "Sure! Please provide more details so we can assist you better.",
    "kindly": "Kindly share your requirement, and our team will get back to you.",
    
    # More service-related queries
    "digital marketing": "We offer full digital marketing services including SEO, SMO, and PPC campaigns.",
    "ppc": "Our PPC campaigns target the right audience to generate leads and sales.",
    "content marketing": "We create high-quality content to engage your audience and improve SEO.",
    "branding": "We help your business build a strong and recognizable brand online.",
    
    # Security & Reliability
    "secure website": "We ensure websites are secure, fast, and mobile-friendly.",
    "reliable service": "Our services are reliable and tailored to achieve your business goals.",
    
    # Queries about updates
    "update": "We keep your website updated and optimized for best performance.",
    "upgrade": "We provide upgrades and new feature integrations as per your need.",
    
    # Problem-solving
    "issue": "Please describe your issue, and we will solve it quickly.",
    "problem": "Our team can resolve your problem efficiently. Share the details.",
    
    # Closing interactions
    "talk later": "Sure! Contact us anytime. We're always here to assist you.",
    "good night": "Good night! We hope you have a restful sleep.",
    
    # Fun/engaging responses
    "how are you": "We are doing great! Excited to help your business grow online.",
    "what's up": "Our team is working hard to provide the best digital solutions!",
    
    # More engagement
    "services list": "We offer Website Design, SEO, Social Media Marketing, App Development, and E-commerce Solutions.",
    "need help": "Absolutely! Please tell us what kind of help you need.",
    
    # Polite follow-ups
    "can you help": "Yes! Our team is ready to help. Please share your requirements.",
    "need consultation": "We offer free consultation. Contact us with your project details.",
    
    # Promotional
    "offers": "Check our website for current offers and promotions on digital services.",
    "discount": "We provide occasional discounts. Reach out to know more.",
    
    # Misc short phrases
    "ok thanks": "You're welcome! Feel free to ask more questions.",
    "welcome": "Welcome! How may we assist you today?",
    "good": "Great! Tell us how we can help further.",
    
    # Project Queries
    "custom website": "We can build a custom website tailored to your business needs.",
    "responsive website": "All our websites are fully responsive and mobile-friendly.",
    "fast website": "We optimize websites for speed and performance.",
    
    # Marketing
    "email marketing": "We create effective email campaigns to engage your audience.",
    "social campaigns": "Our social media campaigns increase brand awareness and leads.",
    
    # Closing general
    "bye bye": "Goodbye! Contact us anytime for your digital needs.",
    "see you soon": "See you soon! We're always here to assist you.",
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
except ImportError:
    # Minimal fallback if ipware not installed
    def get_client_ip(request):
        return request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR")), True

try:
    import geoip2.database
    _GEOIP_READER = None
except ImportError:
    geoip2 = None
    _GEOIP_READER = None


def _get_geo_from_ip(ip: str):
    """
    Returns dict: {"ip", "country", "city", "lat", "lon"}
    Always returns a dict, never crashes.
    """
    try:
        if not ip or ip == "unknown":
            return {"ip": ip, "country": "Unknown", "city": "Unknown", "lat": None, "lon": None}

        # Ignore local/private IPs (LAN / localhost)
        if ip.startswith(("127.", "192.", "10.")):
            return {"ip": ip, "country": "Local Network", "city": "Localhost", "lat": None, "lon": None}

        if geoip2 is None:
            # geoip2 not installed
            return {"ip": ip, "country": "Unknown", "city": "Unknown", "lat": None, "lon": None}

        global _GEOIP_READER
        if _GEOIP_READER is None:
            db_path = getattr(settings, "GEOIP_DB_PATH", None) or "/usr/local/share/GeoIP/GeoLite2-City.mmdb"
            _GEOIP_READER = geoip2.database.Reader(str(db_path))

        resp = _GEOIP_READER.city(ip)
        return {
            "ip": ip,
            "country": resp.country.name or "Unknown",
            "city": resp.city.name or "Unknown",
            "lat": resp.location.latitude,
            "lon": resp.location.longitude,
        }
    except Exception:
        # If anything fails, fallback to safe dummy data
        return {"ip": ip, "country": "Unknown", "city": "Unknown", "lat": None, "lon": None}


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



