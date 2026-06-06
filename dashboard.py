"""
dashboard.py
------------
Dashboard gráfico para o Radar de Promoções.
Mostra as promoções do dia de todas as lojas.
"""

import customtkinter as ctk
import threading
from datetime import datetime

from scraper import recolher_promocoes
from filtrar import organizar_promocoes
from telegram_bot import enviar_promocoes

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("🛒 Radar de Promoções")
app.geometry("800x600")

# --- TÍTULO ---
titulo = ctk.CTkLabel(app, text="🛒 RADAR DE PROMOÇÕES", font=("Arial", 20, "bold"))
titulo.pack(pady=15)

# --- ESTADO ---
label_estado = ctk.CTkLabel(app, text="⏳ Pronto para pesquisar...", font=("Arial", 13))
label_estado.pack(pady=5)

# --- ÚLTIMA ATUALIZAÇÃO ---
label_atualizacao = ctk.CTkLabel(app, text="", font=("Arial", 11), text_color="gray")
label_atualizacao.pack(pady=2)

# --- CAIXA DE RESULTADOS ---
caixa = ctk.CTkTextbox(app, width=750, height=430, font=("Courier", 12))
caixa.pack(pady=10)

# --- BOTÃO ---
def pesquisar():
    botao.configure(state="disabled", text="⏳ A pesquisar...")
    label_estado.configure(text="🔍 A recolher promoções...", text_color="yellow")
    caixa.delete("1.0", "end")
    thread = threading.Thread(target=correr_pesquisa)
    thread.start()


def correr_pesquisa():
    promocoes = recolher_promocoes()
    organizadas = organizar_promocoes(promocoes)
    app.after(0, lambda: mostrar_resultados(organizadas))


def mostrar_resultados(organizadas):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    label_atualizacao.configure(text=f"Última atualização: {agora}")
    caixa.delete("1.0", "end")

    total = sum(
        len(lista)
        for categorias in organizadas.values()
        for lista in categorias.values()
    )

    if total == 0:
        caixa.insert("end", "😴 Nenhuma promoção encontrada hoje.\n")
        label_estado.configure(text="😴 Sem promoções hoje", text_color="gray")
    else:
        label_estado.configure(
            text=f"✅ {total} promoções encontradas!",
            text_color="green"
        )

        for loja, categorias in organizadas.items():
            if not categorias:
                continue
            total_loja = sum(len(lista) for lista in categorias.values())
            caixa.insert("end", f"\n🏪 {loja} ({total_loja} promoções)\n")
            caixa.insert("end", "═" * 50 + "\n")
            for categoria, lista in categorias.items():
                caixa.insert("end", f"\n  📦 {categoria}\n")
                caixa.insert("end", "  " + "─" * 40 + "\n")
                for p in lista:
                    caixa.insert("end", f"    • {p}\n")
            caixa.insert("end", "\n")

        enviar_promocoes(organizadas)

    botao.configure(state="normal", text="🔍 Pesquisar Promoções")


botao = ctk.CTkButton(
    app,
    text="🔍 Pesquisar Promoções",
    font=("Arial", 14, "bold"),
    height=45,
    command=pesquisar
)
botao.pack(pady=10)

if __name__ == "__main__":
    app.mainloop()