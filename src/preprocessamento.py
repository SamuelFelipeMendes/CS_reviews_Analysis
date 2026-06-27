def preparar_reviews(df):
    if df.empty or "texto" not in df.columns:
        return df.copy()

    dados = df.copy()
    dados["texto_modelo"] = dados["texto"].fillna("").astype(str).str.strip()
    dados = dados[dados["texto_modelo"].str.len() > 0]
    dados["sentimento"] = dados["recomendado"].map({True: "positivo", False: "negativo"})
    return dados.reset_index(drop=True)
