## Análise Estruturada de Erros

1.  **Ruído Extremo (Artes ASCII e "Trolls")**
    *   *Falha:* Clusters inteiros formados apenas por reviews contendo desenhos em caracteres ou textos repetitivos ("VAC VAC VAC").
    *   *Hipótese de causa:* Limpeza de dados inicial insuficiente para detectar padrões de spam em textos de internet.
    *   *Ação proposta:* Implementar um filtro baseado em entropia de caracteres e limite mínimo/máximo de palavras antes da vetorização.

2.  **Ambiguidade do Dado (Ironia)**
    *   *Falha:* O modelo clássico e o LLM classificaram o sentimento como "Positivo", mas o texto dizia: *"Ótimo jogo, joguei 500 horas e só encontrei 400 hackers. Recomendo."*
    *   *Hipótese de causa:* Ironia é um desafio persistente em NLP. O embedding capturou palavras de alta polaridade positiva ("Ótimo", "Recomendo").
    *   *Ação proposta:* Incluir exemplos few-shot de ironia gamer no prompt do LLM para refinar a extração de sentimento.

3.  **Erro de Clusterização (K-Means)**
    *   *Falha:* O K-Means misturou reclamações técnicas (queda de FPS) com problemas de rede (lag/ping alto) no mesmo cluster.
    *   *Hipótese de causa:* K-Means tende a criar clusters esféricos de tamanhos similares, o que não reflete a densidade real dos problemas técnicos.
    *   *Ação proposta:* Utilizar o algoritmo HDBSCAN, que se mostrou superior ao separar melhor nichos de alta densidade sem forçar fronteiras artificiais. O HDBSCAN atuou como um filtro de qualidade, entregando para o LLM apenas as reviews que realmente continham discussões densas e estruturadas sobre o jogo, economizando tokens e evitando alucinações.

4.  **Alucinação do LLM**
    *   *Falha:* O LLM nomeou um cluster de reclamações como "Problemas com a campanha Single Player", sendo que CS2 é um jogo puramente Multiplayer.
    *   *Hipótese de causa:* O modelo usou conhecimento paramétrico genérico sobre jogos de tiro em vez de focar apenas no contexto fornecido no prompt.
    *   *Ação proposta:* Reforçar no System Prompt a restrição estrita ao texto de entrada e zerar a temperatura do modelo (`temperature=0.0`).

5.  **Falha de Schema (Pydantic)**
    *   *Falha:* Quebra do script porque o LLM retornou a variável `sugestao_melhoria` como uma lista de strings em vez de uma string única.
    *   *Hipótese de causa:* Falta de coerção estrita por parte da API do LLM em chamadas complexas.
    *   *Ação proposta:* Uso do `try/except ValidationError` do Pydantic acoplado a um mecanismo de `retry` (tentar novamente a requisição formatando a resposta).
