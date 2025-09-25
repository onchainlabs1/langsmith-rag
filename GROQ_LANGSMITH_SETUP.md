# 🚀 Configuração Groq + LangSmith para EU AI Act Compliance

## Visão Geral

Este guia mostra como configurar o Groq com LangSmith para o seu sistema RAG de conformidade com o EU AI Act. O Groq oferece inferência ultra-rápida e custo-benefício excelente para aplicações de compliance.

## 🔑 Configuração das Chaves API

### 1. **Obter Chave do Groq**

1. Acesse [Groq Console](https://console.groq.com/keys)
2. Faça login com sua conta (ou crie uma)
3. Clique em "Create API Key"
4. Copie a chave (começa com `gsk_...`)

### 2. **Obter Chave do LangSmith**

1. Acesse [LangSmith](https://smith.langchain.com/)
2. Faça login com sua conta GitHub (já associada)
3. Vá em Settings > API Keys
4. Copie a chave (começa com `ls__...`)

### 3. **Configurar Variáveis de Ambiente**

```bash
# Groq API Key
export GROQ_API_KEY="gsk_your_real_groq_key_here"

# LangSmith API Key
export LANGCHAIN_API_KEY="ls__your_real_langsmith_key_here"

# OpenAI API Key (para embeddings - ainda necessário)
export OPENAI_API_KEY="sk-your_openai_key_here"

# Configurações do LangSmith
export LANGCHAIN_PROJECT="groq-eu-ai-act-compliance"
export LANGCHAIN_TRACING_V2=true
```

## 🤖 Modelos Groq Disponíveis

### **Modelo Atual: llama-3.1-70b-versatile**
- **Velocidade**: ~300 tokens/segundo
- **Qualidade**: Excelente para compliance
- **Custo**: Muito baixo
- **Uso**: Recomendado para produção

### **Alternativas Disponíveis**

```python
# Para mudar o modelo, edite src/services/groq_langchain_rag.py
self.llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",    # Mais rápido, menor
    # model_name="mixtral-8x7b-32768",    # Alternativa
    # model_name="gemma-7b-it",           # Alternativa
    temperature=0.1,
    max_tokens=1000
)
```

## 🧪 Testando a Configuração

### 1. **Teste Direto**

```bash
# Testar implementação Groq
python3 test_groq_langchain.py
```

### 2. **Teste da API**

```bash
# Iniciar servidor
uvicorn src.main:app --reload

# Em outro terminal, testar API
python3 test_api_langchain.py
```

### 3. **Verificar LangSmith**

1. Acesse [LangSmith Dashboard](https://smith.langchain.com/)
2. Vá para o projeto "groq-eu-ai-act-compliance"
3. Verifique os traces das requisições

## 🌐 Uso da API

### **Endpoints Disponíveis**

```bash
# 1. Login para obter JWT
curl -X POST "http://localhost:8000/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=analyst&password=analyst"

# 2. Usar token para setup
export JWT_TOKEN="seu-jwt-token"
curl -X POST "http://localhost:8000/v1/langchain/setup" \
     -H "Authorization: Bearer $JWT_TOKEN"

# 3. Fazer pergunta
curl -X POST "http://localhost:8000/v1/langchain/ask" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $JWT_TOKEN" \
     -d '{"question": "What are high-risk AI systems under the EU AI Act?"}'
```

## 📊 Comparação de Performance

### **Groq vs OpenAI**

| Métrica | Groq Llama-3.1-70b | OpenAI GPT-4 |
|---------|-------------------|--------------|
| Velocidade | ~300 tokens/seg | ~50 tokens/seg |
| Custo | ~$0.10/1M tokens | ~$1.00/1M tokens |
| Qualidade | Excelente | Excelente |
| Privacidade | ✅ Open-source | ❌ Proprietário |
| EU Compliance | ✅ Amigável | ⚠️ Dados nos EUA |

### **Benefícios do Groq**

- ⚡ **6x mais rápido** que OpenAI
- 💰 **10x mais barato** que OpenAI
- 🔓 **Modelos open-source** (Llama, Mixtral)
- 🌍 **Sem restrições de residência** de dados
- ⚖️ **Amigável ao GDPR** (sem dados saindo da UE)

## 🔍 Monitoramento com LangSmith

### **Traces Automáticos**

Cada pergunta gera automaticamente um trace no LangSmith com:

- **Inputs**: Pergunta do usuário
- **Outputs**: Resposta e fontes
- **Metadata**: Modelo usado, provider, temperatura
- **Performance**: Latência, tokens utilizados
- **Erros**: Logs de erros se houver

### **Métricas Disponíveis**

- **Latência média**: Tempo de resposta
- **Taxa de erro**: Percentual de falhas
- **Uso de tokens**: Eficiência do modelo
- **Qualidade**: Feedback dos usuários
- **Compliance**: Score de conformidade

## 🛠️ Configuração Avançada

### **Personalizar Prompts**

Edite `src/services/groq_langchain_rag.py`:

```python
self.prompt_template = PromptTemplate(
    template="""Você é um especialista em conformidade com o EU AI Act...

    Contexto:
    {context}

    Pergunta: {question}
    
    Resposta:""",
    input_variables=["context", "question"]
)
```

### **Ajustar Parâmetros**

```python
self.llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-70b-versatile",
    temperature=0.1,      # Criatividade (0-1)
    max_tokens=1000,      # Tamanho máximo da resposta
    top_p=0.9,           # Nucleus sampling
    top_k=40             # Top-k sampling
)
```

### **Configurar Retrieval**

```python
self.retriever = self.vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}  # Número de documentos
)
```

## 🚀 Deploy em Produção

### **Variáveis de Ambiente**

```bash
# Produção
GROQ_API_KEY=gsk_production_key
LANGCHAIN_API_KEY=ls__production_key
OPENAI_API_KEY=sk-production_key
LANGCHAIN_PROJECT=eu-ai-act-production
ENVIRONMENT=production
```

### **Docker**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
ENV GROQ_API_KEY=${GROQ_API_KEY}
ENV LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY}

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📈 Monitoramento e Alertas

### **Métricas Prometheus**

```bash
# Verificar métricas
curl http://localhost:8000/metrics
```

### **Alertas Recomendados**

- Latência > 2 segundos
- Taxa de erro > 5%
- Uso de tokens > limite
- Falhas de conectividade Groq

## 🆘 Troubleshooting

### **Problemas Comuns**

1. **"Groq API key not found"**
   ```bash
   export GROQ_API_KEY="gsk_your_real_key"
   ```

2. **"LangSmith not tracing"**
   ```bash
   export LANGCHAIN_TRACING_V2=true
   export LANGCHAIN_API_KEY="ls__your_real_key"
   ```

3. **"Rate limit exceeded"**
   - Groq tem limites generosos
   - Verifique uso no console

4. **"Model not available"**
   - Verifique modelo em https://console.groq.com/docs/models
   - Use modelo alternativo

### **Logs e Debug**

```bash
# Logs detalhados
export LOG_LEVEL=DEBUG
uvicorn src.main:app --reload

# Verificar status Groq
curl -H "Authorization: Bearer $GROQ_API_KEY" \
     https://api.groq.com/openai/v1/models
```

## 🎯 Próximos Passos

1. **Configurar chaves API** (Groq + LangSmith)
2. **Testar implementação** com `test_groq_langchain.py`
3. **Verificar traces** no LangSmith
4. **Ajustar prompts** para seu caso de uso
5. **Configurar monitoramento** e alertas
6. **Deploy em produção**

## 📚 Recursos Adicionais

- [Groq Documentation](https://console.groq.com/docs)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangChain Groq Integration](https://python.langchain.com/docs/integrations/llms/groq)
- [EU AI Act Full Text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52021PC0206)

---

**Configuração completa! 🎉**

Seu sistema agora usa Groq para inferência ultra-rápida e LangSmith para monitoramento completo, mantendo foco em conformidade com o EU AI Act.
