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

## Custos Previstos com LLM (Pipeline de 1000 elementos)

*Premissas para o cálculo:* 
Consideramos a sumarização e rotulação de clusters de reviews da Steam. 
Média estimada: **200 tokens de input** (contexto do cluster/prompt) e **50 tokens de output** (JSON estruturado via Pydantic) por requisição.
Total para 1000 chamadas: **200.000 tokens de Input** e **50.000 tokens de Output**.

| Modelo Utilizado | Custo Input (por 1M) | Custo Output (por 1M) | Custo Total Estimado (1000 reqs) |
| :--- | :--- | :--- | :--- |
| **gemini-2.5-flash** | ~$0.075 | ~$0.30 | **~$0.03** |
| **gemini-3-flash-preview** | ~$0.15 | ~$0.60 | **~$0.06** |
| **gemini-3.1-pro-preview** | ~$3.50 | ~$10.50 | **~$1.22** |

*Conclusão:* Para este pipeline, os modelos da família Flash são extremamente viáveis para produção devido ao baixo custo e alta velocidade, sendo suficientes para a tarefa de extração estruturada de rotulação. O modelo Pro seria utilizado apenas caso a análise semântica exigisse inferência complexa ou cruzamento de jurisprudência.
