import os
import smtplib
import socket
from email.message import EmailMessage
import logging
from threading import Thread
import requests

from dotenv import load_dotenv
from flask import Flask, request, redirect, abort, jsonify


load_dotenv()


app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("apm-backend")


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
MAIL_TO = os.getenv("MAIL_TO", SMTP_USER)
# timeout for SMTP socket in seconds
SMTP_TIMEOUT = int(os.getenv("SMTP_TIMEOUT", "10"))
# send asynchronously by default to avoid blocking HTTP
SMTP_ASYNC = os.getenv("SMTP_ASYNC", "true").lower() in ("1", "true", "yes")
# SendGrid configuration
USE_SENDGRID = os.getenv("USE_SENDGRID", "false").lower() in ("1", "true", "yes")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM = os.getenv("SENDGRID_FROM")


def _smtp_send(msg: EmailMessage) -> bool:
    try:
        logger.info("Iniciando conexão SMTP %s:%s", SMTP_HOST, SMTP_PORT)
        # First try to get IPv4 A records via gethostbyname_ex (returns IPv4 list)
        try:
            ipv4_list = socket.gethostbyname_ex(SMTP_HOST)[2]
        except Exception:
            ipv4_list = []

        last_exc = None

        if ipv4_list:
            # build targets as IPv4 sockaddr tuples consistent with getaddrinfo format
            targets = [(socket.AF_INET, socket.SOCK_STREAM, 0, '', (ip, SMTP_PORT)) for ip in ipv4_list]
        else:
            # fallback to resolving any family (may yield IPv6 only)
            try:
                targets = socket.getaddrinfo(SMTP_HOST, SMTP_PORT, 0, socket.SOCK_STREAM)
            except socket.gaierror:
                targets = []

        if not targets:
            # fallback: try direct hostname (may raise)
            try:
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
                    server.starttls()
                    server.login(SMTP_USER, SMTP_PASSWORD)
                    server.send_message(msg)
                logger.info("E-mail enviado com sucesso para %s", MAIL_TO)
                return True
            except Exception as e:
                logger.exception("Falha ao enviar e-mail sem endereços resolvidos: %s", e)
                return False

        for family, socktype, proto, canonname, sockaddr in targets:
            host_to_connect = sockaddr[0]
            port = sockaddr[1]
            try:
                logger.info("Tentando conexão SMTP em %s (family=%s)", host_to_connect, family)
                with smtplib.SMTP(host_to_connect, port, timeout=SMTP_TIMEOUT) as server:
                    server.starttls()
                    server.login(SMTP_USER, SMTP_PASSWORD)
                    server.send_message(msg)
                logger.info("E-mail enviado com sucesso para %s via %s", MAIL_TO, host_to_connect)
                return True
            except Exception as e:
                last_exc = e
                logger.warning("Falha conexão SMTP em %s: %s", host_to_connect, e)

        # if we reach here, all attempts failed
        logger.exception("Falha ao enviar e-mail após tentar todos os endereços: %s", last_exc)
        return False
    except Exception as e:
        logger.exception("Erro inesperado no envio SMTP: %s", e)
        return False


def send_contact_email(nome: str, contato: str, tipo_projeto: str, mensagem: str) -> None:
    # Validate configuration depending on delivery method
    if USE_SENDGRID:
        if not SENDGRID_API_KEY or not SENDGRID_FROM or not MAIL_TO:
            raise RuntimeError("Configuração SendGrid ausente. Defina SENDGRID_API_KEY, SENDGRID_FROM e MAIL_TO.")
    else:
        if not SMTP_USER or not SMTP_PASSWORD or not MAIL_TO:
            raise RuntimeError("Configuração de SMTP ausente. Defina SMTP_USER, SMTP_PASSWORD e MAIL_TO.")

    body_lines = [
        f"Nome: {nome}",
        f"Contato: {contato}",
        f"Tipo de projeto: {tipo_projeto}",
        "",
        "Mensagem:",
        mensagem or "(sem mensagem)",
    ]

    msg = EmailMessage()
    msg["Subject"] = "Novo contato pelo site APM Arquitetura"
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg.set_content("\n".join(body_lines))

    if SMTP_ASYNC:
        logger.info("Enfileirando envio de e-mail em thread (assíncrono)")
        # If SendGrid is configured, prefer SendGrid for delivery
        if USE_SENDGRID and SENDGRID_API_KEY and SENDGRID_FROM:
            Thread(target=_send_via_sendgrid, args=(msg,), daemon=True).start()
        else:
            Thread(target=_smtp_send, args=(msg,), daemon=True).start()
    else:
        # synchronous, will raise on failure
        if USE_SENDGRID and SENDGRID_API_KEY and SENDGRID_FROM:
            _send_via_sendgrid(msg)
        else:
            _smtp_send(msg)


