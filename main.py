from pathlib import Path

import pandas as pd
import requests

from src.extracao import coletar_reviews
from src.llm_insights import gerar_insights
from src.modelagem import treinar_modelos
from src.preprocessamento import preparar_reviews



BASE_DIR = Path(__file__).parent
RAW_PATH = BASE_DIR / "data" / "raw" / "steam_cs2_reviews.csv"
PROCESSED_PATH = BASE_DIR / "data" / "processado" / "steam_cs2_reviews_processado.csv"
REPORT_PATH = BASE_DIR / "data" / "processado" / "relatorio_insights.txt"



def main():
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("1) Coletando avaliacoes da Steam...")
    try:
        reviews = coletar_reviews(total=1000)
    except requests.RequestException as erro:
        if not RAW_PATH.exists():
            raise

        print(f"   Steam indisponivel agora ({erro}). Usando CSV bruto ja salvo.")
        reviews = pd.read_csv(RAW_PATH)

    reviews.to_csv(RAW_PATH, index=False, encoding="utf-8")
    print(f"   {len(reviews)} avaliacoes salvas em {RAW_PATH}")

    print("2) Limpando e preparando textos...")
    dados = preparar_reviews(reviews)
    if dados.empty:
        raise RuntimeError(
            "Nenhuma avaliacao foi coletada. Verifique a conexao, a resposta da API "
            "ou tente mudar o idioma em coletar_reviews."
        )

    dados.to_csv(PROCESSED_PATH, index=False, encoding="utf-8")
    print(f"   Base processada salva em {PROCESSED_PATH}")

    print("3) Gerando TF-IDF, classificacao e agrupamento...")
    resultados = treinar_modelos(dados)

    print("4) Gerando insights estruturados...")
    insights = gerar_insights(dados, resultados)
    REPORT_PATH.write_text(insights.model_dump_json(indent=2), encoding="utf-8")

    print("\nResumo:")
    print(f"- Avaliacoes analisadas: {len(dados)}")
    print(f"- Acuracia: {resultados['acuracia']:.3f}")
    print(f"- Relatorio salvo em: {REPORT_PATH}")


if __name__ == "__main__":
    main()
