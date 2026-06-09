import time

import pandas as pd
import requests


URL = "https://store.steampowered.com/appreviews/730"
COLUMNS = ["review_id", "texto", "recomendado", "horas_jogadas", "votos_uteis", "data_criacao"]


def _buscar_com_tentativas(params, tentativas=3):
    for tentativa in range(1, tentativas + 1):
        try:
            resposta = requests.get(URL, params=params, timeout=20)
            resposta.raise_for_status()
            return resposta.json()
        except requests.RequestException:
            if tentativa == tentativas:
                raise
            time.sleep(2 * tentativa)


def coletar_reviews(total=600, idioma="brazilian"):
    """Coleta avaliacoes publicas do Counter-Strike 2 na Steam."""
    reviews = []
    cursor = "*"

    while len(reviews) < total:
        params = {
            "json": 1,
            "filter": "recent",
            "language": idioma,
            "purchase_type": "all",
            "num_per_page": 100,
            "cursor": cursor,
        }

        dados = _buscar_com_tentativas(params)

        lote = dados.get("reviews", [])
        if not lote:
            break

        for item in lote:
            reviews.append(
                {
                    "review_id": item.get("recommendationid"),
                    "texto": item.get("review", ""),
                    "recomendado": item.get("voted_up"),
                    "horas_jogadas": item.get("author", {}).get("playtime_forever", 0) / 60,
                    "votos_uteis": item.get("votes_up", 0),
                    "data_criacao": item.get("timestamp_created"),
                }
            )

        cursor = dados.get("cursor", cursor)
        time.sleep(0.5)

    if not reviews:
        return pd.DataFrame(columns=COLUMNS)

    return pd.DataFrame(reviews, columns=COLUMNS).drop_duplicates("review_id").head(total)
