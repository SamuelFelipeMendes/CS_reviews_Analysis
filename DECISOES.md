Decisões seguindo o pipeline dos Dados

1_ Temática e Corpus: Utilizando um request de API da review de um jogo de uma plataforma chamada Steam, tudo vem a partir de um request feito pela chamada da API. Caso não haja comunicação da API, há uma função de fallback que faz com que o programa utilize um CSV previamente baixado. Por se tratar de uma quantidade muito extensa podemos escolher quantos passamos para o programa, escolhemos 1000.

2_ Pré-processamento: O pré-processamento foi extremamente simples, como criar uma analise de sentimento de forma artificial, utilizando a recomendação para definir o sentimentos da review foi positivo ou negativo e o tratamento de campo vazios e um filtro de registro com tamanho menor que zero. Devido ao modelo de embedding selecionado, não seria necessário técnicas de lematização, stemming ou StopWords. Como estamos usando um modelo que leva em consideração o contexto, praticamente tudo é relevante.

3_ Embedding e Modelo: Como escolha mais viável para a vetorização de texto para o embedding e treinamento do modelo, escolhemos o Sentence-Transformer, por causa da captura de texto mais informais e curtos, mas em grandes quantidades. Já a modelagem, seguimos a clusterização. Neste ponto, enviamos dois modelos, Kmeans e o HDBSCAN. Ambos trouxeram dados relevantes e com o silhouette score, avaliamos o mais eficiente no sentido dos agrupamentos.

3.1_ Escolha de modelos e redução de dimensionalidade: 

Usamos PCA só para visualização, não para treinar os clusters.
Os embeddings do sentence-transformers têm muitas dimensões. Por exemplo, o all-MiniLM-L12-v2 gera vetores com centenas de valores por texto. Isso é ótimo para KMeans e HDBSCAN, mas impossível de visualizar diretamente em um gráfico comum.
Então a lógica é:
Embeddings completos -> KMeans/HDBSCAN
Embeddings completos -> PCA para 2D -> gráficos
Ou seja, os modelos agrupam usando a representação completa. O PCA só transforma os embeddings em duas coordenadas:
x, y
para conseguirmos gerar gráficos como:
grafico_kmeans.png
grafico_hdbscan.png
Por que reduzir dimensionalidade?
Porque humanos conseguem interpretar visualmente 2D ou 3D, mas não conseguem olhar um vetor de centenas de dimensões. A redução permite ver, de forma aproximada:
se os clusters parecem separados;
se há sobreposição;
se o HDBSCAN marcou ruídos fora das regiões densas;
se o KMeans está forçando divisões em regiões pouco naturais.
Por que PCA?
Porque é simples, rápido, estável e já vem no scikit-learn. Para o nosso objetivo, que é só criar uma visualização comparativa simples, ele é suficiente e não aumenta a complexidade.
A ressalva importante: o gráfico com PCA é uma projeção aproximada. Ele ajuda na interpretação, mas a comparação quantitativa mais importante continua sendo feita nos embeddings completos, como o silhouette_score.

4_ Schema_Pydantic: O schema do pydantic, foi selecionados dois, um para a LLM e um para o fallback caso não haja acesso a API do Gemini. O mais relevante é o da API do gemini, que está estruturado como:


onde temos ele utiliza LLM para trazer os dados dos cluster analisados por eles, as dores dos jogadores como os maiores problema enfrentados, pontos positivos e as ações recomendada pela LLM, além de identificar os principais temas e as palavras que trazem aqueles pontos baseando-se no prompt.

5_ Insight_LLM:

