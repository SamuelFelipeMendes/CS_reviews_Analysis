from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


def _plotar_clusters(coordenadas, labels, titulo, subtitulo, caminho_saida):
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    df_plot = pd.DataFrame(coordenadas, columns=["x", "y"])
    df_plot["cluster"] = labels

    fig, ax = plt.subplots(figsize=(10, 7))

    for cluster in sorted(df_plot["cluster"].unique()):
        dados_cluster = df_plot[df_plot["cluster"] == cluster]
        if cluster == -1:
            ax.scatter(
                dados_cluster["x"],
                dados_cluster["y"],
                label="Ruido (-1)",
                c="#9ca3af",
                marker="x",
                alpha=0.75,
                s=42,
            )
            continue

        ax.scatter(
            dados_cluster["x"],
            dados_cluster["y"],
            label=f"Cluster {cluster}",
            alpha=0.72,
            s=34,
        )

    ax.set_title(titulo, fontsize=15, fontweight="bold")
    ax.text(0, 1.02, subtitulo, transform=ax.transAxes, fontsize=10, color="#4b5563")
    ax.set_xlabel("Componente principal 1")
    ax.set_ylabel("Componente principal 2")
    ax.grid(alpha=0.2)
    ax.legend(loc="best", fontsize=8, frameon=True)
    fig.tight_layout()
    fig.savefig(caminho_saida, dpi=160)
    plt.close(fig)


def gerar_graficos_clusterizacao(resultados, caminho_kmeans, caminho_hdbscan):
    coordenadas = resultados["coordenadas_2d"]
    kmeans = resultados["modelos"]["kmeans"]
    hdbscan = resultados["modelos"]["hdbscan"]
    silhouette_hdbscan = hdbscan.get("silhouette", hdbscan.get("silhouette_sem_ruido"))

    _plotar_clusters(
        coordenadas=coordenadas,
        labels=kmeans["clusters"],
        titulo="KMeans sobre embeddings das avaliacoes",
        subtitulo=(
            f"{kmeans['quantidade_clusters']} clusters | "
            f"silhouette: {kmeans['silhouette']}"
        ),
        caminho_saida=caminho_kmeans,
    )

    _plotar_clusters(
        coordenadas=coordenadas,
        labels=hdbscan["clusters"],
        titulo="HDBSCAN sobre embeddings das avaliacoes",
        subtitulo=(
            f"{hdbscan['quantidade_clusters']} clusters | "
            f"ruido: {hdbscan['percentual_ruido']}% | "
            f"silhouette: {silhouette_hdbscan}"
        ),
        caminho_saida=caminho_hdbscan,
    )
