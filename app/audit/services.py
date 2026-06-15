from .models import AuditLog


class AuditService:

    @staticmethod
    def log(user, action, entity_type='', entity_id=None, description='', request=None):
        ip_address = None
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR')

        AuditLog.objects.create(
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address,
        )

    @staticmethod
    def log_user_created(user, created_by, request=None):
        AuditService.log(
            user=created_by,
            action='criar_usuario',
            entity_type='User',
            entity_id=user.id,
            description=f'Usuário {user.email} criado',
            request=request,
        )

    @staticmethod
    def log_user_deactivated(user, deactivated_by, request=None):
        AuditService.log(
            user=deactivated_by,
            action='inativar_usuario',
            entity_type='User',
            entity_id=user.id,
            description=f'Usuário {user.email} inativado',
            request=request,
        )

    @staticmethod
    def log_reservation_cancelled(reservation, cancelled_by, request=None):
        AuditService.log(
            user=cancelled_by,
            action='cancelar_reserva',
            entity_type='Reservation',
            entity_id=reservation.id,
            description=f'Reserva {reservation.id} cancelada - {reservation.room_position.code} em {reservation.reservation_date}',
            request=request,
        )

    @staticmethod
    def log_smtp_changed(user, request=None):
        AuditService.log(
            user=user,
            action='alterar_smtp',
            entity_type='SystemSettings',
            description='Configuração SMTP alterada',
            request=request,
        )

    @staticmethod
    def log_user_deleted(user, deleted_by, request=None):
        AuditService.log(
            user=deleted_by,
            action='excluir_usuario',
            entity_type='User',
            entity_id=user.id,
            description=f'Usuário {user.email} excluído',
            request=request,
        )

    @staticmethod
    def log_visual_changed(user, request=None):
        AuditService.log(
            user=user,
            action='alterar_visual',
            entity_type='SystemSettings',
            description='Identidade visual alterada',
            request=request,
        )
