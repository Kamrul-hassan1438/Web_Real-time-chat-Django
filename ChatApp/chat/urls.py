from django.urls import path, include
from chat import views as chat_views
from django.contrib.auth.views import LoginView, LogoutView
from .views import login_user, chatPage

urlpatterns = [
    path("", chat_views.chatPage, name="chat-page"),
    path("login/", login_user, name="login-user"),
    path("chat/", chatPage, name="chat-page"),

    # login-section
    path("auth/login/", LoginView.as_view(template_name="chat/LoginPage.html"), name="login-user"),
    path("auth/logout/", LogoutView.as_view(), name="logout-user"),
]
