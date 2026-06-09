from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


def treinar_modelos(df):
    """Cria embeddings TF-IDF, classifica sentimento e agrupa temas."""
    textos = df["texto_limpo"]
    y = df["recomendado"].astype(int)

    vectorizer = TfidfVectorizer(max_features=1500, ngram_range=(1, 2))
    x = vectorizer.fit_transform(textos)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y
    )

    classificador = LogisticRegression(max_iter=1000)
    classificador.fit(x_train, y_train)
    pred = classificador.predict(x_test)

    kmeans = KMeans(n_clusters=5, random_state=42, n_init="auto")
    clusters = kmeans.fit_predict(x)

    termos = vectorizer.get_feature_names_out()
    topicos = {}
    for i, centroide in enumerate(kmeans.cluster_centers_):
        indices = centroide.argsort()[-8:][::-1]
        topicos[f"topico_{i}"] = [termos[j] for j in indices]

    return {
        "acuracia": accuracy_score(y_test, pred),
        "relatorio_classificacao": classification_report(y_test, pred, zero_division=0),
        "topicos": topicos,
        "clusters": clusters.tolist(),
    }
