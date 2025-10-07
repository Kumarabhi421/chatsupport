
# from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
# from django.core.validators import validate_email
# from django.core.exceptions import ValidationError
# from django.utils import timezone
# from django.http import JsonResponse, StreamingHttpResponse
# from rest_framework import generics
# from django.db.models import Count, Sum
# from django.db.models.functions import ExtractMonth, ExtractYear
# import json, difflib, re
# from queue import Queue
# from .models import Message, ContactInfo
# from .serializers import MessageSerializer
# # ================= KEYWORD BOT =================
# import difflib

# RESPONSES = {
  
#     # Greetings
#     "hello": "Hello! Welcome to Urgent IT Solution. How can we assist you today?",
#     "hi": "Hi there! Urgent IT Solution at your service—what can we do for you?",
#     "hey": "Hey! Great to see you at Urgent IT Solution. How can we help?",
#     "good morning": "Good morning! How can Urgent IT Solution assist you today?",
#     "good afternoon": "Good afternoon! How may we help you with your digital solutions?",
#     "good evening": "Good evening! Need help with your website or online presence?",
    
#     # Company Info
#     "company deatail": "We are Urgent IT Solution, providing Website Design, SEO, Digital Marketing, and E-commerce Solutions.",
#     "about": "Urgent IT Solution helps businesses grow online with websites, SEO, marketing, and more.",
#     "what do you do": "We provide Website Development, SEO, Social Media Marketing, and E-commerce Solutions for your business.",
#     "services": "We offer Website Design, SEO, Social Media Marketing, E-commerce Solutions, and more. How can we help you today?",
    
#     # Contact Info
#     "contact": "You can reach us at contact@urgentitsolution.com or visit our website at https://urgentitsolution.com/",
#     "email": "Our official email is contact@urgentitsolution.com. Feel free to write to us.",
#     "phone": "You can call us at +91-7303468125 for any queries.",
#     "address": "We are located in Noida, Uttar Pradesh, India.",
#     "location": "Our office is in Noida, Uttar Pradesh. Visit us anytime during business hours.",
#    "support": "You can call us at +91-7303468125 for any queries.",
    
#     # Website & Technical
#     "website": "You can explore our services at https://urgentitsolution.com/",
#     "website design": "We create custom, responsive, and SEO-friendly websites for businesses.",
#     "seo": "Our SEO strategies improve your website ranking on Google.",
#     "social media marketing": "We help your brand grow on platforms like Instagram, Facebook, and LinkedIn.",
#     "ecommerce": "We provide complete E-commerce solutions, including store setup and management.",
#     "web development": "We develop fast, secure, and mobile-friendly websites tailored to your business.",
#     "app development": "We build user-friendly mobile apps for iOS and Android platforms.",
    
#     # Pricing & Quotes
#     "pricing": "Our pricing depends on the service you choose. Please contact us for a quote.",
#     "quote": "We can provide a customized quote based on your project requirements.",
#     "cost": "The cost varies depending on your project. Contact us for detailed pricing.",
    
#     # Support & Help
#     "support": "Our support team is here to help. What issue are you facing?",
#     "help": "How can we assist you today? We provide help with websites, SEO, and more.",
#     "technical issue": "Please describe the technical issue, and our team will resolve it ASAP.",
#     "troubleshoot": "We can help troubleshoot your website or digital solution problem.",
    
#     # Business & Collaboration
#     "partnership": "We welcome partnerships. Please contact us with your proposal.",
#     "collaboration": "We are open to collaborations in IT solutions and marketing.",
#     "business": "We help businesses establish and grow their online presence.",
#     "startup": "We provide affordable digital solutions for startups to grow online.",
    
#     # Social Media
#     "instagram": "Follow us on Instagram: https://www.instagram.com/urgentitsolution1/",
#     "linkedin": "Connect with us on LinkedIn: https://in.linkedin.com/company/urgentitsolution",
#     "facebook": "Follow our Facebook page for updates on services and promotions.",
#     "twitter": "Follow us on Twitter for latest news and tips.",
    
