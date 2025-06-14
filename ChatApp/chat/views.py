from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q

from .models import UserProfile
from django.contrib.auth.decorators import login_required
from .models import Message
from django.contrib.auth.models import User


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message,ChatConnection

from django.http import JsonResponse
from .models import Message as ChatMessage
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User








@csrf_exempt
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print("Login successful")
            return JsonResponse({"message": "Login successful"}, status=200)
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

    return JsonResponse({"error": "Method not allowed"}, status=405)





def user_status(request, username):
    try:
        profile = UserProfile.objects.get(user__username=username)
        return JsonResponse({'username': username, 'is_online': profile.is_online})
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)



def user_list(request):
    users = User.objects.all().values("id", "username")
    return JsonResponse(list(users), safe=False)






@csrf_exempt
def get_chat_messages(request, sender_username, recipient_username):
    if request.method == "GET":
        try:
            sender = User.objects.get(username=sender_username)
            recipient = User.objects.get(username=recipient_username)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        messages = ChatMessage.objects.filter(
            sender__in=[sender, recipient],
            recipient__in=[sender, recipient]
        ).order_by("timestamp")

        message_list = [
            {
                "sender": msg.sender.username,
                "recipient": msg.recipient.username,
                "message": msg.message,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                # Remove 'read' if not in model
            }
            for msg in messages
        ]

        return JsonResponse(message_list, safe=False)





def get_previous_chats(request, username):
    user = User.objects.get(username=username)
    connections = ChatConnection.objects.filter(Q(user1=user) | Q(user2=user))


    other_users = []
    for conn in connections:
        other = conn.user2 if conn.user1 == user else conn.user1
        other_users.append({
            "username": other.username,
            "last_interaction": conn.last_interaction
        })

    return JsonResponse(other_users, safe=False)




@csrf_exempt
def connected_users_view(request, username):
    try:
        user = User.objects.get(username=username)
        connections = ChatConnection.objects.filter(user1=user) | ChatConnection.objects.filter(user2=user)
        
        connected_users = []
        for connection in connections:
            connected_user = connection.user2 if connection.user1 == user else connection.user1
            connected_users.append({
                "id": connected_user.id,
                "username": connected_user.username
            })

        return JsonResponse(connected_users, safe=False)

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)





@csrf_exempt
def mark_message_as_read(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
        # Mark the message as read
        message.is_read = True
        message.save()
        return JsonResponse({"status": "success"})
    except Message.DoesNotExist:
        return JsonResponse({"error": "Message not found"}, status=404)