<<<<<<< HEAD
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


class InsightFinal(BaseModel):
    cliente: str
    problema_de_negocio: str
    principais_temas: list[str] = Field(min_length=1)
    dores_dos_jogadores: list[str] = Field(min_length=1)
    pontos_positivos: list[str] = Field(min_length=1)
    acoes_recomendadas: list[str] = Field(min_length=1)
    confianca: float = Field(ge=0, le=1)


def _fallback_sem_llm(df, resultados):
    positivos = int(df["recomendado"].sum())
    negativos = int((~df["recomendado"]).sum())
    topicos_kmeans = resultados["modelos"]["kmeans"]["topicos"]
    topicos_hdbscan = resultados["modelos"]["hdbscan"]["topicos"]
    topicos = [f"KMeans cluster {cluster}: {', '.join(termos)}" for cluster, termos in topicos_kmeans.items()]
    topicos.extend(
        f"HDBSCAN cluster {cluster}: {', '.join(termos)}"
        for cluster, termos in topicos_hdbscan.items()
    )
    if not topicos:
        topicos = ["HDBSCAN marcou a maior parte das avaliacoes como ruido; use KMeans como leitura inicial."]

    return InsightFinal(
        cliente="Gestor de produto/comunidade do Counter-Strike 2",
        problema_de_negocio=(
            f"Entender a percepcao de {len(df)} jogadores brasileiros/portugueses, "
            f"com {positivos} avaliacoes positivas e {negativos} negativas."
        ),
        principais_temas=topicos,
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

    Amostra de avaliacoes:
    {amostra}
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
=======
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


class InsightFinal(BaseModel):
    cliente: str
    problema_de_negocio: str
    principais_temas: list[str] = Field(min_length=1)
    dores_dos_jogadores: list[str] = Field(min_length=1)
    pontos_positivos: list[str] = Field(min_length=1)
    acoes_recomendadas: list[str] = Field(min_length=1)
    confianca: float = Field(ge=0, le=1)


def _fallback_sem_llm(df, resultados):
    positivos = int(df["recomendado"].sum())
    negativos = int((~df["recomendado"]).sum())
    topicos = [", ".join(termos) for termos in resultados["topicos"].values()]

    return InsightFinal(
        cliente="Gestor de produto/comunidade do Counter-Strike 2",
        problema_de_negocio=(
            f"Entender a percepcao de {len(df)} jogadores brasileiros/portugueses, "
            f"com {positivos} avaliacoes positivas e {negativos} negativas."
        ),
        principais_temas=topicos,
        dores_dos_jogadores=[
            "Problemas tecnicos ou desempenho podem aparecer nos temas negativos.",
            "Mudancas de jogabilidade e comparacoes com versoes anteriores merecem atencao.",
        ],
        pontos_positivos=[
            "Avaliacoes recomendadas indicam que parte relevante da comunidade ainda valoriza o jogo.",
            "Os topicos extraidos ajudam a localizar aspectos elogiados com mais frequencia.",
        ],
        acoes_recomendadas=[
            "Priorizar os temas mais recorrentes nas avaliacoes negativas.",
            "Separar comentarios por horas jogadas para diferenciar novatos e jogadores experientes.",
            "Acompanhar a evolucao dos temas apos atualizacoes do jogo.",
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


def gerar_insights(df, resultados):
    """Usa Gemini com saida estruturada validada por Pydantic."""
    load_dotenv()
    api_key = GEMINI_API
    if not api_key:
        return _fallback_sem_llm(df, resultados)

    amostra = df[["texto", "sentimento"]].head(30).to_dict(orient="records")
    prompt = f"""
    Voce e um analista de dados ajudando um gestor da Valve.

    Gere insights acionaveis em portugues com base nos dados abaixo.

    Topicos extraidos por TF-IDF e KMeans:
    {resultados["topicos"]}

    Amostra de avaliacoes:
    {amostra}
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
>>>>>>> 4a138dda4d6e02e95ae7a3e9ce821811881a0f4d
