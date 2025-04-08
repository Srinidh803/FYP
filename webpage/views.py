# webpage/views.py

from django.shortcuts import render
from datetime import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import PlayerProfile, PlayerRequest, PlayerRating, ChatMessage, Post
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages


# Home View
def home(request):
    top_players = PlayerProfile.objects.filter(is_top_player=True).select_related('user')
    trending_players = PlayerProfile.objects.filter(is_trending_player=True).select_related('user')
    
    return render(request, 'index.html', {
        'top_players': top_players,
        'trending_players': trending_players,
    })


# Search View
@login_required
def search(request):
    players = PlayerProfile.objects.exclude(user=request.user)
    
    game = request.GET.get('game')
    state = request.GET.get('state')
    experience = request.GET.get('experience')
    available_from = request.GET.get('available_from')
    available_to = request.GET.get('available_to')

    if game:
        players = players.filter(game__icontains=game)
    if state:
        players = players.filter(state__icontains=state)
    if experience:
        players = players.filter(experience__gte=experience)
    if available_from and available_to:
        players = players.filter(
            available_from__lte=available_from,
            available_to__gte=available_to
        )

    return render(request, 'search.html', {'search_results': players})

def player_profile(request, username):
    player = get_object_or_404(User, username=username)
    profile = get_object_or_404(PlayerProfile, user=player)
    posts = Post.objects.filter(user=player).order_by('-created_at')
    reviews = PlayerRating.objects.filter(to_user=player)

    return render(request, 'profile.html', {
        'player': player,
        'profile': profile,
        'posts': posts,
        'reviews': reviews
    })


@login_required
def add_player(request, username):
    print(f"🛎️ Received request to add {username}")

    if request.method == 'POST':
        try:
            to_user = User.objects.get(username=username)
        except User.DoesNotExist:
            print("❌ User not found.")
            return redirect('home')  # or show some error

        # Prevent duplicate requests
        if PlayerRequest.objects.filter(from_user=request.user, to_user=to_user, status='pending').exists():
            print("⚠️ Duplicate request detected.")
            return redirect('profile', username=username)

        pr = PlayerRequest(from_user=request.user, to_user=to_user)
        pr.save()
        print(f"✅ PlayerRequest created: {pr.from_user.username} ➡ {pr.to_user.username}")

    return redirect('profile', username=username)


@login_required
def manage_requests(request):
    # Incoming requests to the current user
    incoming = PlayerRequest.objects.filter(to_user_id=request.user.id, status='pending')
    print(f"Checking requests for user ID: {request.user.id}")

    all_reqs = PlayerRequest.objects.all()
    print(f"📋 DEBUG: Total PlayerRequests: {all_reqs.count()}")
    for r in all_reqs:
        print(f"📦 Request ID: {r.id} | From: {r.from_user.username} (ID: {r.from_user.id}) ➡ To: {r.to_user.username} (ID: {r.to_user.id}) | Status: {r.status}")

    return render(request, 'manage_requests.html', {'incoming': incoming})

    if request.method == 'POST':
        req_id = request.POST.get('request_id')
        action = request.POST.get('action')
        req = get_object_or_404(PlayerRequest, id=req_id, to_user=request.user)

        if action == 'accept':
            req.status = 'accepted'
            req.save()

            # Optionally create a reverse request to show in both users' chats
            PlayerRequest.objects.get_or_create(
                from_user=request.user,
                to_user=req.from_user,
                defaults={'status': 'accepted'}
            )

        elif action == 'decline':
            req.delete()

        return redirect('manage_requests')

    return render(request, 'manage_requests.html', {'incoming': incoming})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import ChatMessage, PlayerRequest
from django.contrib.auth.models import User

@login_required
def chat_page(request):
    # Users who sent request to you and it was accepted
    accepted_from_others = PlayerRequest.objects.filter(
        to_user=request.user, status='accepted'
    ).values_list('from_user', flat=True)

    # Users you sent request to and it was accepted
    accepted_by_you = PlayerRequest.objects.filter(
        from_user=request.user, status='accepted'
    ).values_list('to_user', flat=True)

    # Union of both
    all_accepted_user_ids = list(accepted_from_others) + list(accepted_by_you)

    contacts = User.objects.filter(id__in=all_accepted_user_ids)

    selected_user = None
    messages = []

    username = request.GET.get('user')
    if username:
        selected_user = get_object_or_404(User, username=username)

        if selected_user.id in all_accepted_user_ids:
            messages = ChatMessage.objects.filter(
                Q(sender=request.user, receiver=selected_user) |
                Q(sender=selected_user, receiver=request.user)
            ).order_by('timestamp')

            if request.method == 'POST':
                content = request.POST.get('message')
                if content:
                    ChatMessage.objects.create(
                        sender=request.user,
                        receiver=selected_user,
                        message=content
                    )
                    return redirect(f"{request.path}?user={selected_user.username}")
        else:
            selected_user = None  # Don't allow chatting with unapproved users

    return render(request, 'chat.html', {
        'contacts': contacts,
        'selected_user': selected_user,
        'messages': messages
    })




@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        Post.objects.create(user=request.user, content=content, image=image)
        return redirect('player_profile', username=request.user.username)
    return render(request, 'create_post.html')

@login_required
def rate_player(request, username):
    to_user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        rating = float(request.POST.get('rating'))
        review = request.POST.get('review')

        obj, created = PlayerRating.objects.update_or_create(
            from_user=request.user,
            to_user=to_user,
            defaults={'rating': rating, 'review': review}
        )
        return redirect('player_profile', username=username)
    return render(request, 'rate_player.html', {'to_user': to_user})


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('create_profile')  # send user to fill profile
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('home')


from .forms import PlayerProfileForm

@login_required
def create_profile(request):
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST, request.FILES)  # 👈 Add request.FILES
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('player_profile', profile.user.username)
    else:
        form = PlayerProfileForm()
    return render(request, 'create_profile.html', {'form': form})



@login_required
# views.py
def edit_profile(request):
    profile = request.user.playerprofile
    if request.method == 'POST':
        form = PlayerProfileForm(request.POST, request.FILES, instance=profile)  # 👈 request.FILES
        if form.is_valid():
            form.save()
            return redirect('player_profile', profile.user.username)
    else:
        form = PlayerProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})








