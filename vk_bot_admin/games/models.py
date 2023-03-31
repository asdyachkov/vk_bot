import django
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    REQUIRED_FIELDS = ("email",)
    USERNAME_FIELD = "username"
    is_anonymous = False
    is_authenticated = False

    username = models.TextField(null=False, unique=True)

    def __str__(self):
        return self.username


class Admin(models.Model):
    email = models.TextField(null=False, unique=True)
    password = models.TextField(null=False, verbose_name="Пароль")
    salt = models.TextField(null=False)
    vk_id = models.IntegerField(null=False, unique=True)

    class Meta:
        verbose_name = "Администратор"
        verbose_name_plural = "Администраторы"
        db_table = "admins"
        ordering = [
            "vk_id",
        ]

    def __str__(self):
        return str(self.vk_id)


class Game(models.Model):

    chat_id = models.IntegerField(null=False)
    is_start = models.BooleanField(null=False, default=False)
    is_end = models.BooleanField(null=False, default=False)
    created_at = models.DateTimeField(
        null=False,
        default=django.utils.timezone.now,
        verbose_name="Время создания",
    )

    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"
        db_table = "games"
        ordering = ["created_at", "chat_id"]

    def __str__(self):
        return str(self.chat_id)


class Round(models.Model):

    state = models.IntegerField(null=False, default=0, verbose_name="Состояние")
    game = models.OneToOneField("Game", on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = "Раунд"
        verbose_name_plural = "Раунды"
        db_table = "rounds"
        ordering = [
            "state",
        ]

    def __str__(self):
        return str(self.state)


class Player(models.Model):

    vk_id = models.IntegerField(null=False)
    is_admin = models.BooleanField(
        null=False, default=False, verbose_name="Администратор ли"
    )
    name = models.TextField(null=False, verbose_name="Имя")
    last_name = models.TextField(null=False, verbose_name="Фамилия")
    photo_id = models.TextField(null=False)
    score = models.IntegerField(
        null=False, default=0, verbose_name="Количество очков"
    )
    state = models.IntegerField(null=False, default=0, verbose_name="Состояние")
    is_plaid = models.BooleanField(
        null=False, default=False, verbose_name="Сыграл ли"
    )
    is_voited = models.BooleanField(
        null=False, default=False, verbose_name="Проголосовал ли"
    )
    round = models.ForeignKey("Round", null=False, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}, {self.vk_id}"

    class Meta:
        verbose_name = "Игрок"
        verbose_name_plural = "Игроки"
        db_table = "players"
        ordering = [
            "name",
            "last_name",
        ]


class Leader(models.Model):

    vk_id = models.IntegerField(null=False)
    is_admin = models.BooleanField(
        null=False, default=False, verbose_name="Администратор ли"
    )
    name = models.TextField(null=False, verbose_name="Имя")
    last_name = models.TextField(null=False, verbose_name="Фамилия")
    photo_id = models.TextField(null=False)
    total_score = models.IntegerField(
        null=False, default=0, verbose_name="Общее количество очков"
    )
    total_wins = models.IntegerField(
        null=False, default=0, verbose_name="Общее количество побед"
    )

    def __str__(self):
        return f"{self.name}, {self.vk_id}"

    class Meta:
        verbose_name = "Лидер"
        verbose_name_plural = "Лидеры"
        db_table = "leaders"
        ordering = [
            "name",
            "last_name",
        ]
