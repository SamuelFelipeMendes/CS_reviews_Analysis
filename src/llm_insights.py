import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ValidationError
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.config import GEMINI_API, GEMINI_MODEL


class ClusterRotulado(BaseModel):
    modelo: str
    cluster_id: int
    rotulo: str
    caracteristicas_chave: list[str] = Field(min_length=1)
    insight_acionavel: str
    relevancia: str


class InsightFinal(BaseModel):
    cliente: str
    problema_de_negocio: str
    clusters_rotulados: list[ClusterRotulado] = Field(min_length=1)
    principais_temas: list[str] = Field(min_length=1)
    dores_dos_jogadores: list[str] = Field(min_length=1)
    pontos_positivos: list[str] = Field(min_length=1)
    acoes_recomendadas: list[str] = Field(min_length=1)
    confianca: float = Field(ge=0, le=1)


def _resumir_clusters_relevantes(df, resultados, limite_por_modelo=3, exemplos_por_cluster=3):
    resumos = []

    for modelo, coluna_cluster in [("kmeans", "cluster_kmeans"), ("hdbscan", "cluster_hdbscan")]:
        if coluna_cluster not in df.columns:
            continue

        dados_modelo = df[df[coluna_cluster] != -1].copy()
        if dados_modelo.empty:
            continue

        contagens = dados_modelo[coluna_cluster].value_counts().head(limite_por_modelo)
        for cluster_id, tamanho in contagens.items():
            dados_cluster = dados_modelo[dados_modelo[coluna_cluster] == cluster_id]
            negativos = int((~dados_cluster["recomendado"]).sum())
            percentual_negativo = round(negativos / len(dados_cluster) * 100, 1)
            exemplos = dados_cluster["texto"].head(exemplos_por_cluster).tolist()

            resumos.append(
                {
                    "modelo": modelo,
                    "cluster_id": int(cluster_id),
                    "tamanho": int(tamanho),
                    "percentual_negativo": percentual_negativo,
                    "exemplos": exemplos,
                }
            )

    return resumos


def _rotulos_fallback(clusters_relevantes):
    rotulos = []
    for cluster in clusters_relevantes:
        rotulo = (
            "Cluster com avaliacoes negativas"
            if cluster["percentual_negativo"] >= 50
            else "Cluster com avaliacoes mistas ou positivas"
        )
        relevancia = (
            f"{cluster['tamanho']} avaliacoes; "
            f"{cluster['percentual_negativo']}% negativas."
        )
        rotulos.append(
            ClusterRotulado(
                modelo=cluster["modelo"],
                cluster_id=cluster["cluster_id"],
                rotulo=rotulo,
                caracteristicas_chave=[
                    "rotulagem fallback baseada em exemplos do cluster",
                    f"{cluster['percentual_negativo']}% de avaliacoes negativas",
                ],
                insight_acionavel=(
                    "Revisar exemplos representativos do cluster e priorizar quando houver "
                    "alta recorrencia ou alta proporcao de avaliacoes negativas."
                ),
                relevancia=relevancia,
            )
        )

    if not rotulos:
        rotulos.append(
            ClusterRotulado(
                modelo="hdbscan",
                cluster_id=-1,
                rotulo="Comentarios dispersos ou ruido",
                caracteristicas_chave=["baixa densidade semantica", "temas pouco recorrentes"],
                insight_acionavel="Usar esses comentarios apenas como sinais qualitativos secundarios.",
                relevancia="HDBSCAN nao encontrou clusters densos relevantes.",
            )
        )

    return rotulos


def _fallback_sem_llm(df, resultados):
    positivos = int(df["recomendado"].sum())
    negativos = int((~df["recomendado"]).sum())
    clusters_relevantes = _resumir_clusters_relevantes(df, resultados)
    temas = [
        f"{cluster['modelo']} cluster {cluster['cluster_id']}: "
        f"{cluster['tamanho']} avaliacoes, {cluster['percentual_negativo']}% negativas"
        for cluster in clusters_relevantes
    ]
    if not temas:
        temas = ["HDBSCAN marcou a maior parte das avaliacoes como ruido; use KMeans como leitura inicial."]

    return InsightFinal(
        cliente="Gestor de produto/comunidade do Counter-Strike 2",
        problema_de_negocio=(
            f"Entender a percepcao de {len(df)} jogadores brasileiros/portugueses, "
            f"com {positivos} avaliacoes positivas e {negativos} negativas."
        ),
        clusters_rotulados=_rotulos_fallback(clusters_relevantes),
        principais_temas=temas,
        dores_dos_jogadores=[
            "Problemas tecnicos ou desempenho podem aparecer nos temas negativos.",
            "Mudancas de jogabilidade e comparacoes com versoes anteriores merecem atencao.",
        ],
        pontos_positivos=[
            "Avaliacoes recomendadas indicam que parte relevante da comunidade ainda valoriza o jogo.",
            "A comparacao entre KMeans e HDBSCAN ajuda a separar temas recorrentes de comentarios atipicos.",
        ],
        acoes_recomendadas=[
            "Priorizar os temas mais recorrentes nas avaliacoes negativas.",
            "Separar comentarios por horas jogadas para diferenciar novatos e jogadores experientes.",
            "Usar o KMeans para visao geral e o HDBSCAN para identificar grupos densos e possiveis outliers.",
        ],
        confianca=0.65,
    )


def _validar_resposta_gemini(resposta):
    parsed = getattr(resposta, "parsed", None)
    if isinstance(parsed, InsightFinal):
        return parsed
    if isinstance(parsed, dict):
        return InsightFinal.model_validate(parsed)

    return InsightFinal.model_validate_json(resposta.text)


def _resumir_modelo_para_prompt(resultado_modelo):
    return {
        chave: valor
        for chave, valor in resultado_modelo.items()
        if chave != "clusters"
    }


def gerar_insights(df, resultados):
    """Usa Gemini com saida estruturada validada por Pydantic."""
    load_dotenv()
    api_key = GEMINI_API
    if not api_key:
        return _fallback_sem_llm(df, resultados)

    amostra = df[["texto", "sentimento"]].head(30).to_dict(orient="records")
    clusters_relevantes = _resumir_clusters_relevantes(df, resultados)
    kmeans_prompt = _resumir_modelo_para_prompt(resultados["modelos"]["kmeans"])
    hdbscan_prompt = _resumir_modelo_para_prompt(resultados["modelos"]["hdbscan"])
    prompt = f"""
    Voce e um analista de dados ajudando um gestor da Valve.

    Gere insights acionaveis em portugues com base nos dados abaixo.

    Os textos foram representados com embeddings do modelo:
    {resultados["embedding_model"]}

    Comparacao de clusterizacao:
    {resultados["comparacao_clusterizacao"]}

    Resultado KMeans:
    {kmeans_prompt}

    Resultado HDBSCAN:
    {hdbscan_prompt}

    Clusters mais relevantes para rotulacao automatica:
    {clusters_relevantes}

    Amostra de avaliacoes:
    {amostra}

    Para cada cluster relevante, preencha clusters_rotulados com:
    - modelo;
    - cluster_id;
    - rotulo curto e interpretavel;
    - caracteristicas_chave;
    - insight_acionavel;
    - relevancia.
    """
    client = genai.Client(api_key=api_key)
    modelo = os.getenv("GEMINI_MODEL", GEMINI_MODEL)
    resposta = client.models.generate_content(
        model=modelo,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=InsightFinal,
        ),
    )

    try:
        return _validar_resposta_gemini(resposta)
    except ValidationError:
        return _fallback_sem_llm(df, resultados)