#     # Working Hours
#     "hours": "We are available Monday to Saturday, 9 AM to 6 PM.",
#     "open": "Our office is open from 9 AM to 6 PM, Monday to Saturday.",
#     "closing": "We close at 6 PM, but you can reach us anytime via email.",
    
#     # Miscellaneous
#     "thank you": "You're welcome! Happy to assist you.",
#     "thanks": "Thanks for reaching out! How else can we help?",
#     "bye": "Goodbye! Have a great day.",
#     "see you": "See you soon! Contact us anytime.",
#     "ok": "Alright! Let us know if you need any further assistance.",
#     "sure": "Sure! How can we assist you further?",
#     "yes": "Great! Please tell us more about your requirement.",
#     "no": "No problem! Let us know if you change your mind.",
    
#     # FAQ style
#     "how to contact": "You can contact us via email, phone, or our website contact form.",
#     "how to get a quote": "Provide your project details via email or form, and we'll send a customized quote.",
#     "how to start": "Reach out to us with your requirements, and our team will guide you step by step.",
#     "do you provide maintenance": "Yes, we offer website maintenance and SEO services after launch.",
#     "can you build ecommerce": "Absolutely! We provide end-to-end E-commerce solutions.",
#     "do you offer hosting": "Yes, we provide hosting and domain registration along with website services.",
    
#     # Engagement
#     "latest projects": "You can check our latest projects on our website portfolio section.",
#     "testimonials": "Visit our testimonials page to see what our clients say about us.",
#     "portfolio": "We have a portfolio of websites, SEO projects, and marketing campaigns. Check online.",
    
#     # User Guidance
#     "how to order": "Contact us with your project details, and we'll guide you on placing an order.",
#     "how long takes": "Project duration depends on complexity. Usually 1-4 weeks for websites.",
#     "payment methods": "We accept online bank transfer, UPI, and other digital payments.",
    
#     # Greetings variations
#     "hola": "Hola! Welcome to Urgent IT Solution.",
#     "greetings": "Greetings! How may we help your business grow online?",
    
#     # Extra polite responses
#     "please": "Sure! Please provide more details so we can assist you better.",
#     "kindly": "Kindly share your requirement, and our team will get back to you.",
    
#     # More service-related queries
#     "digital marketing": "We offer full digital marketing services including SEO, SMO, and PPC campaigns.",
#     "ppc": "Our PPC campaigns target the right audience to generate leads and sales.",
#     "content marketing": "We create high-quality content to engage your audience and improve SEO.",
#     "branding": "We help your business build a strong and recognizable brand online.",
    
#     # Security & Reliability
#     "secure website": "We ensure websites are secure, fast, and mobile-friendly.",
#     "reliable service": "Our services are reliable and tailored to achieve your business goals.",
    
#     # Queries about updates
#     "update": "We keep your website updated and optimized for best performance.",
#     "upgrade": "We provide upgrades and new feature integrations as per your need.",
    
#     # Problem-solving
#     "issue": "Please describe your issue, and we will solve it quickly.",
#     "problem": "Our team can resolve your problem efficiently. Share the details.",
    
#     # Closing interactions
#     "talk later": "Sure! Contact us anytime. We're always here to assist you.",
#     "good night": "Good night! We hope you have a restful sleep.",
    
#     # Fun/engaging responses
#     "how are you": "We are doing great! Excited to help your business grow online.",
#     "what's up": "Our team is working hard to provide the best digital solutions!",
    
#     # More engagement
#     "services list": "We offer Website Design, SEO, Social Media Marketing, App Development, and E-commerce Solutions.",
#     "need help": "Absolutely! Please tell us what kind of help you need.",
    
#     # Polite follow-ups
#     "can you help": "Yes! Our team is ready to help. Please share your requirements.",
#     "need consultation": "We offer free consultation. Contact us with your project details.",
    
#     # Promotional
#     "offers": "Check our website for current offers and promotions on digital services.",
#     "discount": "We provide occasional discounts. Reach out to know more.",
    
