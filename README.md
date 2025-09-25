# 🚀 LangSmith RAG - EU AI Act Compliance System

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-orange.svg)](https://python.langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-0.23+-purple.svg)](https://groq.com/)
[![LangSmith](https://img.shields.io/badge/LangSmith-0.3+-red.svg)](https://smith.langchain.com/)

> **Sistema RAG especializado em conformidade com o EU AI Act usando LangChain, Groq e LangSmith para inferência ultra-rápida e monitoramento completo.**

## 🌟 Características Principais

- ⚡ **Inferência Ultra-Rápida**: Groq com ~300 tokens/segundo (6x mais rápido que OpenAI)
- 💰 **Custo-Efetivo**: ~10x mais barato que OpenAI
- 🔍 **Monitoramento Completo**: Traces automáticos no LangSmith
- ⚖️ **Foco em Conformidade**: Especializado em EU AI Act
- 🛡️ **Segurança**: Autenticação JWT e observabilidade completa
- 🌍 **EU-Friendly**: Sem restrições de residência de dados
- 📊 **Observabilidade**: Métricas Prometheus e Grafana
- 🔄 **Auto-Detecção**: Groq > OpenAI > Mock automaticamente

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI API   │    │   LangSmith     │
│                 │◄──►│                 │◄──►│   Tracing       │
│  User Interface │    │  REST Endpoints │    │   Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Groq LLM      │    │   LangChain     │    │   Vector Store  │
│                 │◄──►│   RAG Pipeline  │◄──►│   FAISS         │
│  Ultra-Fast     │    │   Orchestration │    │   Embeddings    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Início Rápido

### 1. **Clone o Repositório**

```bash
git clone https://github.com/onchainlabs1/langsmith-rag.git
cd langsmith-rag
```

### 2. **Instalar Dependências**

```bash
pip install -r requirements.txt
```

### 3. **Configurar Chaves API**

```bash
# Groq API Key (GRATUITO)
export GROQ_API_KEY="gsk_sua_chave_groq_aqui"

# LangSmith API Key (GRATUITO - 5.000 traces/mês)
export LANGCHAIN_API_KEY="ls__sua_chave_langsmith_aqui"

# OpenAI API Key (para embeddings)
export OPENAI_API_KEY="sk-sua_chave_openai_aqui"

# Configurações LangSmith
export LANGCHAIN_PROJECT="groq-eu-ai-act-compliance"
export LANGCHAIN_TRACING_V2=true
```

### 4. **Testar Configuração**

```bash
# Testar LangSmith
python3 test_langsmith_config.py

# Testar sistema completo
python3 test_groq_langchain.py
```

### 5. **Iniciar Servidor**

```bash
uvicorn src.main:app --reload
```

### 6. **Acessar Interface**

- **API Documentation**: http://localhost:8000/docs
- **Streamlit UI**: `streamlit run ui_app.py`
- **LangSmith Traces**: https://smith.langchain.com/

## 📋 Como Obter as Chaves API

### **Groq API Key (GRATUITO)**
1. Acesse [console.groq.com/keys](https://console.groq.com/keys)
2. Faça login/crie conta
3. Clique em "Create API Key"
4. Copie a chave (começa com `gsk_...`)

### **LangSmith API Key (GRATUITO)**
1. Acesse [smith.langchain.com](https://smith.langchain.com/)
2. Login com GitHub
3. Settings > API Keys > Create API Key
4. Copie a chave (começa com `ls__...`)

### **OpenAI API Key**
1. Acesse [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Crie nova chave
3. Copie a chave (começa com `sk-...`)

## 🧪 Testes

```bash
# Testar configuração LangSmith
python3 test_langsmith_config.py

# Testar sistema Groq
python3 test_groq_langchain.py

# Testar API endpoints
python3 test_api_langchain.py

# Testar mock (sem chaves API)
python3 test_mock_langchain.py
```

## 🌐 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/v1/langchain/health` | Health check |
| `POST` | `/v1/langchain/setup` | Inicializar sistema RAG |
| `POST` | `/v1/langchain/ask` | Fazer perguntas sobre EU AI Act |
| `GET` | `/v1/langchain/similar/{query}` | Buscar documentos similares |
| `GET` | `/v1/langchain/info` | Informações do sistema |
| `POST` | `/v1/auth/login` | Autenticação JWT |

### **Exemplo de Uso**

```bash
# Login
curl -X POST "http://localhost:8000/v1/auth/login" \
     -d "username=analyst&password=analyst"

# Setup
curl -X POST "http://localhost:8000/v1/langchain/setup" \
     -H "Authorization: Bearer $JWT_TOKEN"

# Fazer pergunta
curl -X POST "http://localhost:8000/v1/langchain/ask" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $JWT_TOKEN" \
     -d '{"question": "What are high-risk AI systems under the EU AI Act?"}'
```

## 📊 Performance

### **Comparação de LLMs**

| Métrica | Groq | OpenAI | Mock |
|---------|------|--------|------|
| Velocidade | 300 tok/s | 50 tok/s | Instantâneo |
| Custo | $0.10/1M | $1.00/1M | Grátis |
| Qualidade | Excelente | Excelente | Básica |
| LangSmith | ✅ | ✅ | ❌ |

### **Benefícios do Groq**

- ⚡ **6x mais rápido** que OpenAI
- 💰 **10x mais barato** que OpenAI
- 🔓 **Modelos open-source** (Llama, Mixtral)
- 🌍 **Sem restrições de dados** (não sai da UE)
- ⚖️ **GDPR-friendly**

## 🛠️ Desenvolvimento

### **Estrutura do Projeto**

```
langsmith-rag/
├── src/
│   ├── api/                    # Endpoints da API
│   ├── app/services/           # Serviços avançados
│   ├── core/                   # Configuração e segurança
│   ├── services/               # Serviços LangChain
│   └── main.py                 # Aplicação FastAPI
├── tests/                      # Testes automatizados
├── monitoring/                 # Configuração Prometheus/Grafana
├── docs/                       # Documentação
└── requirements.txt            # Dependências
```

### **Scripts de Desenvolvimento**

```bash
# Desenvolvimento
uvicorn src.main:app --reload

# Testes
pytest tests/

# Linting
ruff src/
mypy src/

# Docker
make docker-build
make docker-run
```

## 🐳 Docker

```bash
# Build
docker build -t langsmith-rag .

# Run
docker run -p 8000:8000 \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -e LANGCHAIN_API_KEY=$LANGCHAIN_API_KEY \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  langsmith-rag
```

## 📈 Monitoramento

### **Prometheus Metrics**
- Acesse: http://localhost:8000/metrics

### **Grafana Dashboard**
- Configuração em `monitoring/grafana/`

### **LangSmith Traces**
- Acesse: https://smith.langchain.com/
- Projeto: `groq-eu-ai-act-compliance`

## 🔒 Segurança

- ✅ Autenticação JWT
- ✅ Rate limiting
- ✅ Input validation
- ✅ Error handling
- ✅ Observabilidade completa
- ✅ Logs estruturados

## 📚 Documentação

- [Guia de Implementação LangChain](LANGCHAIN_IMPLEMENTATION_GUIDE.md)
- [Setup Groq + LangSmith](GROQ_LANGSMITH_SETUP.md)
- [Arquitetura do Sistema](ARCHITECTURE.md)
- [Observabilidade](OBSERVABILITY.md)
- [Segurança](SECURITY.md)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [LangChain](https://python.langchain.com/) - Framework de LLM
- [Groq](https://groq.com/) - Inferência ultra-rápida
- [LangSmith](https://smith.langchain.com/) - Monitoramento e tracing
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [Streamlit](https://streamlit.io/) - Interface de usuário

## 📞 Suporte

- 📧 **Issues**: [GitHub Issues](https://github.com/onchainlabs1/langsmith-rag/issues)
- 📖 **Documentação**: [Wiki do Projeto](https://github.com/onchainlabs1/langsmith-rag/wiki)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/onchainlabs1/langsmith-rag/discussions)

---

**Desenvolvido com ❤️ para conformidade com EU AI Act**

⭐ **Se este projeto foi útil, considere dar uma estrela!**
