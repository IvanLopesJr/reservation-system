# Manual de Uso — Sistema de Reservas

## 1. Primeiros Passos

**Acessar o sistema:** abra o navegador (Chrome, Edge, Firefox) e digite o endereço fornecido pela sua equipe de TI.

**Fazer login:**
1. Digite seu **e-mail** (ex: `joao@empresa.com`)
2. Digite sua **senha**
3. Marque **"Lembre-me"** se quiser ficar logado por 14 dias (útil em computadores pessoais)
4. Clique em **"Entrar"**

---

## 2. Esqueci Minha Senha

1. Na tela de login, clique em **"Esqueceu a senha?"**
2. Digite seu e-mail e clique em **"Enviar"**
3. Verifique sua caixa de entrada — você receberá um e-mail com um link
4. Clique no link, digite a nova senha e confirme
5. Pronto! Volte para a tela de login e entre com a nova senha

> **Observação:** a mensagem de confirmação é propositalmente genérica por segurança. Se o e-mail não estiver cadastrado, você não receberá a mensagem.

---

## 3. Primeiro Acesso (Convite)

Se você recebeu um **convite por e-mail**:

1. Abra o e-mail e clique no link de convite
2. Crie uma senha (e confirme)
3. Pronto! Agora você pode fazer login normalmente

> O link do convite expira em **48 horas**. Se vencer, peça ao administrador para reenviar.

---

## 4. Para Usuários

### 4.1. Painel Inicial

Ao fazer login, você vê:

- **Mensagem de boas-vindas** com seu nome
- **Atalhos rápidos:** Nova reserva, Minhas reservas, Alterar senha
- **Cards de estatísticas:** quantas posições e vagas estão disponíveis hoje
- **"Disponibilidade hoje":** mostra, para cada período (Manhã, Tarde, Dia inteiro), quantas posições e vagas estão livres
- **"Reservas de hoje":** tabela com todas as reservas do dia
- **"Próximas reservas":** suas reservas futuras (com botão para cancelar)

### 4.2. Como Fazer uma Reserva

1. Clique em **"Reservar"** (atalho no painel) ou acesse **"Nova reserva"** no menu
2. **Escolha a sala** — clique na seta e selecione a desejada
3. **Escolha a data** — clique no campo e selecione no calendário
4. **Escolha o período:**
   - **Manhã** — ocupa a posição apenas pela manhã
   - **Tarde** — ocupa a posição apenas à tarde
   - **Dia inteiro** — ocupa a posição o dia todo
5. **Escolha a posição** — as posições disponíveis aparecem em **verde**. Clique em uma para selecionar (a borda muda para a **cor primária** do sistema). Posições ocupadas aparecem em **cinza** e não podem ser clicadas
6. **Opcional: vaga de estacionamento** — se houver vagas livres **e seu perfil tiver permissão para usar estacionamento**, aparecerá a opção **"Quero vaga de estacionamento"**. Marque a caixa e escolha a vaga desejada
7. Clique em **"Confirmar reserva"**

Pronto! Você receberá um e-mail de confirmação (se o administrador tiver configurado o envio).

> **Importante:** você só pode ter **uma reserva ativa por dia**. Se já tiver uma reserva na data escolhida, o sistema avisará.

### 4.3. Minhas Reservas

Acesse **"Minhas reservas"** no menu para ver a lista completa de todas as suas reservas.

- **Ícone de olho** — ver detalhes da reserva
- **Ícone de X vermelho** — cancelar a reserva (só aparece para reservas ativas)
- **Reservas passadas** aparecem como "Finalizada" ou "Cancelada"

### 4.4. Cancelar uma Reserva

1. Vá em **"Minhas reservas"**
2. Clique no **X vermelho** ao lado da reserva que deseja cancelar
3. Opcional: digite o motivo do cancelamento
4. Clique em **"Confirmar cancelamento"**

> A vaga e a posição são liberadas imediatamente para outro usuário reservar.

### 4.5. Alterar Senha

1. Clique no **seu nome** no canto superior direito
2. Selecione **"Alterar senha"**
3. Digite a **senha atual**, a **nova senha** e **confirme**
4. Clique em **"Alterar"**

---

## 5. Para Administradores

Além de todas as funções de usuário comum, o administrador tem acesso às telas descritas abaixo.

### 5.1. Painel Administrativo

Ao fazer login como administrador, você vê:

- **Cards com totais do dia:**
  - Reservas hoje
  - Usuários hoje (quantas pessoas diferentes reservaram)
  - Posições totais
  - Vagas totais
  - Posições ocupadas
  - Vagas ocupadas
- **"Disponibilidade hoje":** posições e vagas livres por período
- **"Reservas de hoje":** tabela completa com todas as reservas
- **"Últimas falhas de e-mail":** mostra os 5 e-mails mais recentes que não foram enviados

### 5.2. Gerenciar Usuários

Acesse **"Usuários"** no menu **Administrar**.

**Criar novo usuário:**
1. Clique em **"Novo usuário"**
2. Preencha: nome, sobrenome, e-mail, senha (ou clique em **"Gerar senha aleatória"**)
3. Opções:
   - **"Administrador"** — marque se a pessoa for administradora
   - **"Ativo"** — desmarque para criar como inativo
   - **"Pode usar estacionamento"** — desmarque para usuários que não podem reservar vagas
   - **"Enviar credenciais"** — marque para enviar e-mail com os dados de acesso
4. Clique em **"Salvar"**

**Editar usuário:** clique no **lápis** ao lado do usuário na lista. Você também pode alterar a permissão **"Pode usar estacionamento"**.