#     # Misc short phrases
#     "ok thanks": "You're welcome! Feel free to ask more questions.",
#     "welcome": "Welcome! How may we assist you today?",
#     "good": "Great! Tell us how we can help further.",
    
#     # Project Queries
#     "custom website": "We can build a custom website tailored to your business needs.",
#     "responsive website": "All our websites are fully responsive and mobile-friendly.",
#     "fast website": "We optimize websites for speed and performance.",
    
#     # Marketing
#     "email marketing": "We create effective email campaigns to engage your audience.",
#     "social campaigns": "Our social media campaigns increase brand awareness and leads.",
    
#     # Closing general
#     "bye bye": "Goodbye! Contact us anytime for your digital needs.",
#     "see you soon": "See you soon! We're always here to assist you.",
# }


# def _best_reply(user_message: str) -> str:
#     if not user_message:
#         return "Hello! How can I help you?"

#     user_message = user_message.lower().strip()

#     # Fuzzy match (best effort)
#     match = difflib.get_close_matches(user_message, RESPONSES.keys(), n=1, cutoff=0.6)
#     if match:   
#         return RESPONSES[match[0]]

#     # Substring check (agar keyword sentence me ho)
#     for key, reply in RESPONSES.items():
#         if key in user_message:
#             return reply

#     return "Hello! How can I help you?"

# # ================= CONTACT INFO EXTRACTION =================
# def extract_contact_info(text: str):
#     mobile_pattern = r"\b\d{10}\b"
#     email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

#     mobile = re.search(mobile_pattern, text)
#     mobile = mobile.group(0) if mobile else None

#     email_match = re.search(email_pattern, text)
#     email = email_match.group(0) if email_match else None

#     if email:
#         try:
#             validate_email(email)
#         except ValidationError:
#             email = None

#     return mobile, email

# # ================== GEO LOCATION (IP → City/Country) ==================
# # Uses: django-ipware + geoip2. Falls back gracefully if DB not available.
# from django.conf import settings
# try:
#     from ipware import get_client_ip
# except ImportError:
#     # Minimal fallback if ipware not installed
#     def get_client_ip(request):
#         return request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR")), True

# try:
#     import geoip2.database
#     _GEOIP_READER = None
# except ImportError:
#     geoip2 = None
#     _GEOIP_READER = None


# def _get_geo_from_ip(ip: str):
#     """
#     Returns dict: {"ip", "country", "city", "lat", "lon"}
#     Always returns a dict, never crashes.
#     """
#     try:
#         if not ip or ip == "unknown":
#             return {"ip": ip, "country": "Unknown", "city": "Unknown", "lat": None, "lon": None}

#         # Ignore local/private IPs (LAN / localhost)
#         if ip.startswith(("127.", "192.", "10.")):
#             return {"ip": ip, "country": "Local Network", "city": "Localhost", "lat": None, "lon": None}

#         if geoip2 is None:
#             # geoip2 not installed
#             return {"ip": ip, "country": "Unknown", "city": "Unknown", "lat": None, "lon": None}

#         global _GEOIP_READER
#         if _GEOIP_READER is None:
#             db_path = getattr(settings, "GEOIP_DB_PATH", None) or "/usr/local/share/GeoIP/GeoLite2-City.mmdb"
#             _GEOIP_READER = geoip2.database.Reader(str(db_path))

#         resp = _GEOIP_READER.city(ip)
#         return {
#             "ip": ip,
#             "country": resp.country.name or "Unknown",
#             "city": resp.city.name or "Unknown",
#             "lat": resp.location.latitude,
#             "lon": resp.location.longitude,
#         }
#     except Exception:
#         # If anything fails, fallback to safe dummy data
#         return {"ip": ip, "country": "Unknown", "city": "Unknown", "lat": None, "lon": None}


# # ================= VIEWS =================
# def chat_view(request):
#     return render(request, 'chat.html')

# def admin_panel_view(request):
#     contacts = ContactInfo.objects.prefetch_related("messages").all().order_by("-created_at")
#     return render(request, 'chat/admin_panel.html', {"contacts": contacts})

