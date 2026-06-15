import json, io, sys
from datetime import date, timedelta
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from accounts.forms import LoginForm, UserCreateForm, FirstAccessForm
from accounts.views import user_create_view, user_list_view, login_view
from accounts.services import InvitationService, UserProfileService
from booking.services import ReservationService, ReservationConflictError
from booking.models import Reservation
from rooms.models import Room, RoomPosition
from parking.models import ParkingSpot
from audit.services import AuditService
from system_settings.models import SystemSettings
from system_settings.forms import SystemSettingsForm
from audit.models import AuditLog

User = get_user_model()
rf = RequestFactory()
errors = []
ok = []

def add_session(request):
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()
    return request

def add_messages(request):
    setattr(request, '_messages', FallbackStorage(request))
    return request

# ====== 1. LOGIN ======
print('=== 1. LOGIN ===')
form = LoginForm(data={'email': 'admin@exemplo.com', 'password': 'admin123'})
if form.is_valid():
    ok.append('Login valida admin corretamente')
else:
    errors.append(f'Login invalid: {form.errors}')

form_bad = LoginForm(data={'email': 'admin@exemplo.com', 'password': 'wrong'})
if not form_bad.is_valid():
    ok.append('Login rejeita senha errada')
else:
    errors.append('Login aceitou senha errada')

form_inactive = LoginForm(data={'email': 'inexistente@test.com', 'password': 'x'})
if not form_inactive.is_valid():
    err_msg = str(form_inactive.errors)
    if 'inválidos' in err_msg:
        ok.append('Login msg genérica para e-mail inexistente')
    else:
        errors.append(f'Mensagem reveladora: {err_msg}')
else:
    errors.append('Login aceitou usuário inexistente')

# ====== 2. CRIAR USUÁRIO (o bug original) ======
print('=== 2. CRIAR USUÁRIO ===')
form_create = UserCreateForm(data={
    'first_name': 'Teste', 'last_name': 'Silva',
    'email': 'teste@test.com', 'is_active': True, 'is_staff': False,
})
if form_create.is_valid():
    request = rf.post('/usuarios/novo/', data=form_create.data)
    request.user = User.objects.get(email='admin@exemplo.com')
    add_session(request)
    add_messages(request)
    response = user_create_view(request)
    new_user = User.objects.filter(email='teste@test.com').first()
    if new_user:
        ok.append(f'Usuário criado: {new_user.email}, staff={new_user.is_staff}')
        if new_user.has_usable_password() == False:
            ok.append('Senha do novo usuário é inutilizável (correto)')
        else:
            errors.append('Senha do novo usuário está utilizável')
    else:
        errors.append('Usuário NÃO foi criado')
else:
    errors.append(f'UserCreateForm invalid: {form_create.errors}')

# ====== 3. CRIAR USUÁRIO ADMIN ======
print('=== 3. CRIAR USUÁRIO ADMIN ===')
form_admin = UserCreateForm(data={
    'first_name': 'Admin2', 'last_name': 'Sistema',
    'email': 'admin2@test.com', 'is_active': True, 'is_staff': True,
})
if form_admin.is_valid():
    request = rf.post('/usuarios/novo/', data=form_admin.data)
    request.user = User.objects.get(email='admin@exemplo.com')
    add_session(request)
    add_messages(request)
    user_create_view(request)
    admin2 = User.objects.filter(email='admin2@test.com').first()
    if admin2 and admin2.is_staff:
        ok.append('Usuário admin criado com is_staff=True')
    else:
        errors.append('Falha ao criar admin')
else:
    errors.append(f'Admin form invalid: {form_admin.errors}')

# ====== 4. LISTAR USUÁRIOS ======
print('=== 4. LISTAR USUÁRIOS ===')
request = rf.get('/usuarios/')
request.user = User.objects.get(email='admin@exemplo.com')
add_session(request)
response = user_list_view(request)
if response.status_code == 200:
    ok.append('Listagem de usuários retorna 200')
else:
    errors.append(f'Listagem retornou {response.status_code}')

# ====== 5. SALAS E POSIÇÕES ======
print('=== 5. SALAS E POSIÇÕES ===')
room = Room.objects.create(name='Sala 01', description='Sala principal')
pos_a = RoomPosition.objects.create(room=room, code='A1', description='Posição A1')
pos_b = RoomPosition.objects.create(room=room, code='A2', description='Posição A2')
ok.append(f'Sala e posições criadas: {room.name} ({pos_a.code}, {pos_b.code})')

# ====== 6. VAGAS DE ESTACIONAMENTO ======
print('=== 6. VAGAS DE ESTACIONAMENTO ===')
spot1 = ParkingSpot.objects.create(code='V01', type='common')
spot2 = ParkingSpot.objects.create(code='V02', type='accessible')
ok.append(f'Vagas criadas: {spot1.code}, {spot2.code}')

# ====== 7. RESERVAS ======
print('=== 7. RESERVAS ===')
user_teste = User.objects.get(email='teste@test.com')
tomorrow = date.today() + timedelta(days=1)
admin_user = User.objects.get(email='admin@exemplo.com')

res1 = ReservationService.create_reservation(
    user=user_teste, room_position=pos_a,
    reservation_date=tomorrow, period='morning',
)
ok.append(f'Reserva mínima criada: {res1.id}')

try:
    ReservationService.create_reservation(
        user=admin_user, room_position=pos_a,
        reservation_date=tomorrow, period='morning',
    )
    errors.append('Deveria ter lançado conflito para mesma posição')
except ReservationConflictError:
    ok.append('Conflito detectado para mesma posição')

