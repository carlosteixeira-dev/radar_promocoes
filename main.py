"""
main.py
-------
Ponto de entrada do Radar de Promoções.
Orquestra o scraper, filtrar e telegram_bot.
"""

from scraper import recolher_promocoes
from filtrar import organizar_promocoes
from telegram_bot import enviar_promocoes


def main():
    print("🛒 Radar de Promoções — a iniciar...\n")

    # recolhe promoções
    promocoes = recolher_promocoes()

    # limpa e organiza
    organizadas = organizar_promocoes(promocoes)

    # envia para o Telegram
    enviar_promocoes(organizadas)

    print("\n🏁 Concluído!")


if __name__ == "__main__":
    main()