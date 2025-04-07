from django.db import models
from django.contrib.auth.models import User

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True,default='profile_images/default.png')

    game = models.CharField(max_length=100)
    experience = models.PositiveIntegerField(help_text="Experience in years")
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    college = models.CharField(max_length=150, blank=True, null=True)
    country = models.CharField(max_length=100)

    skills = models.TextField(help_text="Comma-separated skills")
    self_rating = models.FloatField(default=0.0)

    available_from = models.TimeField()
    available_to = models.TimeField()

    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_top_player = models.BooleanField(default=False)
    is_trending_player = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
# models.py

class PlayerRating(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')
    
    rating = models.FloatField()
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')  # Prevent multiple reviews

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.rating})"
    
class PlayerRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.status})"
    

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}"
    
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Post"




