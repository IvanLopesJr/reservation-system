import hashlib
import secrets
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import AccessInvitation, UserProfile

User = get_user_model()


class InvitationService:

    @staticmethod
    def create_invitation(user, created_by):
        InvitationService.invalidate_previous(user)
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expires_at = timezone.now() + timedelta(hours=48)

        invitation = AccessInvitation.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=expires_at,
            created_by=created_by,
        )
        invitation._plain_token = token
        return invitation

    @staticmethod
    def validate_token(token):
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        try:
            invitation = AccessInvitation.objects.get(token_hash=token_hash)
        except AccessInvitation.DoesNotExist:
            return None

        if invitation.is_used:
            return None
        if invitation.is_expired:
            return None
        return invitation

    @staticmethod
    def mark_as_used(invitation):
        invitation.used_at = timezone.now()
        invitation.save(update_fields=['used_at'])

    @staticmethod
    def invalidate_previous(user):
        now = timezone.now()
        AccessInvitation.objects.filter(
            user=user,
            used_at__isnull=True,
            expires_at__gte=now,
        ).update(expires_at=now)


class UserProfileService:

    @staticmethod
    def create_profile(user, created_by_admin=True):
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'created_by_admin': created_by_admin},
        )
        return profile

    @staticmethod
    def complete_first_access(user):
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.first_access_completed = True
        profile.save(update_fields=['first_access_completed'])
        return profile
