# README.md
# Agendador Pro Público

MVP para agendamento de visto de Angola para Portugal com:
- link de gravação biométrica para outro telemóvel
- upload do vídeo do requerente
- automação Playwright para tentar preencher o formulário da VFS Global
- bloqueio seguro quando houver CAPTCHA/login manual

## Estrutura

- `app.py` — Flask API
- `static/record.html` — página WebRTC para gravação do vídeo no telemóvel
- `automation/scheduler.py` — script de automação Playwright para tentar agendar e preencher formulários
- `.env.example` — variáveis de ambiente

## Requisitos

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

## Configuração

Cria um ficheiro `.env` a partir do `.env.example` e preenche os valores.

```bash
cp .env.example .env
```

## Executar

```bash
source .venv/bin/activate
python app.py
```

A API fica em `http://localhost:5000`

### Endpoints principais

- `POST /send_record_link` — gera token e envia link para outro telemóvel
- `GET /record?token=...` — página de gravação biométrica
- `POST /upload_video` — upload do vídeo gravado
- `POST /schedule` — inicia rotina de agendamento em background

## Importante

A VFS Global exige login e CAPTCHA. Este MVP foi desenhado para:
1. tentar automatizar
2. detectar bloqueios
3. parar e pedir intervenção humana
4. continuar quando o operador resolve a verificação

Não é permitido contornar CAPTCHA, autenticação 2FA ou mecanismos anti-bot.

