# Análise Estruturada de Erros

Esta seção documenta o mapeamento crítico das falhas e anomalias identificadas ao longo da execução do pipeline, categorizadas conforme as diretrizes de avaliação da disciplina.

---

### 1. Ruído Extremo (Artes ASCII e "Trolls")
* **Falha:** Formação de aglomerados residuais dispersos (capturados como ruído pelo HDBSCAN) compostos puramente por desenhos em blocos de caracteres (Artes ASCII), tabelas de premiações falsas ou repetições obsessivas de palavras-chave como *"VAC VAC VAC"*.
* **Hipótese de Causa:** O módulo de limpeza inicial foi projetado para consistência estrutural básica (`fillna` e tamanho de string) e não removeu padrões complexos de spam repetitivo e caracteres não alfanuméricos sequenciais, permitindo que esses dados fossem vetorizados.
* **Ação Proposta:** Implementar filtros heurísticos baseados em cálculo de entropia de caracteres por string e limites rígidos de taxa de caracteres repetidos por documento antes da etapa de embedding.

### 2. Ambiguidade do Dado (Ironia de Comunidade Gamer)
* **Falha:** O metadado nativo traduzido como sentimento classificou uma review como `"positivo"` e o modelo clássico tendeu a aproximá-la de termos favoráveis, mas o conteúdo semântico real continha forte sarcasmo: *"Ótimo jogo, joguei 500 horas e só encontrei 400 hackers. Recomendo."*
* **Hipótese de Causa:** Fenômeno persistente em Processamento de Linguagem Natural (NLP). Os modelos de embeddings geram vetores densos que agrupam palavras de alta polaridade lexical explícita (*"Ótimo"*, *"Recomendo"*), mascarando a quebra de contexto irônica do restante da sentença.
* **Ação Proposta:** Inserir exemplos contextuais focados (*Few-Shot Prompts*) mapeando o linguajar sarcástico da comunidade de eSports no prompt estruturado da LLM, permitindo que ela reclassifique a polaridade gerada nos insights finos.

### 3. Erro de Fronteira Semântica e Convexidade (K-Means)
* **Falha:** O algoritmo K-Means aglutinou em um mesmo cluster reclamações de otimização de hardware (queda drástica de FPS) com problemas críticos de conectividade de rede (latência/lag elevado e perda de pacotes).
* **Hipótese de Causa:** O K-Means impõe partições geométricas estritas, rígidas e convexas (esféricas) sobre o espaço vetorial. Isso o força a traçar fronteiras artificiais cortando a massa contínua central de dados e agrupando documentos semanticamente distintos localizados nas zonas de transição.
* **Ação Proposta:** Validar o uso complementar da abordagem hierárquica por densidade do **HDBSCAN**. Na execução do pipeline, o HDBSCAN provou-se metodologicamente superior ao isolar **83.2% do corpus como ruído (-1)**, permitindo que a "névoa" central ambígua fosse descartada e retendo apenas **3 clusters altamente estáveis e purificados** para a análise da LLM.

### 4. Alucinação e Expansão Paramétrica da LLM
* **Falha:** Em versões preliminares de teste de prompts livres, a LLM gerou categorizações rotulando um subgrupo como *"Problemas na progressão da campanha solo (Single Player)"*, cenário inexistente visto que Counter-Strike 2 é um produto exclusivamente focado em partidas competitivas Multiplayer.
* **Hipótese de Causa:** O modelo de linguagem utilizou o seu conhecimento prévio paramétrico genérico sobre jogos de tiro (*First-Person Shooters*) para preencher campos, em vez de restringir sua inferência unicamente ao contexto descritivo e estatístico dos clusters fornecidos na requisição.
* **Ação Proposta:** Reforçar as diretrizes de confinamento contextual e restrição estrita no System Prompt e mitigar a variabilidade de amostragem configurando a temperatura do modelo como determinística próxima a zero.

### 5. Incompatibilidade Estrutural de Contrato (Quebra de Schema Pydantic)
* **Falha:** Quebra de execução do script principal nas fases iniciais porque a LLM retornou um formato onde atributos que exigiam tipos específicos (ex: dicionários estruturados de subclusters) vieram encapsulados como blocos de texto corrido ou arrays de strings livres não mapeadas.
* **Hipótese de Causa:** Falta de aderência absoluta do modelo às diretrizes de inferência estruturada JSON quando submetido a prompts extensos ou quando ocorrem instabilidades e oscilações na API cloud.
* **Ação Proposta:** Refatoração robusta executada no arquivo `src/llm_insights.py`, substituindo a validação de texto livre pelo uso nativo de esquemas de resposta no SDK do Google (`response_schema=InsightFinal`), além do encapsulamento de segurança em blocos `try/except (ValidationError, Exception)`. Essa blindagem intercepta desvios estruturais graciosamente e engaja automaticamente a função local de contingência e fallback analítico `_fallback_sem_llm()`.
