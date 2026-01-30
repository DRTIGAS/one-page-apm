import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from flask import Flask, request, redirect, abort


load_dotenv()


app = Flask(__name__)


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
MAIL_TO = os.getenv("MAIL_TO", SMTP_USER)


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

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)


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