**Ativar/Desativar:** clique no **ícone de play/pause** para bloquear ou liberar o acesso.

**Reenviar convite:** para usuários que ainda **não completaram o primeiro acesso**. Um novo e-mail de convite será enviado.

**Reenviar credenciais:** para usuários que completaram o primeiro acesso mas **nunca fizeram login**. Uma nova senha será gerada e enviada por e-mail.

**Excluir usuário:** clique no **ícone de lixeira**. Só é permitido excluir se o usuário não tiver reservas ativas.

### 5.3. Gerenciar Salas e Posições

Acesse **"Salas"** no menu **Administrar**.

**Salas:**
- **Nova sala:** nome e descrição
- **Editar:** alterar dados (ícone ✏️)
- **Ativar/Desativar:** desativar uma sala a remove da lista de opções na hora de reservar (ícone ▶ / ⏸)
- **Excluir:** clique no **ícone 🗑️** para remover a sala permanentemente (só permitido se não houver reservas ativas)

**Posições (dentro de cada sala):**
- Clique no **ícone de grade** para ver as posições de uma sala
- **Nova posição:** código (ex: "A1", "B2"), descrição e status
- **Editar:** alterar dados (ícone ✏️)
- **Alternar status:** cada clique alterna entre: Disponível → Bloqueada → Inativa → Disponível (ícone 🔄)
- **Excluir:** clique no **ícone 🗑️** para remover a posição permanentemente (só permitido se não houver reservas ativas)

> Posições **Bloqueadas** ou **Inativas** não aparecem para reserva.

### 5.4. Gerenciar Vagas de Estacionamento

Acesse **"Vagas"** no menu **Administrar**.

- **Nova vaga:** código, tipo (Comum, Acessível, Visitante, Reservada), descrição e status
- **Editar:** alterar dados (ícone ✏️)
- **Alternar status:** Disponível → Bloqueada → Inativa → Disponível (ícone 🔄)
- **Excluir:** clique no **ícone 🗑️** para remover a vaga permanentemente (só permitido se não houver reservas ativas)

### 5.5. Gerenciar Reservas

Acesse **"Reservas"** no menu **Administrar**.

- Lista **completa** de todas as reservas do sistema
- Use os **filtros** para buscar por: data inicial, data final, e-mail do usuário, status
- **Exportar:** clique em **"Exportar CSV"** para baixar uma planilha com todas as reservas
- **Detalhes:** clique no olho para ver informações completas
- **Cancelar:** clique no X vermelho para cancelar qualquer reserva (informe o motivo)

### 5.6. Configurações do Sistema

Acesse **"Configurações"** no menu **Administrar**.

**Identidade Visual (lado esquerdo):**

| Campo | O que faz |
|-------|-----------|
| Nome da aplicação | Nome que aparece na barra e no rodapé |
| URL base | Endereço usado nos e-mails (links) |
| Texto de boas-vindas | Mensagem que aparece no painel do usuário |
| Nome da organização | Aparece no rodapé dos e-mails |
| Logotipo | Imagem da sua empresa (máx. 2MB) |
| Favicon | Ícone que aparece na aba do navegador |
| Imagem de login | Imagem de fundo da tela de entrada |
| Cores | Personalize as cores do sistema (primária, fundo, barra, etc.) |
| Visibilidade do nome | Escolha onde mostrar o nome: barra, tela de login, rodapé |
| Usar menu offcanvas no celular | Desmarque para usar o menu collapse padrão em vez do painel lateral |

**E-mail (lado direito):**

| Campo | O que faz |
|-------|-----------|
| E-mail de suporte | Endereço de contato |
| Configurações SMTP | Host, porta, usuário e senha do servidor de e-mail |
| Usar TLS/SSL | Marque para ativar segurança (sistema escolhe TLS ou SSL conforme a porta) |
| Ativar configuração | Marque para usar estas configurações |
| Enviar e-mail ao confirmar | Marque para enviar confirmação automática |
| Enviar e-mail ao cancelar | Marque para enviar aviso de cancelamento |

> **Testar configuração:** preencha os dados e clique em **"Testar configuração"** — um e-mail de teste será enviado sem precisar salvar antes.

### 5.7. Auditoria

Acesse **"Auditoria"** no menu **Administrar**.

Registro completo de todas as ações importantes feitas no sistema:

- Criação de usuários
- Ativação/desativação
- Exclusão de usuários
- Cancelamento de reservas
- Alterações de configuração

Para cada ação, você vê: **quem fez**, **o que fez**, **quando** e **de qual IP**.

---

## 6. Regras Importantes

- Cada usuário só pode ter **uma reserva ativa por dia**
- Reserva de **Manhã** conflita com: Manhã e Dia inteiro
- Reserva de **Tarde** conflita com: Tarde e Dia inteiro
- Reserva de **Dia inteiro** conflita com: Manhã, Tarde e Dia inteiro
- Não é possível reservar ou cancelar em **datas passadas**
- O link de convite expira em **48 horas**
- Falhas no envio de e-mail **não cancelam** a reserva — sua reserva fica garantida
- A senha do servidor de e-mail é armazenada de forma criptografada

---

## 7. Ícones e Atalhos

| Ícone | Significado |
|-------|-------------|
| 👁 | Ver detalhes |
| ✏️ | Editar |
| 🗑️ | Excluir permanentemente |
| ❌ | Cancelar reserva |
| ▶ / ⏸ | Ativar / Desativar |
| 🔄 | Alternar status |
| ⬇ | Baixar / Exportar |
| 🔗 | Ver posições da sala |