res2 = ReservationService.create_reservation(
    user=admin_user, room_position=pos_a,
    reservation_date=tomorrow, period='afternoon',
)
ok.append('Período diferente na mesma posição permitido')

try:
    ReservationService.create_reservation(
        user=user_teste, room_position=pos_b,
        reservation_date=tomorrow, period='full_day',
    )
    try:
        ReservationService.create_reservation(
            user=admin_user, room_position=pos_b,
            reservation_date=tomorrow, period='morning',
        )
        errors.append('Full day deveria bloquear manhã')
    except ReservationConflictError:
        ok.append('Full day bloqueia manhã na mesma posição')
except ReservationConflictError:
    errors.append('Não conseguiu criar full day')

res_with_parking = ReservationService.create_reservation(
    user=user_teste, room_position=pos_b,
    reservation_date=tomorrow + timedelta(days=1),
    period='morning', parking_spot=spot1,
)
ok.append(f'Reserva com estacionamento criada: {res_with_parking.id}')

try:
    ReservationService.create_reservation(
        user=admin_user, room_position=pos_a,
        reservation_date=tomorrow + timedelta(days=1),
        period='morning', parking_spot=spot1,
    )
    errors.append('Deveria ter conflito de vaga')
except ReservationConflictError:
    ok.append('Conflito de vaga de estacionamento detectado')

ReservationService.cancel_reservation(res1, admin_user, 'Teste cancelamento')
res1.refresh_from_db()
if res1.status == 'cancelled':
    ok.append('Reserva cancelada com sucesso')
else:
    errors.append('Status não mudou para cancelled')

res_after_cancel = ReservationService.create_reservation(
    user=admin_user, room_position=pos_a,
    reservation_date=tomorrow, period='morning',
)
ok.append('Reserva cancelada não bloqueia nova reserva')

try:
    ReservationService.create_reservation(
        user=user_teste, room_position=pos_a,
        reservation_date=date(2020, 1, 1), period='morning',
    )
    errors.append('Data passada deveria ser rejeitada')
except ReservationConflictError:
    ok.append('Data passada rejeitada')

# ====== 8. SISTEMA DE CONVITE ======
print('=== 8. SISTEMA DE CONVITE ===')
inv = InvitationService.create_invitation(user_teste, admin_user)
if inv._plain_token:
    ok.append('Convite criado com token')
else:
    errors.append('Token não gerado')

validated = InvitationService.validate_token(inv._plain_token)
if validated:
    ok.append('Token válido validado')
else:
    errors.append('Token válido NÃO validado')

InvitationService.mark_as_used(inv)
used = InvitationService.validate_token(inv._plain_token)
if used is None:
    ok.append('Token usado não é mais válido')
else:
    errors.append('Token usado ainda é válido')

inv2 = InvitationService.create_invitation(user_teste, admin_user)
if inv2._plain_token:
    ok.append('Segundo convite criado')
    old_valid = InvitationService.validate_token(inv._plain_token)
    if old_valid is None:
        ok.append('Convite anterior invalidado')
    else:
        errors.append('Convite anterior ainda válido')

# ====== 9. PERFIL PRIMEIRO ACESSO ======
print('=== 9. PERFIL PRIMEIRO ACESSO ===')
up = UserProfileService.complete_first_access(user_teste)
if up.first_access_completed:
    ok.append('Primeiro acesso concluído')
else:
    errors.append('First access não marcado')

# ====== 10. SYSTEM SETTINGS ======
print('=== 10. SYSTEM SETTINGS ===')
ss = SystemSettingsService.get_settings()
if ss.app_name == 'Sistema de Reservas':
    ok.append('Settings default carregado')
else:
    errors.append(f'Settings com nome inesperado: {ss.app_name}')

form_ss = SystemSettingsForm(instance=ss, data={
    'app_name': 'Meu Sistema',
    'primary_color': '#ff0000',
    'secondary_color': '#00ff00',
    'smtp_host': 'smtp.test.com',
    'smtp_port': 587,
    'smtp_username': 'user@test.com',
    'smtp_use_tls': True,
    'smtp_use_ssl': False,
}, initial={'smtp_password': ''})
if form_ss.is_valid():
    form_ss.save()
    ss.refresh_from_db()
    if ss.app_name == 'Meu Sistema' and ss.primary_color == '#ff0000':
        ok.append('System settings salvos corretamente')
    else:
        errors.append(f'Settings não foram salvos: {ss.app_name}')
else:
    errors.append(f'SystemSettingsForm invalid: {form_ss.errors}')

form_ss_bad = SystemSettingsForm(instance=ss, data={
    'app_name': 'Teste',
    'smtp_use_tls': True,
    'smtp_use_ssl': True,
}, initial={'smtp_password': ''})
if form_ss_bad.is_valid():
    ss_bad = form_ss_bad.save()
    if ss_bad.smtp_use_tls and not ss_bad.smtp_use_ssl:
        ok.append('TLS/SSL mutual exclusion forçado (SSL desligado)')
    else:
        errors.append('Mutual exclusion falhou')
else:
    errors.append(f'TLS+SSL form invalid: {form_ss_bad.errors}')

# ====== 11. AUDITORIA ======
print('=== 11. AUDITORIA ===')
AuditService.log_user_created(user_teste, admin_user, None)
logs = AuditLog.objects.filter(user=user_teste)
if logs.exists():
    ok.append('Log de auditoria criado')
else:
    errors.append('Log de auditoria NÃO criado')

# ====== 12. RESULTADO ======
print()
print(f'✓ OK: {len(ok)}')
print(f'✗ ERROS: {len(errors)}')
for e in errors:
    print(f'  ✗ {e}')