# # ================= SSE STREAM =================
# subscribers_admin = set()
# subscribers_user = {}

# def _broadcast_admin(payload: dict):
#     dead = []
#     for q in list(subscribers_admin):
#         try:
#             q.put(payload, timeout=0.1)
#         except Exception:
#             dead.append(q)
#     for q in dead:
#         subscribers_admin.discard(q)

# def _broadcast_user(contact_id: int, payload: dict):
#     try:
#         contact_key = int(contact_id)
#     except Exception:
#         return
#     if contact_key in subscribers_user:
#         dead = []
#         for q in list(subscribers_user[contact_key]):
#             try:
#                 q.put(payload, timeout=0.1)
#             except Exception:
#                 dead.append(q)
#         for q in dead:
#             subscribers_user[contact_key].discard(q)

# def lead_stream(request):
#     def event_stream():
#         q = Queue()
#         subscribers_admin.add(q)
#         try:
#             yield "event: ping\ndata: {}\n\n"
#             while True:
#                 data = q.get()
#                 yield f"data: {json.dumps(data)}\n\n"
#         except GeneratorExit:
#             pass
#         finally:
#             subscribers_admin.discard(q)

#     resp = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
#     resp["Cache-Control"] = "no-cache"
#     return resp

# def user_stream(request, contact_id):
#     def event_stream():
#         q = Queue()
#         subscribers_user.setdefault(int(contact_id), set()).add(q)
#         try:
#             yield "event: ping\ndata: {}\n\n"
#             while True:
#                 data = q.get()
#                 yield f"data: {json.dumps(data)}\n\n"
#         except GeneratorExit:
#             pass
#         finally:
#             subscribers_user[int(contact_id)].discard(q)

#     resp = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
#     resp["Cache-Control"] = "no-cache"
#     return resp

# # ================= CONTACT / CHAT LOGIC =================
# SERVER_START_TIME = timezone.now()

# def _get_or_create_contact(request, user_ip: str) -> ContactInfo:
#     if not request.session.session_key:
#         request.session.create()

#     contact_id = request.session.get("contact_id")
#     session_start = request.session.get("session_start")

#     contact = None
#     if contact_id:
#         contact = ContactInfo.objects.filter(id=contact_id).first()

#     if (not contact) or (not session_start) or (session_start < str(SERVER_START_TIME)):
#         contact = ContactInfo.objects.create(
#             ip_address=user_ip,
#             session_key=request.session.session_key,
#             contact_type="temp",
#         )
#         request.session["contact_id"] = contact.id
#         request.session["session_start"] = str(SERVER_START_TIME)
#         request.session["ask_count"] = 0
#         request.session["contact_saved"] = False

#     return contact

# # ================= CHAT API =================
# @csrf_exempt
# def get_response(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid method"}, status=405)

#     try:
#         data = json.loads(request.body or "{}")
#     except json.JSONDecodeError:
#         return JsonResponse({'error': 'Invalid JSON'}, status=400)

#     user_message = (data.get('message') or "").strip()
#     sender = (data.get('sender') or 'user').lower()

#     # --- IP + GEO (added) ---
#     client_ip, _ = get_client_ip(request)
#     user_ip = client_ip or request.META.get("REMOTE_ADDR", "unknown")
#     geo = _get_geo_from_ip(user_ip)
#     request.session["user_geo"] = geo  # handy for templates or later use

#     contact = _get_or_create_contact(request, user_ip)

#     # save user message
#     if user_message:
#         msg = Message.objects.create(sender=sender, text=user_message, contact=contact)
#         payload_user = {
#             "id": msg.id,
#             "contact_id": contact.id,
#             "token": f"TKN-{contact.id}",
#             "sender": sender,
#             "text": user_message,
#             "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
#             # --- GEO included in SSE to admin (added) ---
#             "geo": geo,
#         }
#         _broadcast_admin(payload_user)

#     # check contact info
#     if not request.session.get("contact_saved", False):
#         mobile, email = extract_contact_info(user_message)

