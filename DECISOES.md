# Diário de Decisões do Projeto

*   **Modelo de Embedding escolhido:** Optamos pelo `sentence-transformers` (ex: *paraphrase-multilingual-MiniLM-L12-v2* ou *BERTimbau*) por apresentar o melhor equilíbrio entre velocidade de inferência e captura semântica em textos informais e curtos, característicos de reviews da Steam.
*   **Estratégia de Pré-processamento:** Textos de CS2 contêm muitas gírias e artes ASCII. Aplicamos limpeza de caracteres especiais, remoção de stopwords padrão, mas mantivemos termos técnicos (ping, fps, vac, smurf) que são cruciais para a clusterização.
*   **Medida de Similaridade e Algoritmo:** Comparamos K-Means e HDBSCAN. Decidimos usar a distância do cosseno para os vetores. O HDBSCAN lidou melhor com o formato dos dados por não forçar pontos ruidosos (reviews inúteis) dentro de clusters relevantes.
*   **Campos do Schema Pydantic:** Definimos os campos `tema_principal` (string curta), `sentimento_majoritario` (Enum: Positivo/Negativo/Neutro) e `sugestao_melhoria` (string) para garantir que a saída fosse acionável para um gestor de produto do CS2.
*   **Adaptações após erros (LLM):** Observamos que o LLM ocasionalmente errava o formato JSON. Implementamos temperatura `0.1` no prompt para maior determinismo e um bloco `try/except ValidationError` no código para garantir que o pipeline não quebre.
