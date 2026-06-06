"""
scraper.py
----------
Faz scraping do blog200porcento.com para extrair as promoções
do Pingo Doce, Continente, Lidl e Intermarché.
Filtra apenas folhetos válidos na data atual.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

LOJAS = {
    "Pingo Doce": "https://blog200porcento.com/tag/pingo+doce",
    "Continente": "https://blog200porcento.com/tag/continente",
    "Lidl": "https://blog200porcento.com/tag/lidl",
    "Intermarche": "https://blog200porcento.com/tag/intermarch%C3%A9",
}

# meses em português para converter datas
MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12
}


def extrair_data_validade(soup) -> datetime | None:
    """
    Tenta extrair a data de validade do folheto a partir do título ou conteúdo.
    Ex: "promoções de 2 a 8 junho" → datetime(2026, 6, 8)
    Ex: "promoções até 8 junho" → datetime(2026, 6, 8)
    """
    # tenta encontrar a data no título da página
    titulo = soup.find("h1")
    texto = titulo.get_text(strip=True).lower() if titulo else ""

    hoje = datetime.now()
    ano = hoje.year

    # padrão "de X a Y mês" ou "até Y mês"
    padroes = [
        r"de\s+\d+\s+a\s+(\d+)\s+de\s+(\w+)",
        r"de\s+\d+\s+a\s+(\d+)\s+(\w+)",
        r"at[eé]\s+(\d+)\s+de\s+(\w+)",
        r"at[eé]\s+(\d+)\s+(\w+)",
        r"(\d+)\s+a\s+(\d+)\s+(\w+)",
    ]

    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            grupos = match.groups()
            try:
                if len(grupos) == 2:
                    dia = int(grupos[0])
                    mes_str = grupos[1].lower()
                    mes = MESES.get(mes_str)
                    if mes:
                        return datetime(ano, mes, dia)
                elif len(grupos) == 3:
                    dia = int(grupos[1])
                    mes_str = grupos[2].lower()
                    mes = MESES.get(mes_str)
                    if mes:
                        return datetime(ano, mes, dia)
            except:
                continue

    return None


def folheto_valido(soup) -> bool:
    """
    Verifica se o folheto ainda está dentro da data de validade.
    Se não conseguir extrair a data, inclui o folheto por precaução.
    """
    data_fim = extrair_data_validade(soup)

    if data_fim is None:
        return True  # sem data, inclui por precaução

    hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return data_fim >= hoje


def obter_links_folhetos(loja: str, url: str) -> list[str]:
    """
    Obtém os links dos folhetos mais recentes de uma loja.
    """
    try:
        resposta = requests.get(url, headers=HEADERS, timeout=10)
        if resposta.status_code != 200:
            print(f"⚠️  Erro ao aceder a {loja}: {resposta.status_code}")
            return []

        soup = BeautifulSoup(resposta.content, "html.parser")

        links = []
        for artigo in soup.find_all("a", href=True):
            href = artigo["href"]
            if "blog200porcento.com" in href and "antevisao" in href.lower():
                if href not in links:
                    links.append(href)

        return links[:5]

    except Exception as erro:
        print(f"⚠️  Erro: {erro}")
        return []


def extrair_promocoes(url: str) -> tuple[str, list[str]]:
    """
    Extrai o título e os produtos de um artigo de folheto.
    Devolve (titulo, lista_de_promocoes).
    """
    try:
        resposta = requests.get(url, headers=HEADERS, timeout=10)
        if resposta.status_code != 200:
            return "", []

        soup = BeautifulSoup(resposta.content, "html.parser")

        if not folheto_valido(soup):
            print(f"   ⏰ Folheto expirado: {url}")
            return "", []

        # extrai o título do artigo como categoria
        h1 = soup.find("h1")
        titulo = h1.get_text(strip=True) if h1 else "Geral"

       
        # remove "Antevisão Folheto LOJA " do início — loja pode ter várias palavras
        titulo = re.sub(r"^Antevisão Folheto [A-ZÁÉÍÓÚÃÕÂÊÔÇÜ\s]+ ", "", titulo)
        titulo = re.sub(r" Promoções.*$", "", titulo)
        titulo = titulo.strip()
        if not titulo:
            titulo = "Geral"

        promocoes = []
        for li in soup.find_all("li"):
            texto = li.get_text(strip=True)
            if "€" in texto and len(texto) > 3:
                promocoes.append(texto)

        if not promocoes:
            for p in soup.find_all("p"):
                texto = p.get_text(strip=True)
                if "€" in texto and len(texto) > 3:
                    promocoes.append(texto)

        return titulo, promocoes

    except Exception as erro:
        print(f"⚠️  Erro: {erro}")
        return "", []


def recolher_promocoes() -> dict:
    """
    Recolhe todas as promoções de todas as lojas organizadas por categoria.
    Devolve: { "Pingo Doce": { "Frescos": [...], "Bazar": [...] }, ... }
    """
    todas = {}

    for loja, url in LOJAS.items():
        print(f"🔍 A recolher promoções: {loja}...")

        links = obter_links_folhetos(loja, url)
        categorias_loja = {}

        for link in links[:5]:
            titulo, promocoes = extrair_promocoes(link)
            if titulo and promocoes:
                categorias_loja[titulo] = promocoes

        todas[loja] = categorias_loja
        total = sum(len(v) for v in categorias_loja.values())
        print(f"   ✅ {total} promoções em {len(categorias_loja)} categorias")

    return todas


if __name__ == "__main__":
    resultado = recolher_promocoes()
    for loja, promocoes in resultado.items():
        print(f"\n=== {loja} ===")
        for p in promocoes[:10]:
            print(f"  • {p}")