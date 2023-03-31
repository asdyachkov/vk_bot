from django.contrib import admin
from .models import Admin, Game, Round, Player, Leader


admin.site.register(Admin)
admin.site.register(Game)
admin.site.register(Round)
admin.site.register(Player)
admin.site.register(Leader)
