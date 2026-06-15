# Sistema de Reserva de Posições e Estacionamento

Aplicação web responsiva para reserva de posições em sala, com reserva opcional de vaga de estacionamento.

## Stack

- **Backend:** Django 5.2
- **Banco:** SQLite
- **Container:** Docker + Docker Compose
- **Frontend:** Django Templates + Bootstrap 5
- **Interações:** HTMX + Alpine.js
- **Estáticos:** WhiteNoise

## Requisitos

- Docker e Docker Compose (recomendado)
- Ou Python 3.12+ e pip

## Execução com Docker

```bash
cp .env.example .env
docker compose up --build
```

Acesse http://localhost:3001

## Execução sem Docker

```bash
cd app
pip install -r ../requirements.txt
cp ../.env.example ../.env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Credenciais padrão (desenvolvimento)

- **Admin:** admin@exemplo.com / admin123

## Estrutura do projeto

```
reservation-system/
├── app/                    # Código Django
│   ├── config/             # Configurações do projeto
│   ├── accounts/           # Autenticação, usuários, convites
│   ├── audit/              # Registro de auditoria
│   ├── booking/            # Reservas e validação de conflitos
│   ├── core/               # Dashboard, páginas de erro
│   ├── notifications/      # E-mails transacionais e EmailLog
│   ├── parking/            # Vagas de estacionamento
│   ├── rooms/              # Salas e posições
│   ├── system_settings/    # Configurações visuais e SMTP
│   ├── templates/          # Templates Django
│   ├── static/             # Arquivos estáticos
│   └── media/              # Uploads (logo, favicon)
├── data/                   # Banco SQLite (volume Docker)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Funcionalidades

- Autenticação por e-mail com primeiro acesso via convite
- Redefinição de senha
- Cadastro de usuários restrito a administradores
- Gerenciamento de salas, posições e vagas
- Reserva de posição com vaga opcional de estacionamento
- Validação de conflitos por período (manhã/tarde/dia inteiro)
- Cancelamento de reservas com liberação de recursos
- Configuração SMTP dinâmica via administração
- Personalização visual (logo, favicon, cores)
- Auditoria de ações administrativas
- Dashboard do usuário e administrativo
- Interface responsiva (desktop e mobile)

## Testes

```bash
cd app
pytest -v
```

## Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `DJANGO_SECRET_KEY` | Chave secreta Django |
| `DJANGO_DEBUG` | Modo debug (True/False) |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origens confiáveis CSRF |
| `SMTP_PASSWORD_KEY` | Chave Fernet para criptografia da senha SMTP |