#         if mobile or email:
#             if mobile:
#                 contact.mobile = mobile
#                 contact.contact_type = "phone"
#                 contact.contact_value = mobile
#             elif email:
#                 contact.email = email
#                 contact.contact_type = "email"
#                 contact.contact_value = email
#             contact.save()
#             request.session["contact_saved"] = True
#             reply = "✅ Thanks! Your contact info has been saved — we’ll contact you shortly, please share your problem below."
#         else:
#             ask_count = request.session.get("ask_count", 0)
#             if ask_count < 3:
#                 request.session["ask_count"] = ask_count + 1
#                 reply = "🙏 Could you please share your phone or email so we can assist you better?"
#             else:
#                 request.session["contact_saved"] = True
#                 reply = "Alright 👍 let's continue. How can we help you?"
#     else:
#         reply = _best_reply(user_message.lower()) if user_message else "Hello! How can I help you?"

#     # send bot reply
#     bot_msg = Message.objects.create(sender="bot", text=reply, contact=contact)
#     payload_bot = {
#         "id": bot_msg.id,
#         "contact_id": contact.id,
#         "token": f"TKN-{contact.id}",
#         "sender": "bot",
#         "text": reply,
#         "timestamp": bot_msg.timestamp.strftime("%Y-%m-%d %H:%M"),
#         # --- GEO included for both admin + user streams (added) ---
#         "geo": geo,
#     }
#     _broadcast_admin(payload_bot)
#     _broadcast_user(contact.id, payload_bot)

#     return JsonResponse({
#         "reply": reply,
#         "contact_id": contact.id,
#         "token": f"TKN-{contact.id}",
#         # --- GEO included in API response (added) ---
#         "geo": geo,
#     })

# # ================= ADMIN REPLY =================
# @csrf_exempt
# def admin_reply(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid method"}, status=405)

#     try:
#         data = json.loads(request.body or "{}")
#     except json.JSONDecodeError:
#         return JsonResponse({'error': 'Invalid JSON'}, status=400)

#     contact_id = data.get("contact_id")
#     token = data.get("token") or data.get("token_number")
#     message = (data.get("message") or "").strip()

#     if not (contact_id or token) or not message:
#         return JsonResponse({"error": "Missing contact_id/token or message"}, status=400)

#     contact = None
#     if contact_id:
#         contact = ContactInfo.objects.filter(id=int(contact_id)).first()
#     elif token:
#         if isinstance(token, str) and token.upper().startswith("TKN-"):
#             try:
#                 possible_id = int(token.split("-", 1)[1])
#                 contact = ContactInfo.objects.filter(id=possible_id).first()
#             except Exception:
#                 pass
#         if not contact:
#             contact = ContactInfo.objects.filter(token_number=token).first()

#     if not contact:
#         return JsonResponse({"error": "Contact not found"}, status=404)

#     msg = Message.objects.create(sender="admin", text=message, contact=contact)
#     # try to attach last known geo from session if available (non-blocking)
#     geo = None
#     try:
#         geo = getattr(request, "session", {}).get("user_geo")
#     except Exception:
#         geo = None

#     payload = {
#         "id": msg.id,
#         "contact_id": contact.id,
#         "token": f"TKN-{contact.id}",
#         "sender": "admin",
#         "text": message,
#         "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
#         # --- GEO included in SSE to user + admin (added) ---
#         "geo": geo,
#     }
#     _broadcast_user(contact.id, payload)
#     _broadcast_admin(payload)

#     return JsonResponse({"status": "success", "message": "Sent", "token": f"TKN-{contact.id}"})

# admin_send_message = admin_reply

# # ================= MESSAGES API =================
# class MessageListCreateView(generics.ListCreateAPIView):
#     queryset = Message.objects.all().order_by('-timestamp')
#     serializer_class = MessageSerializer

# # ================= CONTACT API =================
# @csrf_exempt
# def save_contact(request):
#     if request.method != "POST":
#         return JsonResponse({"status": "error", "message": "Invalid request"}, status=405)

