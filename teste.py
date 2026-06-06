from scraper import recolher_promocoes
from filtrar import organizar_promocoes

promocoes = recolher_promocoes()
organizadas = organizar_promocoes(promocoes)

for loja, categorias in organizadas.items():
    print(f"\n=== {loja} ===")
    for categoria, produtos in categorias.items():
        print(f"  📦 {categoria} ({len(produtos)} produtos)")
        for p in produtos[:3]:
            print(f"    • {p}")