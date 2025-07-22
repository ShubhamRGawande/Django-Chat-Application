from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from .models import Message
from .forms import RegisterForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def home(request):
    if request.user.is_authenticated:
        return redirect('user_list')
    return render(request, 'chat/home.html')


@login_required
def user_list(request):
    """
    Display all users with last message and unread count
    """
    users = User.objects.exclude(id=request.user.id).annotate(
        unread_count=Count(
            'sent_messages',
            filter=Q(sent_messages__receiver=request.user, sent_messages__read=False)
        )
    )

    for user in users:
        last_message = Message.objects.filter(
            Q(sender=request.user, receiver=user) |
            Q(sender=user, receiver=request.user)
        ).order_by('-timestamp').first()

        user.last_message = last_message.content if last_message else None
        user.last_message_time = last_message.timestamp if last_message else None
        user.last_message_sender = last_message.sender.username if last_message else None

    return render(request, 'chat/user_list.html', {
        'users': users,
        'current_user': request.user
    })


@login_required
def chat_room(request, username):
    """
    Display chat room with message history and mark messages as read
    """
    other_user = get_object_or_404(User, username=username)
    if other_user == request.user:
        return redirect('user_list')

    # Mark all messages from this user as read
    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        read=False
    ).update(read=True)

    # Get all users for sidebar (with unread counts)
    users = User.objects.exclude(id=request.user.id).annotate(
        unread_count=Count(
            'sent_messages',
            filter=Q(sent_messages__receiver=request.user, sent_messages__read=False)
        )
    )

    # Get message history (both directions)
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')[:100]  # Limit to 100 most recent messages

    return render(request, 'chat/chat_room.html', {
        'other_user': other_user,
        'users': users,
        'messages': messages,
        'current_user': request.user
    })


@require_POST
@login_required
def mark_messages_read(request, username):
    """
    API endpoint to mark messages as read (called via AJAX)
    """
    try:
        other_user = User.objects.get(username=username)
        Message.objects.filter(
            sender=other_user,
            receiver=request.user,
            read=False
        ).update(read=True)
        return JsonResponse({'status': 'success'})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)


def register(request):
    """
    User registration with auto-login
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_list')
    else:
        form = RegisterForm()

    return render(request, 'chat/register.html', {'form': form})


@login_required
def delete_message(request, message_id):
    """
    Delete a message (soft delete implementation recommended)
    """
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    message.delete()
    return JsonResponse({'status': 'success'})
