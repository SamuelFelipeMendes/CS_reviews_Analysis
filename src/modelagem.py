import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import HDBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score


MODEL_NAME = "sentence-transformers/all-MiniLM-L12-v2"
N_CLUSTERS = 5
TOP_N_TERMOS = 8


def _calcular_silhouette(embeddings, labels, ignorar_ruido=False):
    labels_serie = pd.Series(labels)

    if ignorar_ruido:
        mascara = labels_serie != -1
        labels_serie = labels_serie[mascara]
        embeddings = embeddings[mascara.to_numpy()]

    if labels_serie.nunique() < 2 or len(labels_serie) <= labels_serie.nunique():
        return None

    return round(float(silhouette_score(embeddings, labels_serie)), 4)


def _extrair_topicos(textos, labels):
    topicos = {}
    labels_serie = pd.Series(labels)
    labels_validos = sorted(label for label in labels_serie.unique() if label != -1)

    if not labels_validos:
        return topicos

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    matriz = vectorizer.fit_transform(textos)
    termos = vectorizer.get_feature_names_out()

    for label in labels_validos:
        indices = labels_serie[labels_serie == label].index
        pesos_medios = matriz[indices].mean(axis=0).A1
        melhores_indices = pesos_medios.argsort()[::-1][:TOP_N_TERMOS]
        topicos[int(label)] = [
            termos[i]
            for i in melhores_indices
            if pesos_medios[i] > 0
        ]

    return topicos


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
    topicos_kmeans = _extrair_topicos(textos, clusters_kmeans)
    topicos_hdbscan = _extrair_topicos(textos, clusters_hdbscan)
    coordenadas_2d = _reduzir_embeddings_para_2d(embeddings)

    return {
        "embedding_model": MODEL_NAME,
        "coordenadas_2d": coordenadas_2d,
        "topicos": topicos_kmeans,
        "modelos": {
            "kmeans": {
                "clusters": clusters_kmeans.tolist(),
                "quantidade_clusters": int(pd.Series(clusters_kmeans).nunique()),
                "distribuicao_clusters": _resumo_clusters(clusters_kmeans),
                "silhouette": _calcular_silhouette(embeddings, clusters_kmeans),
                "topicos": topicos_kmeans,
            },
            "hdbscan": {
                "clusters": clusters_hdbscan.tolist(),
                "quantidade_clusters": int(pd.Series(clusters_hdbscan)[pd.Series(clusters_hdbscan) != -1].nunique()),
                "distribuicao_clusters": _resumo_clusters(clusters_hdbscan),
                "percentual_ruido": round(float((clusters_hdbscan == -1).mean() * 100), 1),
                "silhouette_sem_ruido": _calcular_silhouette(
                    embeddings,
                    clusters_hdbscan,
                    ignorar_ruido=True,
                ),
                "topicos": topicos_hdbscan,
            },
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