#     try:
#         if request.content_type and "application/json" in request.content_type:
#             data = json.loads(request.body or "{}")
#             contact_value = data.get("contact_value")
#             contact_type = data.get("contact_type", "temp")
#         else:
#             contact_value = request.POST.get("contact_value")
#             contact_type = request.POST.get("contact_type", "temp")
#     except json.JSONDecodeError:
#         contact_value, contact_type = None, "temp"

#     # --- IP + GEO (added) ---
#     client_ip, _ = get_client_ip(request)
#     user_ip = client_ip or request.META.get("REMOTE_ADDR", "unknown")
#     geo = _get_geo_from_ip(user_ip)
#     request.session["user_geo"] = geo

#     contact = _get_or_create_contact(request, user_ip)

#     if contact_value:
#         if contact_type == "phone":
#             contact.mobile = contact_value
#         elif contact_type == "email":
#             contact.email = contact_value
#         contact.contact_value = contact_value
#         contact.contact_type = contact_type
#         contact.save()
#         request.session["contact_saved"] = True

#     return JsonResponse({
#         "status": "success",
#         "id": contact.id,
#         "token": f"TKN-{contact.id}",
#         # --- GEO included in API response (added) ---
#         "geo": geo,
#     })

# def get_contacts(request):
#     contacts_qs = ContactInfo.objects.all().order_by("-created_at").values(
#         "id", "token_number", "mobile", "email", "contact_value", "created_at", "is_seen"
#     )
#     contacts = list(contacts_qs)
#     for c in contacts:
#         c["token"] = c.get("token_number") or f"TKN-{c['id']}"
#     return JsonResponse({"contacts": contacts})

# def get_messages(request, contact_id):
#     try:
#         contact = ContactInfo.objects.get(id=contact_id)
#         messages = Message.objects.filter(contact=contact).order_by("timestamp")
#         data = [
#             {
#                 "id": msg.id,
#                 "sender": msg.sender.lower(),
#                 "text": msg.text,
#                 "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M"),
#             }
#             for msg in messages
#         ]
#         # also return last known geo from session if present
#         geo = None
#         try:
#             geo = request.session.get("user_geo")
#         except Exception:
#             geo = None

#         return JsonResponse({
#             "messages": data,
#             "token": f"TKN-{contact.id}",
#             "token_number": contact.token_number,
#             "geo": geo,  # (added)
#         })
#     except ContactInfo.DoesNotExist:
#         return JsonResponse({"error": "Contact not found"}, status=404)

# # ================= STATS API =================
# def stats(request):
#     total_contacts = ContactInfo.objects.count()
#     total_messages = Message.objects.count()
#     total_visitors = ContactInfo.objects.values("contact_value").distinct().count()

#     total_chats = Message.objects.values("contact_id").distinct().count()

#     page_views_agg = ContactInfo.objects.aggregate(total=Sum('page_views'))
#     total_pageviews = page_views_agg.get('total') or 0

#     sender_stats = list(Message.objects.values("sender").annotate(total=Count("id")))

#     now = timezone.now()

#     visitors_by_month_qs = ContactInfo.objects.annotate(
#         y=ExtractYear('created_at'), m=ExtractMonth('created_at')
#     ).values('y', 'm').annotate(total=Count('id')).order_by('y', 'm')

#     messages_by_month_qs = Message.objects.annotate(
#         y=ExtractYear('timestamp'), m=ExtractMonth('timestamp')
#     ).values('y', 'm').annotate(total=Count('id')).order_by('y', 'm')

#     pageviews_by_month_qs = ContactInfo.objects.annotate(
#         y=ExtractYear('created_at'), m=ExtractMonth('created_at')
#     ).values('y', 'm').annotate(total=Sum('page_views')).order_by('y', 'm')

#     vis_lookup = {f"{r['y']}-{int(r['m']):02d}": r['total'] for r in visitors_by_month_qs}
#     msg_lookup = {f"{r['y']}-{int(r['m']):02d}": r['total'] for r in messages_by_month_qs}
#     pv_lookup = {f"{r['y']}-{int(r['m']):02d}": r['total'] or 0 for r in pageviews_by_month_qs}

