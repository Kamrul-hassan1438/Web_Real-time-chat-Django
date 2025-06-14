from django.contrib import admin
from .models import Message, UserProfile, ChatConnection


admin.site.register(Message)

admin.site.register(UserProfile)
admin.site.register(ChatConnection)