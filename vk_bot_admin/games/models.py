import django
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    REQUIRED_FIELDS = ('email', )
    USERNAME_FIELD = "username"
    is_anonymous = False
    is_authenticated = False

    username = models.TextField(null=False, unique=True)

    def __str__(self):
        return self.username


class Admin(models.Model):
    email = models.TextField(null=False, unique=True)
    password = models.TextField(null=False)
    salt = models.TextField(null=False)
    vk_id = models.IntegerField(null=False, unique=True)

    class Meta:
        verbose_name = "Администратор"
        verbose_name_plural = "Администраторы"
        db_table = "admins"


class Game(models.Model):

    chat_id = models.IntegerField(null=False)
    is_start = models.BooleanField(null=False, default=False)
    is_end = models.BooleanField(null=False, default=False)
    created_at = models.DateTimeField(null=False, default=django.utils.timezone.now)

    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"
        db_table = "games"


class Round(models.Model):

    state = models.IntegerField(null=False, default=0)
    game = models.OneToOneField("Game", on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = "Роунд"
        verbose_name_plural = "Роунды"
        db_table = "rounds"


class Player(models.Model):

    vk_id = models.IntegerField(null=False)
    is_admin = models.BooleanField(null=False, default=False)
    name = models.TextField(null=False)
    last_name = models.TextField(null=False)
    photo_id = models.TextField(null=False)
    score = models.IntegerField(null=False, default=0)
    state = models.IntegerField(null=False, default=0)
    is_plaid = models.BooleanField(null=False, default=False)
    is_voited = models.BooleanField(null=False, default=False)
    round = models.ForeignKey('Round', null=False, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"
        db_table = "players"


class Leader(models.Model):

    vk_id = models.IntegerField(null=False)
    is_admin = models.BooleanField(null=False, default=False)
    name = models.TextField(null=False)
    last_name = models.TextField(null=False)
    photo_id = models.TextField(null=False)
    total_score = models.IntegerField(null=False, default=0)
    total_wins = models.IntegerField(null=False, default=0)

    class Meta:
        verbose_name = "Лидер"
        verbose_name_plural = "Лидеры"
        db_table = "leaders"
