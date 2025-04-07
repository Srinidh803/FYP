from django.contrib import admin
from .models import PlayerProfile

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'experience', 'is_top_player', 'is_trending_player']
    list_filter = ['is_top_player', 'is_trending_player', 'game', 'state']
    search_fields = ['user__username', 'game', 'college', 'district']
    list_editable = ['is_top_player', 'is_trending_player']
