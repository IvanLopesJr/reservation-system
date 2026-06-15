from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='E-mail')
    username = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f'{self.get_full_name()} <{self.email}>'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_access_completed = models.BooleanField(default=False, verbose_name='Primeiro acesso concluído')
    created_by_admin = models.BooleanField(default=True, verbose_name='Criado por administrador')
    can_use_parking = models.BooleanField(default=True, verbose_name='Pode usar estacionamento')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Perfil de usuário'
        verbose_name_plural = 'Perfis de usuários'

    def __str__(self):
        return f'Perfil de {self.user.email}'


class AccessInvitation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations')
    token_hash = models.CharField(max_length=128, verbose_name='Hash do token')
    expires_at = models.DateTimeField(verbose_name='Expira em')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='Usado em')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='created_invitations', verbose_name='Criado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Convite de acesso'
        verbose_name_plural = 'Convites de acesso'

    @property
    def is_used(self):
        return self.used_at is not None

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def __str__(self):
        return f'Convite para {self.user.email}'
