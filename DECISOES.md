# Diário de Decisões do Projeto

*   **Modelo de Embedding escolhido:** Optamos pelo `sentence-transformers/all-MiniLM-L12-v2` por apresentar o melhor equilíbrio entre velocidade de inferência e captura semântica em textos informais e curtos, característicos de reviews da Steam.
  
*   **Estratégia de Pré-processamento:** Textos de CS2 contêm muitas gírias e artes ASCII. O pré-processamento adotado em preprocessamento.py priorizou a integridade estrutural do corpus antes da vetorização. Realizamos o tratamento de dados ausentes (convertendo eventuais campos nulos em strings limpas) e filtramos registros cujo comprimento de texto fosse igual a zero. Além disso, aproveitamos o metadado nativo da Steam (recomendado) para mapear explicitamente a polaridade de sentimento de cada avaliação em 'positivo' ou 'negativo', gerando uma feature de suporte para a análise subsequente.

*   **Medida de Similaridade e Algoritmo:** Comparamos K-Means e HDBSCAN. Decidimos usar a distância do cosseno para os vetores. O HDBSCAN lidou melhor com o formato dos dados por não forçar pontos ruidosos (reviews inúteis) dentro de clusters relevantes.

*   **Campos do Schema Pydantic:** Estruturamos a classe `InsightFinal` contendo campos estratégicos (`cliente`, `problema_de_negocio`, `principais_temas`, `dores_dos_jogadores`, `pontos_positivos`, `acoes_recomendadas` e `confianca`). Essa modelagem garante que a resposta do LLM atenda perfeitamente aos requisitos de negócio demandados por um gestor da Valve.

*   **Mecanismos de Confiabilidade do Software:** Forçamos o comportamento determinístico da API do Gemini utilizando o parâmetro `response_schema=InsightFinal`. Além disso, implementamos uma cláusula de salvaguarda com `try/except ValidationError` para acionar um pipeline de fallback analítico caso a validação do contrato de dados falhasse.
