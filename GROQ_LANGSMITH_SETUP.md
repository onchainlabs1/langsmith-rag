# 🚀 Groq + LangSmith Setup for EU AI Act Compliance

## Overview

This guide shows how to configure Groq with LangSmith for your EU AI Act compliance RAG system. Groq offers ultra-fast inference and excellent cost-benefit for compliance applications.

## 🔑 API Key Configuration

### 1. **Get Groq Key**

1. Visit [Groq Console](https://console.groq.com/keys)
2. Login with your account (or create one)
3. Click "Create API Key"
4. Copy the key (starts with `gsk_...`)

### 2. **Get LangSmith Key**

1. Visit [LangSmith](https://smith.langchain.com/)
2. Login with your GitHub account (already associated)
3. Go to Settings > API Keys
4. Copy the key (starts with `ls__...`)

### 3. **Configure Environment Variables**

```bash
# Groq API Key
export GROQ_API_KEY="gsk_your_real_groq_key_here"

# LangSmith API Key
export LANGCHAIN_API_KEY="your_langsmith_api_key_here"

# OpenAI API Key (for embeddings - still needed)
export OPENAI_API_KEY="sk-your_openai_key_here"

# LangSmith Configuration
export LANGCHAIN_PROJECT="groq-eu-ai-act-compliance"
export LANGCHAIN_TRACING_V2=true
```

## 🤖 Available Groq Models

### **Current Model: llama-3.1-70b-versatile**
- **Speed**: ~300 tokens/second
- **Quality**: Excellent for compliance
- **Cost**: Very low
- **Usage**: Recommended for production

### **Available Alternatives**

```python
# To change the model, edit src/services/groq_langchain_rag.py
self.llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",    # Faster, smaller
    # model_name="mixtral-8x7b-32768",    # Alternative
    # model_name="gemma-7b-it",           # Alternative
    temperature=0.1,
    max_tokens=1000
)
```

## 🧪 Testing the Configuration

### 1. **Direct Test**

```bash
# Test Groq implementation
python3 test_groq_langchain.py
```

### 2. **API Test**

```bash
# Start server
uvicorn src.main:app --reload

# In another terminal, test API
python3 test_api_langchain.py
```

### 3. **Check LangSmith**

1. Visit [LangSmith Dashboard](https://smith.langchain.com/)
2. Go to project "groq-eu-ai-act-compliance"
3. Check request traces

## 🌐 API Usage

### **Available Endpoints**

```bash
# 1. Login to get JWT
curl -X POST "http://localhost:8000/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=analyst&password=analyst"

# 2. Use token for setup
export JWT_TOKEN="your-jwt-token"
curl -X POST "http://localhost:8000/v1/langchain/setup" \
     -H "Authorization: Bearer $JWT_TOKEN"

# 3. Ask question
curl -X POST "http://localhost:8000/v1/langchain/ask" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $JWT_TOKEN" \
     -d '{"question": "What are high-risk AI systems under the EU AI Act?"}'
```

## 📊 Performance Comparison

### **Groq vs OpenAI**

| Metric | Groq Llama-3.1-70b | OpenAI GPT-4 |
|---------|-------------------|--------------|
| Speed | ~300 tokens/sec | ~50 tokens/sec |
| Cost | ~$0.10/1M tokens | ~$1.00/1M tokens |
| Quality | Excellent | Excellent |
| Privacy | ✅ Open-source | ❌ Proprietary |
| EU Compliance | ✅ Friendly | ⚠️ Data in USA |

### **Groq Benefits**

- ⚡ **6x faster** than OpenAI
- 💰 **10x cheaper** than OpenAI
- 🔓 **Open-source models** (Llama, Mixtral)
- 🌍 **No data residency** restrictions
- ⚖️ **GDPR-friendly** (no data leaving EU)

## 🔍 Monitoring with LangSmith

### **Automatic Traces**

Each question automatically generates a trace in LangSmith with:

- **Inputs**: User question
- **Outputs**: Response and sources
- **Metadata**: Model used, provider, temperature
- **Performance**: Latency, tokens used
- **Errors**: Error logs if any

### **Available Metrics**

- **Average latency**: Response time
- **Error rate**: Failure percentage
- **Token usage**: Model efficiency
- **Quality**: User feedback
- **Compliance**: Compliance score

## 🛠️ Advanced Configuration

### **Customize Prompts**

Edit `src/services/groq_langchain_rag.py`:

```python
self.prompt_template = PromptTemplate(
    template="""You are an EU AI Act compliance expert...

    Context:
    {context}

    Question: {question}
    
    Answer:""",
    input_variables=["context", "question"]
)
```

### **Adjust Parameters**

```python
self.llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-70b-versatile",
    temperature=0.1,      # Creativity (0-1)
    max_tokens=1000,      # Maximum response size
    top_p=0.9,           # Nucleus sampling
    top_k=40             # Top-k sampling
)
```

### **Configure Retrieval**

```python
self.retriever = self.vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}  # Number of documents
)
```

## 🚀 Production Deployment

### **Environment Variables**

```bash
# Production
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
