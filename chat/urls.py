# from django.urls import path
# from . import views

# urlpatterns = [
#     # Chat page
#     path("", views.chat_view, name="chat_page"),

#     # User chat APIs
#     path("api/save-contact/", views.save_contact, name="save_contact"),
#     path("api/get-response/", views.get_response, name="get_response"),
#     path("api/user-stream/<int:contact_id>/", views.user_stream, name="user_stream"),

#     # Admin panel
#     path("admin-panel/", views.admin_panel_view, name="admin_panel"),
#     path("api/admin-reply/", views.admin_reply, name="admin_reply"),
#     path("api/lead-stream/", views.lead_stream, name="lead_stream"),
#     path("api/contacts/", views.get_contacts, name="get_contacts"),
#     path("api/messages/<int:contact_id>/", views.get_messages, name="get_messages"),

#     # Django REST Framework endpoints
#     path("api/messages/", views.MessageListCreateView.as_view(), name="message_list_create"),
#     path("api/admin-send/", views.admin_send_message, name="admin_send_message"),

#     # Stats API
#     path("api/stats/", views.stats, name="stats"),
# ]





from django.urls import path
from . import views

urlpatterns = [
    # ========================
    # 💬 Chat & User Facing APIs
    # ========================
    path("chat/", views.chat_view, name="chat_page"),                        # Chat page render
    path("api/get-response/", views.get_response, name="get_response"), # Bot/user chat API
    path("api/user-stream/<int:contact_id>/", views.user_stream, name="user_stream"), # SSE for users

    # ========================
    # 🔑 Website Admin Login/Logout
    # ========================
   path("admin-login/", views.website_admin_login, name="website_admin_login"),
    path("admin-register/", views.website_admin_register, name="website_admin_register"),
    path("admin-logout/", views.website_admin_logout, name="website_admin_logout"),

    # ========================
    # 🛠 Admin Panel (Protected) + APIs
    # ========================
    path("admin-panel/", views.admin_panel_view, name="admin_panel"),   # Locked Admin Panel
    path("api/admin-reply/", views.admin_reply, name="admin_reply"),    # Admin reply to users
    path("api/lead-stream/", views.lead_stream, name="lead_stream"),    # SSE for admin dashboard
    path("api/contacts/", views.get_contacts, name="get_contacts"),    # All contacts list
    path("api/messages/<int:contact_id>/", views.get_messages, name="get_messages"), # Messages of one contact
    path("api/save-contact/", views.save_contact, name="save_contact"), # Save user contact
    path("api/messages/", views.MessageListCreateView.as_view(), name="message_list_create"), # DRF messages list
    path("api/admin-send/", views.admin_send_message, name="admin_send_message"),   # Admin send message
    path('api/save-bot-response/', views.save_bot_response, name='save_bot_response'),

    # ========================
    # 📊 Dashboard & Stats
    # ========================
    path("api/stats/", views.stats, name="stats"),

  # Website
    path("save-website/", views.save_website, name="save_website"),
]
