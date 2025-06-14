from django.urls import path, include
from chat import views as chat_views
from django.contrib.auth.views import LoginView, LogoutView
from .views import login_user, user_list, mark_message_as_read
from . import views

urlpatterns = [
    path("login/", login_user, name="login-user"),
    path("users/", user_list, name="user-list"),
    path("messages/<str:sender_username>/<str:recipient_username>/", views.get_chat_messages),
    path('messages/<int:message_id>/mark-as-read/', mark_message_as_read),
    path("connected-users/<str:username>/", views.connected_users_view, name="connected_users"),

    # login-section
    path("auth/login/", LoginView.as_view(template_name="chat/LoginPage.html"), name="login-user"),
    path("auth/logout/", LogoutView.as_view(), name="logout-user"),
    path("status/<str:username>/", chat_views.user_status, name="user-status"),

]
