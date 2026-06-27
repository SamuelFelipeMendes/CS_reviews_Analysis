<<<<<<< HEAD
# Pipeline simples de mineracao de texto - Steam CS2

Este projeto coleta avaliacoes publicas em portugues do Counter-Strike 2 pela API da Steam:

`https://store.steampowered.com/appreviews/730?json=1`

O objetivo e montar uma pipeline simples que vai do dado bruto ate insights para um gestor do jogo.

## Etapas

1. **Extracao**: coleta pelo endpoint publico da Steam.
2. **Preparacao minima**: validacao de textos vazios e criacao do campo de sentimento.
3. **Embeddings semanticos**: representacao dos textos originais com `sentence-transformers`.
4. **Machine Learning**:
   - sentimento derivado do campo `recomendado` da Steam;
   - agrupamento de temas com KMeans;
   - comparacao com HDBSCAN para detectar grupos por densidade e comentarios atipicos.
5. **LLM estruturado**:
   - gera insights no formato validado por Pydantic;
   - usa Gemini quando houver `GEMINI_API_KEY`;
   - se nao houver chave, usa uma versao simples sem LLM.

## Como executar

```bash
python main.py
```

Para usar Gemini nos insights, crie um arquivo `.env` na raiz do projeto:

```env
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.5-flash
```

Saidas geradas:

- `data/raw/steam_cs2_reviews.csv`
- `data/processado/steam_cs2_reviews_processado.csv`
- `data/processado/grafico_kmeans.png`
- `data/processado/grafico_hdbscan.png`
- `data/processado/relatorio_insights.txt`

## Cliente ficticio

Gestor de produto/comunidade do Counter-Strike 2 interessado em entender reclamacoes,
elogios e prioridades de melhoria a partir das avaliacoes dos jogadores em portugues.
=======
# Pipeline simples de mineracao de texto - Steam CS2

Este projeto coleta avaliacoes publicas em portugues do Counter-Strike 2 pela API da Steam:

`https://store.steampowered.com/appreviews/730?json=1`

O objetivo e montar uma pipeline simples que vai do dado bruto ate insights para um gestor do jogo.

## Etapas

1. **Extracao**: coleta pelo endpoint publico da Steam.
2. **Pre-processamento**: limpeza basica do texto e remocao de stopwords.
3. **Embeddings classicos**: vetorizacao com TF-IDF.
4. **Machine Learning**:
   - classificacao simples de sentimento usando `recomendado` como rotulo;
   - agrupamento de temas com KMeans.
5. **LLM estruturado**:
   - gera insights no formato validado por Pydantic;
   - usa Gemini quando houver `GEMINI_API_KEY`;
   - se nao houver chave, usa uma versao simples sem LLM.

## Como executar

```bash
python main.py
```

Para usar Gemini nos insights, crie um arquivo `.env` na raiz do projeto:

```env
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-2.5-flash
```

Saidas geradas:

- `data/raw/steam_cs2_reviews.csv`
- `data/processado/steam_cs2_reviews_processado.csv`
- `data/processado/relatorio_insights.txt`

