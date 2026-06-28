import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import HDBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score


MODEL_NAME = "sentence-transformers/all-MiniLM-L12-v2"
N_CLUSTERS = 5


def _calcular_silhouette(embeddings, labels, ignorar_ruido=False):
    labels_serie = pd.Series(labels)

    if ignorar_ruido:
        mascara = labels_serie != -1
        labels_serie = labels_serie[mascara]
        embeddings = embeddings[mascara.to_numpy()]

    if labels_serie.nunique() < 2 or len(labels_serie) <= labels_serie.nunique():
        return None

    return round(float(silhouette_score(embeddings, labels_serie)), 4)


def _resumo_clusters(labels):
    labels_serie = pd.Series(labels)
    return {
        int(label): int(qtd)
        for label, qtd in labels_serie.value_counts().sort_index().items()
    }


def _reduzir_embeddings_para_2d(embeddings):
    if len(embeddings) < 2:
        return [[0.0, 0.0] for _ in range(len(embeddings))]

    coordenadas = PCA(n_components=2, random_state=42).fit_transform(embeddings)
    return coordenadas.round(6).tolist()


def treinar_modelos(dados: pd.DataFrame) -> dict:
    coluna_texto = "texto_modelo" if "texto_modelo" in dados.columns else "texto"
    textos = dados[coluna_texto].fillna("").astype(str).tolist()
    n_clusters = min(N_CLUSTERS, len(textos))

    print("   Gerando embeddings com sentence-transformers...")
    modelo_emb = SentenceTransformer(MODEL_NAME)
    embeddings = modelo_emb.encode(textos, show_progress_bar=True, batch_size=32)

    print("   Clusterizando com KMeans...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    clusters_kmeans = kmeans.fit_predict(embeddings)
    dados["cluster_kmeans"] = clusters_kmeans

    dados["cluster_kmeans"].to_csv("clusters_output_KMEANS.csv", index=False)

    print("   Clusterizando com HDBSCAN...")
    if len(textos) < 5:
        clusters_hdbscan = np.full(len(textos), -1)
    else:
        min_cluster_size = max(5, min(25, len(textos) // 20))
        hdbscan = HDBSCAN(min_cluster_size=min_cluster_size)
        clusters_hdbscan = hdbscan.fit_predict(embeddings)
    dados["cluster_hdbscan"] = clusters_hdbscan

    dados["cluster_hdbscan"].to_csv("cluster_output_DB.csv")

    n_positivas = dados["recomendado"].sum()
    n_negativas = (~dados["recomendado"]).sum()
    coordenadas_2d = _reduzir_embeddings_para_2d(embeddings)
    silhouette_kmeans = _calcular_silhouette(embeddings, clusters_kmeans)
    silhouette_hdbscan = _calcular_silhouette(
        embeddings,
        clusters_hdbscan,
        ignorar_ruido=True,
    )

    return {
        "embedding_model": MODEL_NAME,
        "coordenadas_2d": coordenadas_2d,
        "modelos": {
            "kmeans": {
                "clusters": clusters_kmeans.tolist(),
                "quantidade_clusters": int(pd.Series(clusters_kmeans).nunique()),
                "distribuicao_clusters": _resumo_clusters(clusters_kmeans),
                "silhouette": silhouette_kmeans,
            },
            "hdbscan": {
                "clusters": clusters_hdbscan.tolist(),
                "quantidade_clusters": int(pd.Series(clusters_hdbscan)[pd.Series(clusters_hdbscan) != -1].nunique()),
                "distribuicao_clusters": _resumo_clusters(clusters_hdbscan),
                "percentual_ruido": round(float((clusters_hdbscan == -1).mean() * 100), 1),
                "silhouette": silhouette_hdbscan,
                "silhouette_sem_ruido": silhouette_hdbscan,
            },
        },
        "comparacao_silhouette": {
            "kmeans": silhouette_kmeans,
            "hdbscan": silhouette_hdbscan,
            "observacao": (
                "No HDBSCAN, o silhouette e calculado sem os pontos de ruido (-1), "
                "pois eles nao representam clusters."
            ),
        },
        "comparacao_clusterizacao": (
            "KMeans forca todas as avaliacoes em grupos predefinidos; HDBSCAN encontra "
            "grupos por densidade e pode marcar avaliacoes atipicas como ruido (-1)."
        ),
        "sentimento": {
            "positivas": int(n_positivas),
            "negativas": int(n_negativas),
            "percentual_positivo": round(n_positivas / len(dados) * 100, 1),
        },
    }
