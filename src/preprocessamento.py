<<<<<<< HEAD
def preparar_reviews(df):
    if df.empty or "texto" not in df.columns:
        return df.copy()

    dados = df.copy()
    dados["texto_modelo"] = dados["texto"].fillna("").astype(str).str.strip()
    dados = dados[dados["texto_modelo"].str.len() > 0]
    dados["sentimento"] = dados["recomendado"].map({True: "positivo", False: "negativo"})
    return dados.reset_index(drop=True)
=======
import re


STOPWORDS = {
    "a", "o", "os", "as", "um", "uma", "de", "do", "da", "dos", "das",
    "em", "no", "na", "nos", "nas", "e", "ou", "para", "por", "com",
    "que", "se", "ao", "mais", "muito", "muita", "muitos", "muitas",
    "jogo", "game", "cs", "cs2", "counter", "strike",
}


def limpar_texto(texto):
    texto = str(texto).lower()
    texto = re.sub(r"http\S+|www\S+", " ", texto)
    texto = re.sub(r"[^\w\s]", " ", texto, flags=re.UNICODE)
    palavras = [p for p in texto.split() if p not in STOPWORDS and len(p) > 2]
    return " ".join(palavras)


def preparar_reviews(df):
    if df.empty or "texto" not in df.columns:
        return df.copy()

    dados = df.copy()
    dados["texto_limpo"] = dados["texto"].apply(limpar_texto)
    dados = dados[dados["texto_limpo"].str.len() > 5]
    dados["sentimento"] = dados["recomendado"].map({True: "positivo", False: "negativo"})
    return dados.reset_index(drop=True)
>>>>>>> 4a138dda4d6e02e95ae7a3e9ce821811881a0f4d
