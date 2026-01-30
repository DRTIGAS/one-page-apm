import os
import smtplib
import socket
from email.message import EmailMessage
import logging
from threading import Thread

from dotenv import load_dotenv
from flask import Flask, request, redirect, abort


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


def _smtp_send(msg: EmailMessage) -> None:
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
                return
            except Exception as e:
                logger.exception("Falha ao enviar e-mail sem endereços resolvidos: %s", e)
                return

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
                return
            except Exception as e:
                last_exc = e
                logger.warning("Falha conexão SMTP em %s: %s", host_to_connect, e)

        # if we reach here, all attempts failed
        logger.exception("Falha ao enviar e-mail após tentar todos os endereços: %s", last_exc)
    except Exception as e:
        logger.exception("Erro inesperado no envio SMTP: %s", e)


def send_contact_email(nome: str, contato: str, tipo_projeto: str, mensagem: str) -> None:
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
        Thread(target=_smtp_send, args=(msg,), daemon=True).start()
    else:
        # synchronous, will raise on failure
        _smtp_send(msg)


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
    except Exception:
        # Em produção, logar o erro; por enquanto só retorna 500 genérico
        abort(500, "Erro ao enviar e-mail")

    return redirect("/?contato=ok")


@app.get("/health")
def health() -> str:
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
