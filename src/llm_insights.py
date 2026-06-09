import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ValidationError
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
    api_key = os.getenv(GEMINI_API)
    #api_key = ('AIzaSyDngPLiXkuXSij1fCM4fX8VMWJ3dfGnWQE')
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

    #client = genai.Client(api_key='AIzaSyDngPLiXkuXSij1fCM4fX8VMWJ3dfGnWQE')
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
