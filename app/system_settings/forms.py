from django import forms
from .models import SystemSettings
from .services import SystemSettingsService


class SystemSettingsForm(forms.ModelForm):
    smtp_password = forms.CharField(
        label='Senha SMTP', required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        help_text='Deixe em branco para manter a senha atual.'
    )

    class Meta:
        model = SystemSettings
        fields = [
            'app_name', 'app_base_url',
            'logo', 'favicon', 'login_image',
            'primary_color', 'secondary_color', 'background_color',
            'navbar_bg_color', 'navbar_text_color',
            'welcome_text', 'organization_name', 'support_email',
            'email_sender_name', 'email_sender_address', 'email_reply_to',
            'smtp_host', 'smtp_port', 'smtp_username',
            'smtp_use_tls', 'email_settings_active',
            'send_confirmation_email', 'send_cancellation_email',
            'show_app_name_navbar', 'show_app_name_login', 'show_app_name_footer',
        ]
        widgets = {
            'app_name': forms.TextInput(attrs={'class': 'form-control'}),
            'app_base_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://exemplo.com'}),
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/png,image/jpeg,image/svg+xml'}),
            'favicon': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/png,image/x-icon,image/svg+xml'}),
            'login_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/png,image/jpeg,image/svg+xml'}),
            'primary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'background_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'navbar_bg_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'navbar_text_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'organization_name': forms.TextInput(attrs={'class': 'form-control'}),
            'welcome_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'support_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'email_sender_name': forms.TextInput(attrs={'class': 'form-control'}),
            'show_app_name_navbar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_app_name_login': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_app_name_footer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_sender_address': forms.EmailInput(attrs={'class': 'form-control'}),
            'email_reply_to': forms.EmailInput(attrs={'class': 'form-control'}),
            'smtp_host': forms.TextInput(attrs={'class': 'form-control'}),
            'smtp_port': forms.NumberInput(attrs={'class': 'form-control'}),
            'smtp_username': forms.TextInput(attrs={'class': 'form-control'}),
            'smtp_use_tls': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_settings_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_confirmation_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_cancellation_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'app_name': 'Nome da aplicação',
            'app_base_url': 'URL base',
            'logo': 'Logo',
            'favicon': 'Favicon',
            'login_image': 'Imagem de fundo da tela de login',
            'primary_color': 'Cor primária',
            'secondary_color': 'Cor secundária',
            'background_color': 'Cor de fundo',
            'navbar_bg_color': 'Cor da barra de navegação',
            'navbar_text_color': 'Cor do texto da barra de navegação',
            'organization_name': 'Nome da organização',
            'welcome_text': 'Texto de boas-vindas',
            'support_email': 'E-mail de suporte',
            'show_app_name_navbar': 'Exibir nome na barra de navegação',
            'show_app_name_login': 'Exibir nome na tela de login',
            'show_app_name_footer': 'Exibir nome no rodapé',
            'email_sender_name': 'Nome do remetente',
            'email_sender_address': 'E-mail remetente',
            'email_reply_to': 'E-mail de resposta',
            'smtp_host': 'Host SMTP',
            'smtp_port': 'Porta SMTP',
            'smtp_username': 'Usuário SMTP',
            'smtp_use_tls': 'Usar TLS/SSL',
            'email_settings_active': 'Configuração ativa',
            'send_confirmation_email': 'Enviar e-mail ao confirmar reserva',
            'send_cancellation_email': 'Enviar e-mail ao cancelar reserva',
        }

    def clean(self):
        cleaned_data = super().clean()
        port = cleaned_data.get('smtp_port', 587)

        if cleaned_data.get('smtp_use_tls'):
            if port == 465:
                cleaned_data['smtp_use_tls'] = False
        else:
            if 'smtp_use_tls' not in self.data:
                cleaned_data.pop('smtp_use_tls', None)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        raw_password = self.cleaned_data.get('smtp_password')
        if raw_password:
            instance.set_smtp_password(raw_password)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class SmtpTestForm(forms.Form):
    to_email = forms.EmailField(
        label='E-mail destinatário',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'teste@exemplo.com'})
    )