#     months = []
#     visitors_data = []
#     chats_data = []
#     page_views_dist = []

#     for i in range(5, -1, -1):
#         target = (now - timezone.timedelta(days=30 * i))
#         y = target.year
#         m = target.month
#         label = f"{y}-{m:02d}"
#         months.append(label)
#         visitors_data.append(vis_lookup.get(label, 0))
#         chats_data.append(msg_lookup.get(label, 0))
#         page_views_dist.append(pv_lookup.get(label, 0))

#     feedback_percent = 0
#     if total_messages > 0:
#         feedback_percent = min(100, (total_contacts * 10) // total_messages)

#     return JsonResponse({
#         "total_visitors": total_visitors,
#         "total_chats": total_chats,
#         "page_views_total": total_pageviews,
#         "feedback_percent": feedback_percent,

#         "contacts": total_contacts,
#         "messages": total_messages,
#         "sender_stats": sender_stats,
#         "months": months,
#         "visitors_data": visitors_data,
#         "chats_data": chats_data,
#         "page_views_dist": page_views_dist,
#     })

# from django.shortcuts import render, redirect
# from django.views.decorators.csrf import csrf_exempt
# from django.core.validators import validate_email
# from django.core.exceptions import ValidationError
# from django.utils import timezone
# from django.http import JsonResponse, StreamingHttpResponse
# from django.contrib import messages
# from django.contrib.auth.hashers import make_password, check_password
# from django.utils.crypto import get_random_string

# from rest_framework import generics

# import json, difflib, re
# from queue import Queue

# from .models import (
#     Message, ContactInfo, WebsiteRegistration, Chat
# )
# from .serializers import MessageSerializer, WebsiteRegistrationSerializer

# # ================= KEYWORD BOT =================
# RESPONSES = {
#     "hello": "Hello! How can we help?",
#     "hi": "Hi there! How can we assist you?",
#     "hello": "Hello! How can we help?",
#     "contact": "9939791122?",
# }

# def _best_reply(user_message: str) -> str:
#     if not user_message:
#         return "Hello! How can I help you?"
#     user_message = user_message.lower().strip()
#     match = difflib.get_close_matches(user_message, RESPONSES.keys(), n=1, cutoff=0.6)
#     if match:
#         return RESPONSES[match[0]]
#     for key, reply in RESPONSES.items():
#         if key in user_message:
#             return reply
#     return "Hello! How can I help you?"

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
# def chat_view(request):
#     website_id = "ZWVhhTr5vE"  # ya dynamic logic se pick karo
#     return render(request, "chat.html", {"website_id": website_id})

def chat_view(request):
    host = request.get_host()  # example: "example.com:8000"
    try:
        website = WebsiteRegistration.objects.get(website_url__icontains=host)
        website_id = website.website_id
    except WebsiteRegistration.DoesNotExist:
        website_id = None  # fallback, ya show error
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

def _get_or_create_contact(request, website_id=None) -> tuple:
    if not request.session.session_key:
        request.session.create()

    contact_id = request.session.get("contact_id")
    session_start = request.session.get("session_start")

    website = None
    if website_id:
        website = WebsiteRegistration.objects.filter(website_id=website_id).first()

    contact = ContactInfo.objects.filter(id=contact_id).first() if contact_id else None

    if (not contact) or (not session_start) or (timezone.datetime.fromisoformat(session_start) < SERVER_START_TIME):
        contact = ContactInfo.objects.create(contact_type="temp", website=website)
        request.session["contact_id"] = contact.id
        request.session["session_start"] = str(SERVER_START_TIME)
        request.session["ask_count"] = 0
        request.session["contact_saved"] = False

    chat = Chat.objects.filter(contact=contact).last()
    if not chat:
        chat = Chat.objects.create(
            chat_id=f"CHAT-{contact.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            contact=contact
        )

    return contact, chat

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

        return JsonResponse({"status": "success", "msg": "Bot response सफलतापूर्वक save हुआ"})

    return JsonResponse({"status": "error", "msg": "Invalid request"}, status=405)
