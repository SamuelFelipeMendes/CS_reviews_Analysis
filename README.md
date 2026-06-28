# Análise de Avaliações do CS2 com Clusterização e LLMs 🚀

Este projeto realiza uma mineração de textos automatizada sobre as avaliações (reviews) do jogo Counter-Strike 2 (CS2) coletadas diretamente da API da Steam. A arquitetura combina algoritmos clássicos de aprendizado não supervisionado (Machine Learning) com modelos de linguagem de grande porte (LLMs) para gerar insights de negócio estruturados e acionáveis para a Valve.
---
# Alunos:
      Samuel Mendes
      Victor Ferreira

---

## 🏗️ Arquitetura do Pipeline

O fluxo de dados do projeto segue uma abordagem de engenharia robusta dividida em módulos:

1. **Extração (`src/extracao.py`):** Coleta automática de 1.000 avaliações de usuários em tempo real via API pública da Steam.
2. **Pré-processamento (`src/preprocessamento.py`):** Limpeza estrutural de dados ausentes (`fillna`), filtragem de strings de comprimento zero e mapeamento do metadado de recomendação em categorias explícitas de sentimento (`positivo` ou `negativo`).
3. **Vetorização e Modelagem (`src/modelagem.py`):** * Geração de representações densas utilizando o modelo de embeddings `sentence-transformers/all-MiniLM-L12-v2` (384 dimensões).
   * Redução de dimensionalidade via PCA para projeção espacial e suporte à plotagem gráfica bidimensional.
   * Clusterização comparativa aplicando **K-Means** (abordagem por partição forçada) e **HDBSCAN** (abordagem hierárquica baseada em densidade).
4. **Análise de IA (`src/llm_insights.py`):** Integração com o SDK do Google Gemini alimentado pelos outputs estatísticos de ambos os algoritmos clássicos. A resposta é rigidamente estruturada através de um contrato de dados via **Pydantic** composto por um mapeamento hierárquico aninhado (`InsightFinal` e `ClusterRotulado`), contando com tratamento de exceções (`ValidationError`) e resiliência a falhas de rede.

---

## 📈 Resultados da Clusterização

* **K-Means:** Mapeou de forma geométrica e global a distribuição volumétrica do corpus, dividindo as avaliações de maneira uniforme em **5 macrotemas** de discussão.
* **HDBSCAN:** Atuou cirurgicamente como um filtro de qualidade para o LLM, identificando de forma rigorosa que **83.2% do corpus da Steam constituía ruído sem densidade clara** (mensagens de spam, artes ASCII e piadas repetitivas). De forma orgânica, o algoritmo isolou com precisão exatamente **3 clusters estáveis** nas extremidades de densidade.

Os gráficos comparativos (`grafico_kmeans.png` e `grafico_hdbscan.png`) e o arquivo final de inteligência de negócios (`relatorio_insights.txt`) são salvos automaticamente no diretório `data/processado/`.

---

### 🧠 Uso do KMeans e HDBSCAN simultaneamente pela LLM?

Em vez de escolher apenas um algoritmo, erscolhemos enviar os outputs estruturados de ambos os modelos de Machine Learning clássico para o Google Gemini. A abordagem híbrida foi adotada devido à complementaridade matemática de suas forças:

* **K-Means (Abordagem Panorâmica):** Ao forçar a partição de 100% dos dados em 5 macrotemas, o K-Means atua fornecendo uma visão holística e volumétrica do corpus. Ele garante que a LLM compreenda a totalidade do espaço amostral, mapeando tendências mesmo nas zonas de transição e garantindo representatividade global.
* **HDBSCAN (Filtro de Densidade e Qualidade):** Ao isolar rigorosamente 83.2% do corpus como ruído sem densidade clara, o HDBSCAN atua como um "curador de elite" para a IA. Ele filtra o spam e as piadas da comunidade gamer, entregando para a LLM apenas 3 núcleos semânticos purificados e incontestáveis de feedback. 

**Ganhos para o negócio:** A união de ambos evita que a LLM alucine com dados dispersos (graças ao HDBSCAN) e impede que ela perca o contexto do panorama geral do ecossistema de avaliações (graças ao K-Means). Isso otimiza o consumo de tokens e enriquece a robustez dos insights finais gerados para a Valve.

---

## 💰 Estimativa de Custos Previstos (Pipeline de 1.000 Elementos)

*Premissas para o cálculo:* Consideramos a sumarização de clusters de texto contendo, em média, 200 tokens de input (contexto dos clusters + prompt) e gerando 50 tokens de output (JSON estruturado final do Pydantic) por ciclo de chamada. Total estimado: 200.000 tokens de Input e 50.000 tokens de Output para 1.000 registros avaliados.

| Modelo Utilizado | Custo Input (por 1M) | Custo Output (por 1M) | Custo Total Estimado (1000 reqs) |
| :--- | :--- | :--- | :--- |
| **gemini-2.5-flash** | ~$0.075 | ~$0.30 | **~ $0.03** |
| **gemini-3-flash-preview** | ~$0.15 | ~$0.60 | **~ $0.06** |
| **gemini-3.1-pro-preview** | ~$3.50 | ~$10.50 | **~ $1.22** |

*Conclusão Econômica:* Os modelos da família *Flash* mostram-se ideais para a execução deste pipeline em larga escala, entregando baixíssimo custo e tempo de resposta otimizado, enquanto a variante *Pro* fica reservada para auditorias semânticas complexas.

## 🛠️ Como Executar o Projeto

1. Certifique-se de ter o Python 3.10+ instalado.
2. Crie e ative o seu ambiente virtual (`venv`).
3. Instale as dependências obrigatórias:
   ```bash
   pip install -r requirements.txt

## Como executar

```bash
python main.py
```

Para usar Gemini nos insights, crie um arquivo `.env` na pasta de config do projeto:

```env
GEMINI_API='sua_chave_aqui'
```
