from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import PasswordChangeForm
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from booking.models import Reservation

from audit.services import AuditService
from notifications.services import EmailService
from system_settings.services import SystemSettingsService
from .forms import LoginForm, FirstAccessForm, UserCreateForm, UserUpdateForm
from .models import UserProfile
from .services import InvitationService, UserProfileService

User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            if not form.cleaned_data.get('remember'):
                request.session.set_expiry(0)
            profile = getattr(user, 'profile', None)
            if not profile or not profile.first_access_completed:
                return redirect('accounts:first_access_required')
            return redirect('core:dashboard')

    settings = SystemSettingsService.get_settings()
    return render(request, 'accounts/login.html', {'form': form, 'app_settings': settings})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def first_access_required(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.first_access_completed:
        return redirect('core:dashboard')
    from system_settings.services import SystemSettingsService
    return render(request, 'accounts/first_access_required.html', {'app_settings': SystemSettingsService.get_settings()})


def first_access_view(request, token):
    invitation = InvitationService.validate_token(token)
    if not invitation:
        return render(request, 'accounts/invitation_invalid.html', {'error': 'invalid'})

    if request.method == 'POST':
        form = FirstAccessForm(request.POST)
        if form.is_valid():
            user = invitation.user
            user.set_password(form.cleaned_data['password'])
            user.save()
            InvitationService.mark_as_used(invitation)
            UserProfileService.complete_first_access(user)
            messages.success(request, 'Senha definida com sucesso! Faça seu login.')
            return redirect('accounts:login')
    else:
        form = FirstAccessForm()

    return render(request, 'accounts/first_access.html', {'form': form, 'user': invitation.user})


def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                user = User.objects.get(email=email, is_active=True)
                from django.contrib.auth.tokens import default_token_generator
                from django.utils.http import urlsafe_base64_encode
                from django.utils.encoding import force_bytes
                from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm

                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                settings = SystemSettingsService.get_settings()
                base_url = settings.app_base_url if settings and settings.app_base_url else 'http://localhost:3001'
                link = f'{base_url}/redefinir-senha/{uid}/{token}/'

                EmailService.send_password_reset(user, f'{uid}/{token}', base_url)
            except User.DoesNotExist:
                pass
        messages.success(request, 'Se o e-mail informado estiver cadastrado e ativo, você receberá as instruções para redefinir sua senha.')
        return redirect('accounts:login')

    return render(request, 'accounts/password_reset.html')


def password_reset_confirm_view(request, uidb64, token):
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    from django.utils.encoding import force_str

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (ValueError, User.DoesNotExist):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return render(request, 'accounts/password_reset_invalid.html')

    if request.method == 'POST':
        form = FirstAccessForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Senha redefinida com sucesso! Faça seu login.')
            return redirect('accounts:login')
    else:
        form = FirstAccessForm()

    return render(request, 'accounts/password_reset_confirm.html', {'form': form})


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Senha alterada com sucesso.')
            return redirect('core:dashboard')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def user_list_view(request):
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def user_create_view(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = form.cleaned_data.get('is_staff', False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            UserProfileService.create_profile(user, created_by_admin=True)
            UserProfileService.complete_first_access(user)
            AuditService.log_user_created(user, request.user, request)

            if form.cleaned_data.get('send_credentials'):
                try:
                    EmailService.send_welcome_credentials(
                        user, form.cleaned_data['password']
                    )
                except Exception:
                    messages.warning(
                        request,
                        f'Usuário criado, mas não foi possível enviar o e-mail com as credenciais. '
                        f'As configurações de SMTP podem estar pendentes.'
                    )

            messages.success(request, f'Usuário {user.email} criado com sucesso.')
            return redirect('accounts:user_list')
    else:
        form = UserCreateForm()

    return render(request, 'accounts/user_form.html', {'form': form, 'is_create': True})


@login_required
@user_passes_test(is_admin)
def user_update_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = form.cleaned_data.get('is_staff', False)
            user.save()
            messages.success(request, f'Usuário {user.email} atualizado.')
            return redirect('accounts:user_list')
    else:
        form = UserUpdateForm(instance=user, initial={'is_staff': user.is_staff})

    return render(request, 'accounts/user_form.html', {'form': form, 'is_create': False, 'user_obj': user})


@login_required
@user_passes_test(is_admin)
def user_toggle_active_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        if not user.is_active:
            AuditService.log_user_deactivated(user, request.user, request)
            messages.warning(request, f'Usuário {user.email} inativado.')
        else:
            messages.success(request, f'Usuário {user.email} ativado.')
    return redirect('accounts:user_list')


@login_required
@user_passes_test(is_admin)
def resend_invitation_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        invitation = InvitationService.create_invitation(user, request.user)
        settings = SystemSettingsService.get_settings()
        base_url = settings.app_base_url if settings and settings.app_base_url else request.build_absolute_uri('/')[:-1]
        EmailService.send_invitation(user, invitation, base_url)
        messages.success(request, f'Convite reenviado para {user.email}.')
    return redirect('accounts:user_list')


@login_required
@user_passes_test(is_admin)
def resend_credentials_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        import secrets
        import string
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        user.set_password(new_password)
        user.save()
        try:
            EmailService.send_welcome_credentials(user, new_password)
            messages.success(request, f'Credenciais reenviadas para {user.email}.')
        except Exception:
            messages.warning(
                request,
                f'Senha alterada, mas falha ao enviar e-mail para {user.email}. '
                f'As configurações de SMTP podem estar pendentes.'
            )
    return redirect('accounts:user_list')


@login_required
@user_passes_test(is_admin)
def user_delete_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        if request.user == user:
            messages.error(request, 'Você não pode excluir seu próprio usuário.')
            return redirect('accounts:user_list')

        active_reservations = Reservation.objects.filter(user=user, status='active')
        if active_reservations.exists():
            messages.error(
                request,
                f'Não é possível excluir {user.email}. O usuário possui '
                f'{active_reservations.count()} reserva(s) ativa(s). '
                f'Cancele as reservas antes de excluir.'
            )
            return redirect('accounts:user_list')

        AuditService.log_user_deleted(user, request.user, request)
        user.delete()
        messages.success(request, f'Usuário {user.email} excluído permanentemente.')
        return redirect('accounts:user_list')

    active_count = Reservation.objects.filter(user=user, status='active').count()
    total_reservations = Reservation.objects.filter(user=user).count()
    return render(request, 'accounts/user_confirm_delete.html', {
        'user_obj': user,
        'active_count': active_count,
        'total_reservations': total_reservations,
    })
