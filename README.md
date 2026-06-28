# Análise de Avaliações do CS2 com Clusterização e LLMs 🚀

Este projeto realiza uma mineração de textos automatizada sobre as avaliações (reviews) do jogo Counter-Strike 2 (CS2) coletadas diretamente da API da Steam. A arquitetura combina algoritmos clássicos de aprendizado não supervisionado (Machine Learning) com modelos de linguagem de grande porte (LLMs) para gerar insights de negócio estruturados e acionáveis para a Valve.

---

## 🏗️ Arquitetura do Pipeline

O fluxo de dados do projeto segue uma abordagem de engenharia robusta dividida em módulos:

1. **Extração (`src/extracao.py`):** Coleta automática de 1.000 avaliações de usuários em tempo real via API pública da Steam.
2. **Pré-processamento (`src/preprocessamento.py`):** Limpeza estrutural de dados ausentes (`fillna`), filtragem de strings de comprimento zero e mapeamento do metadado de recomendação em categorias explícitas de sentimento (`positivo` ou `negativo`).
3. **Vetorização e Modelagem (`src/modelagem.py`):** * Geração de representações densas utilizando o modelo de embeddings `sentence-transformers/all-MiniLM-L12-v2` (384 dimensões).
   * Redução de dimensionalidade via PCA para projeção e suporte a gráficos de dispersão bidimensionais.
   * Clusterização comparativa aplicando **K-Means** (abordagem por partição forçada em 5 macrotemas) e **HDBSCAN** (abordagem hierárquica baseada em densidade).
4. **Análise de IA (`src/llm_insights.py`):** Integração com o SDK do Google Gemini alimentado pelos outputs estatísticos de ambos os algoritmos clássicos. A resposta é rigidamente estruturada através de um contrato de dados via **Pydantic** (`InsightFinal`) com blindagem por tratamento de exceções (`ValidationError`).

---

## 📈 Resultados da Clusterização

* **K-Means:** Forçou o agrupamento total dos dados, mapeando a distribuição volumétrica e os tópicos mais recorrentes do corpus de forma macro.
* **HDBSCAN:** Atuou cirurgicamente como um filtro de qualidade, identificando que **83% do corpus da Steam constituía ruído sem densidade clara** (como spams, artes ASCII e piadas genéricas). O algoritmo isolou com precisão **3 clusters puros** nas extremidades do espaço vetorial, identificando nichos críticos e específicos de reclamações técnicas e comportamentais dos jogadores.

Os gráficos comparativos (`grafico_kmeans.png` e `grafico_hdbscan.png`) e o arquivo final de inteligência de negócios (`relatorio_insights.txt`) são salvos automaticamente no diretório `data/processado/`.

---

## 💰 Estimativa de Custos Previstos (Pipeline de 1.000 Elementos)

*Premissas para o cálculo:* Consideramos a sumarização de clusters de texto contendo, em média, 200 tokens de input (contexto dos clusters + prompt) e gerando 50 tokens de output (JSON estruturado final do Pydantic) por ciclo de chamada. Total estimado: 200.000 tokens de Input e 50.000 tokens de Output para 1.000 registros avaliados.

| Modelo Utilizado | Custo Input (por 1M) | Custo Output (por 1M) | Custo Total Estimado (1000 reqs) |
| :--- | :--- | :--- | :--- |
| **gemini-2.5-flash** | ~$0.075 | ~$0.30 | **~ $0.03** |
| **gemini-3-flash-preview** | ~$0.15 | ~$0.60 | **~ $0.06** |
| **gemini-3.1-pro-preview** | ~$3.50 | ~$10.50 | **~ $1.22** |

*Conclusão Econômica:* Os modelos da família *Flash* mostram-se ideais para a execução deste pipeline em larga escala, entregando baixíssimo custo e tempo de resposta otimizado, enquanto a variante *Pro* fica reservada para auditorias semânticas complexas.

---

## 🛠️ Como Executar o Projeto

1. Certifique-se de ter o Python 3.10+ instalado.
2. Crie e ative o seu ambiente virtual (`venv`).
3. Instale as dependências obrigatórias:
   ```bash
   pip install -r requirements.txt
