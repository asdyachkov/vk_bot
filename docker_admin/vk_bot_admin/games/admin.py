from django.contrib import admin
from .models import Admin, Game, Round, Player, Leader


class AdminAdmin(admin.ModelAdmin):
    list_display = ("vk_id", "email")
    list_display_links = ("vk_id", "email")
    search_fields = ("email",)


class GameAdmin(admin.ModelAdmin):
    list_display = ("chat_id", "created_at", "is_start", "is_end")
    list_display_links = ("chat_id",)
    search_fields = ("chat_id", "is_start", "is_end")


class PlayerAdmin(admin.ModelAdmin):
    list_display = ("vk_id", "is_admin", "name", "last_name")
    list_display_links = ("vk_id", "name", "last_name")
    search_fields = ("vk_id", "is_admin", "name", "last_name")


class LeaderAdmin(admin.ModelAdmin):
    list_display = ("vk_id", "is_admin", "name", "last_name")
    list_display_links = ("vk_id", "name", "last_name")
    search_fields = ("vk_id", "is_admin", "name", "last_name")


admin.site.register(Admin, AdminAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Round)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Leader, LeaderAdmin)
