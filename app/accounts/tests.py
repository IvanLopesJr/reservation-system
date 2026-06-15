import pytest
from django.contrib.auth import get_user_model
from accounts.models import AccessInvitation, UserProfile
from accounts.services import InvitationService, UserProfileService

User = get_user_model()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email='admin@test.com', password='test123',
        first_name='Admin', is_staff=True,
    )


@pytest.fixture
def new_user(db):
    return User.objects.create_user(
        email='user@test.com', password='test123',
        first_name='User',
    )


class TestUserProfileService:
    def test_create_profile(self, db, new_user):
        UserProfileService.create_profile(new_user)
        assert UserProfile.objects.filter(user=new_user).exists()

    def test_complete_first_access(self, db, new_user):
        UserProfileService.complete_first_access(new_user)
        profile = UserProfile.objects.get(user=new_user)
        assert profile.first_access_completed is True


class TestInvitationService:
    def test_create_invitation_generates_token(self, db, admin_user, new_user):
        invitation = InvitationService.create_invitation(new_user, admin_user)
        assert invitation.user == new_user
        assert invitation.created_by == admin_user
        assert invitation.token_hash
        assert hasattr(invitation, '_plain_token')
        assert invitation._plain_token

    def test_validate_valid_token(self, db, admin_user, new_user):
        invitation = InvitationService.create_invitation(new_user, admin_user)
        token = invitation._plain_token
        validated = InvitationService.validate_token(token)
        assert validated is not None
        assert validated.id == invitation.id

    def test_validate_used_token(self, db, admin_user, new_user):
        invitation = InvitationService.create_invitation(new_user, admin_user)
        InvitationService.mark_as_used(invitation)
        token = invitation._plain_token
        validated = InvitationService.validate_token(token)
        assert validated is None

    def test_validate_invalid_token(self, db):
        validated = InvitationService.validate_token('invalid-token')
        assert validated is None

    def test_mark_as_used(self, db, admin_user, new_user):
        invitation = InvitationService.create_invitation(new_user, admin_user)
        InvitationService.mark_as_used(invitation)
        invitation.refresh_from_db()
        assert invitation.is_used

    def test_invalidate_previous(self, db, admin_user, new_user):
        first = InvitationService.create_invitation(new_user, admin_user)
        second = InvitationService.create_invitation(new_user, admin_user)
        first.refresh_from_db()
        assert first.is_expired
        assert not second.is_expired


class TestUserModel:
    def test_login_by_email(self, db):
        user = User.objects.create_user(
            email='login@test.com', password='pass123',
            first_name='Test',
        )
        UserProfileService.complete_first_access(user)
        from django.contrib.auth import authenticate
        authenticated = authenticate(username='login@test.com', password='pass123')
        assert authenticated is not None
        assert authenticated.email == 'login@test.com'

    def test_inactive_user_cannot_login(self, db):
        user = User.objects.create_user(
            email='inactive@test.com', password='pass123',
            first_name='Test', is_active=False,
        )
        from django.contrib.auth import authenticate
        authenticated = authenticate(username='inactive@test.com', password='pass123')
        assert authenticated is None