def _send_via_sendgrid(msg: EmailMessage) -> bool:
    try:
        logger.info("Enviando via SendGrid: %s -> %s", SENDGRID_FROM, MAIL_TO)
        if not SENDGRID_API_KEY or not SENDGRID_FROM:
            logger.warning("SendGrid não configurado corretamente")
            return False

        # Prefer using official SendGrid SDK if available
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail as SGMail
        except Exception:
            logger.warning("sendgrid package não encontrado, fazendo fallback para HTTP API via requests")
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {SENDGRID_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "personalizations": [{"to": [{"email": MAIL_TO}], "subject": msg["Subject"]}],
                "from": {"email": SENDGRID_FROM},
                "content": [{"type": "text/plain", "value": msg.get_content()}],
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=10)
            if resp.status_code >= 400:
                logger.error("SendGrid error %s: %s", resp.status_code, resp.text)
                return False
            logger.info("SendGrid accepted message (status %s)", resp.status_code)
            return True

        message = SGMail(from_email=SENDGRID_FROM, to_emails=MAIL_TO, subject=msg["Subject"], plain_text_content=msg.get_content())
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        resp = sg.send(message)
        status = getattr(resp, "status_code", None)
        if status is None:
            logger.warning("Resposta SendGrid inesperada: %s", resp)
            return False
        if status >= 400:
            body = getattr(resp, "body", None)
            logger.error("SendGrid error %s: %s", status, body)
            return False
        logger.info("SendGrid accepted message (status %s)", status)
        return True
    except Exception as e:
        logger.exception("Falha ao enviar via SendGrid: %s", e)
        return False


@app.post("/contato")
def contato() -> str:
    nome = request.form.get("nome", "").strip()
    contato_campo = request.form.get("contato", "").strip()
    tipo_projeto = request.form.get("tipoProjeto", "").strip()
    mensagem = request.form.get("mensagem", "").strip()

    if not nome or not contato_campo or not tipo_projeto:
        abort(400, "Campos obrigatórios ausentes")

    try:
        send_contact_email(nome, contato_campo, tipo_projeto, mensagem)
    except Exception as e:
        logger.exception("Erro ao processar /contato: %s", e)
        abort(500, "Erro ao enviar e-mail")

    return redirect("/?contato=ok")



@app.get("/debug/validate-smtp")
def debug_validate_smtp():
    try:
        if not SMTP_USER or not SMTP_PASSWORD:
            return jsonify({"ok": False, "error": "SMTP_USER or SMTP_PASSWORD not set"}), 400
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
        return jsonify({"ok": True, "msg": f"Conectado e autenticado em {SMTP_HOST}:{SMTP_PORT}"})
    except Exception as e:
        logger.exception("Validação SMTP falhou: %s", e)
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/debug/validate-sendgrid")
def debug_validate_sendgrid():
    try:
        if not SENDGRID_API_KEY:
            return jsonify({"ok": False, "error": "SENDGRID_API_KEY not set"}), 400
        url = "https://api.sendgrid.com/v3/user/account"
        headers = {"Authorization": f"Bearer {SENDGRID_API_KEY}"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return jsonify({"ok": True, "msg": "SendGrid API key appears valid"})
        return jsonify({"ok": False, "status": resp.status_code, "text": resp.text}), 500
    except Exception as e:
        logger.exception("Validação SendGrid falhou: %s", e)
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/debug/send-test-email")
def debug_send_test_email():
    async_param = request.args.get("async", "false").lower() in ("1", "true", "yes")
    subject = "[APM] Teste de envio de e-mail"
    content = "Este é um e-mail de teste gerado pelo endpoint /debug/send-test-email"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SENDGRID_FROM if USE_SENDGRID and SENDGRID_FROM else SMTP_USER
    msg["To"] = MAIL_TO
    msg.set_content(content)

    try:
        if async_param:
            if USE_SENDGRID and SENDGRID_API_KEY and SENDGRID_FROM:
                Thread(target=_send_via_sendgrid, args=(msg,), daemon=True).start()
            else:
                Thread(target=_smtp_send, args=(msg,), daemon=True).start()
            return jsonify({"ok": True, "async": True, "msg": "Enviado em background"})
        else:
            if USE_SENDGRID and SENDGRID_API_KEY and SENDGRID_FROM:
                ok = _send_via_sendgrid(msg)
            else:
                ok = _smtp_send(msg)
            if ok:
                return jsonify({"ok": True, "async": False, "msg": "E-mail enviado com sucesso"})
            else:
                return jsonify({"ok": False, "async": False, "msg": "Falha no envio"}), 500
    except Exception as e:
        logger.exception("Erro em /debug/send-test-email: %s", e)
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/health")
def health() -> str:
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
