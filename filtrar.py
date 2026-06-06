"""
filtrar.py
----------
Limpa e organiza as promoções recolhidas pelo scraper.
"""

LIXO = [
    "oferta entrega",
    "continente até dia",
    "comentar",
    "seja o primeiro",
    "sem comentários",
    "deixar um comentário",
    "posts relacionados",
    "publicações recentes",
]


def limpar_promocoes(promocoes: list[str]) -> list[str]:
    limpas = []
    for promocao in promocoes:
        texto = promocao.strip()
        if any(l in texto.lower() for l in LIXO):
            continue
        if len(texto) > 100:
            continue
        if texto not in limpas:
            limpas.append(texto)
    return limpas


def organizar_promocoes(todas: dict) -> dict:
    """
    Limpa as promoções mantendo a estrutura por categorias.
    Entrada:  { "Pingo Doce": { "Frescos": [...] }, ... }
    Saída:    { "Pingo Doce": { "Frescos": [...] }, ... }
    """
    organizadas = {}
    for loja, categorias in todas.items():
        organizadas[loja] = {}
        for categoria, promocoes in categorias.items():
            limpas = limpar_promocoes(promocoes)
            if limpas:
                organizadas[loja][categoria] = limpas
    return organizadas