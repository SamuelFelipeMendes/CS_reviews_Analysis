from pathlib import Path

import pandas as pd
import requests

from src.extracao import coletar_reviews
from src.llm_insights import gerar_insights
from src.modelagem import treinar_modelos
from src.preprocessamento import preparar_reviews
from src.visualizacao import gerar_graficos_clusterizacao


BASE_DIR = Path(__file__).parent
RAW_PATH = BASE_DIR / "data" / "raw" / "steam_cs2_reviews.csv"
PROCESSED_PATH = BASE_DIR / "data" / "processado" / "steam_cs2_reviews_processado.csv"
REPORT_PATH = BASE_DIR / "data" / "processado" / "relatorio_insights.txt"
KMEANS_PLOT_PATH = BASE_DIR / "data" / "processado" / "grafico_kmeans.png"
HDBSCAN_PLOT_PATH = BASE_DIR / "data" / "processado" / "grafico_hdbscan.png"



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

    print("2) Validando textos e preparando metadados...")
    dados = preparar_reviews(reviews)
    if dados.empty:
        raise RuntimeError(
            "Nenhuma avaliacao foi coletada. Verifique a conexao, a resposta da API "
            "ou tente mudar o idioma em coletar_reviews."
        )

    print("3) Gerando Embedding e agrupamento...")
    resultados = treinar_modelos(dados)

    print("4) Gerando graficos de interpretacao dos clusters...")
    gerar_graficos_clusterizacao(resultados, KMEANS_PLOT_PATH, HDBSCAN_PLOT_PATH)

    dados.to_csv(PROCESSED_PATH, index=False, encoding="utf-8")
    print(f"   Base processada salva em {PROCESSED_PATH}")

    print("5) Gerando insights estruturados...")
    insights = gerar_insights(dados, resultados)
    REPORT_PATH.write_text(insights.model_dump_json(indent=2), encoding="utf-8")

    print("\nResumo:")
    print(f"- Avaliacoes analisadas: {len(dados)}")
    print(f"- Modelo de embeddings: {resultados['embedding_model']}")
    print(f"- Clusters KMeans: {resultados['modelos']['kmeans']['quantidade_clusters']}")
    print(f"- Silhouette KMeans: {resultados['modelos']['kmeans']['silhouette']}")
    print(f"- Clusters HDBSCAN: {resultados['modelos']['hdbscan']['quantidade_clusters']}")
    silhouette_hdbscan = resultados["modelos"]["hdbscan"].get(
        "silhouette",
        resultados["modelos"]["hdbscan"].get("silhouette_sem_ruido"),
    )
    print(f"- Silhouette HDBSCAN: {silhouette_hdbscan}")
    print(f"- Ruido HDBSCAN: {resultados['modelos']['hdbscan']['percentual_ruido']}%")
    print(f"- Grafico KMeans: {KMEANS_PLOT_PATH}")
    print(f"- Grafico HDBSCAN: {HDBSCAN_PLOT_PATH}")
    print(f"- Relatorio salvo em: {REPORT_PATH}")


if __name__ == "__main__":
    main()
