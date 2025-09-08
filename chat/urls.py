
# from django.urls import path
# from . import views

# urlpatterns = [
#     path("", views.chat_view, name="chat_page"),
#     path("api/get-response/", views.get_response, name="get_response"),
#     path("api/user-stream/<int:contact_id>/", views.user_stream, name="user_stream"),

#     # Admin panel
#     path("admin-panel/", views.admin_panel_view, name="admin_panel"),
#     path("api/admin-reply/", views.admin_reply, name="admin_reply"),
#     path("api/lead-stream/", views.lead_stream, name="lead_stream"),
#     path("api/contacts/", views.get_contacts, name="get_contacts"),
#     path("api/messages/<int:contact_id>/", views.get_messages, name="get_messages"),
#     path("api/save-contact/", views.save_contact, name="save_contact"),

#     # DRF API
#     path("api/messages/", views.MessageListCreateView.as_view(), name="message_list_create"),
#     path("api/admin-send/", views.admin_send_message, name="admin_send_message"),

#     # ✅ Stats API
#     path("api/stats/", views.stats, name="stats"),
# ]










from django.urls import path
from . import views

urlpatterns = [
    # ==== Main Chat Page ====
    path("", views.chat_view, name="chat_page"),

    # ==== Chatbot APIs ====
    path("api/get-response/", views.get_response, name="get_response"),
    path("api/save-contact/", views.save_contact, name="save_contact"),

    # ==== Streaming (SSE) ====
    path("api/user-stream/<int:contact_id>/", views.user_stream, name="user_stream"),
    path("api/lead-stream/", views.lead_stream, name="lead_stream"),

    # ==== Admin Panel ====
    path("admin-panel/", views.admin_panel_view, name="admin_panel"),
    path("api/admin-reply/", views.admin_reply, name="admin_reply"),
    path("api/admin-send/", views.admin_send_message, name="admin_send_message"),

    # ==== Contacts & Messages ====
    path("api/contacts/", views.get_contacts, name="get_contacts"),
    path("api/messages/<int:contact_id>/", views.get_messages, name="get_messages"),
    path("api/messages/", views.MessageListCreateView.as_view(), name="message_list_create"),

    # ==== Stats API ====
    path("api/stats/", views.stats, name="stats"),
]
