from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.shortcuts import render, redirect
from audit.services import AuditService
from notifications.services import EmailService
from .forms import SystemSettingsForm, SmtpTestForm
from .services import SystemSettingsService


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def system_settings_view(request):
    settings_obj = SystemSettingsService.get_settings()

    if request.method == 'POST':
        form = SystemSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            AuditService.log_visual_changed(request.user, request)
            messages.success(request, 'Configurações salvas com sucesso.')
            return redirect('system_settings:settings')
    else:
        initial = {}
        if settings_obj:
            initial = {
                'smtp_password': '',
            }
        form = SystemSettingsForm(instance=settings_obj, initial=initial)

    return render(request, 'system_settings/settings.html', {
        'form': form,
        'settings_obj': settings_obj,
    })


@login_required
@user_passes_test(is_admin)
def smtp_test_view(request):
    if request.method == 'POST':
        form = SmtpTestForm(request.POST)
        if form.is_valid():
            to_email = form.cleaned_data['to_email']
            config = SystemSettingsService.get_settings()
            log = EmailService.send_test_email(to_email, config)
            if log.status == 'sent':
                messages.success(request, f'E-mail de teste enviado para {to_email}.')
            else:
                messages.error(request, f'Falha ao enviar e-mail de teste: {log.error_message}')
            return redirect('system_settings:settings')
    return redirect('system_settings:settings')


@login_required
@user_passes_test(is_admin)
def smtp_test_config_view(request):
    if request.method != 'POST':
        return redirect('system_settings:settings')

    host = request.POST.get('smtp_host', '')
    port_str = request.POST.get('smtp_port', '587')
    username = request.POST.get('smtp_username', '')
    password = request.POST.get('smtp_password', '')
    use_tls_raw = request.POST.get('smtp_use_tls', '') == 'on'
    to_email = request.POST.get('smtp_test_to_email', '')

    try:
        port = int(port_str)
    except (ValueError, TypeError):
        port = 587

    if use_tls_raw:
        if port == 465:
            use_tls, use_ssl = False, True
        else:
            use_tls, use_ssl = True, False
    else:
        use_tls, use_ssl = False, False

    if not host:
        return HttpResponse('<div class="alert alert-danger py-1 small mb-0">Host SMTP é obrigatório.</div>')
    if not to_email:
        return HttpResponse('<div class="alert alert-danger py-1 small mb-0">Informe um e-mail de destino para o teste.</div>')

    try:
        from django.core.mail.backends.smtp import EmailBackend
        backend = EmailBackend(
            host=host, port=port, username=username, password=password,
            use_tls=use_tls, use_ssl=use_ssl, fail_silently=False,
        )
        backend.open()
        backend.close()

        from django.core.mail import EmailMessage
        sender_name = request.POST.get('email_sender_name', '')
        sender_address = request.POST.get('email_sender_address', '') or settings.DEFAULT_FROM_EMAIL
        from_header = f'{sender_name} <{sender_address}>' if sender_name else sender_address

        msg = EmailMessage(
            subject='Teste de configuração SMTP',
            body=f'Teste enviado com sucesso!\n\nHost: {host}\nPorta: {port}',
            from_email=from_header,
            to=[to_email],
            connection=backend,
        )
        msg.send()

        html = '<div class="alert alert-success py-1 small mb-0"><i class="bi bi-check-circle"></i> Teste OK! E-mail enviado com sucesso.</div>'
    except Exception as e:
        html = f'<div class="alert alert-danger py-1 small mb-0"><i class="bi bi-x-circle"></i> Falha: {str(e)[:300]}</div>'

    return HttpResponse(html)
