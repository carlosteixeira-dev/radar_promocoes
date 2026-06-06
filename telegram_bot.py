"""
telegram_bot.py
---------------
Envia o resumo das promoções para o Telegram.
"""

import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def enviar_mensagem(texto: str) -> bool:
    """
    Envia uma mensagem para o Telegram.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Token ou Chat ID não definidos!")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        resposta = requests.post(url, data=payload, timeout=10)
        if resposta.status_code == 200:
            print("✅ Mensagem enviada!")
            return True
        else:
            print(f"❌ Erro: {resposta.status_code} - {resposta.text}")
            return False
    except Exception as erro:
        print(f"❌ Erro de ligação: {erro}")
        return False


def formatar_promocoes(promocoes: dict) -> list[str]:
    """
    Formata as promoções em mensagens para o Telegram.
    Uma mensagem por loja para não ultrapassar o limite.
    """
    hoje = datetime.now().strftime("%d/%m/%Y")
    mensagens = []

    # cabeçalho separado
    mensagens.append(f"🛒 <b>PROMOÇÕES DO DIA — {hoje}</b>\n━━━━━━━━━━━━━━━━━━━━━━")

    for loja, categorias in promocoes.items():
        if not categorias:
            continue

        mensagem_loja = f"🏪 <b>{loja}</b>\n"

        for categoria, lista in categorias.items():
            if not lista:
                continue
            mensagem_loja += f"\n📦 <b>{categoria}</b>\n"
            for p in lista[:10]:  # máximo 10 produtos por categoria
                mensagem_loja += f"• {p}\n"

        mensagens.append(mensagem_loja)

    return mensagens


def enviar_promocoes(promocoes: dict) -> None:
    """
    Formata e envia todas as promoções para o Telegram.
    """
    mensagens = formatar_promocoes(promocoes)

    for i, mensagem in enumerate(mensagens):
        print(f"\n--- MENSAGEM {i+1} ---")
        print(mensagem)
        enviar_mensagem(mensagem)


if __name__ == "__main__":
    from scraper import recolher_promocoes
    from filtrar import organizar_promocoes

    promocoes = recolher_promocoes()
    organizadas = organizar_promocoes(promocoes)
    enviar_promocoes(organizadas)