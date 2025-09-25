#!/bin/bash

# Script para configurar e subir o projeto langsmith-rag para GitHub
# Repositório: https://github.com/onchainlabs1/langsmith-rag

echo "🚀 Configurando projeto langsmith-rag para GitHub..."
echo "Repositório: https://github.com/onchainlabs1/langsmith-rag"
echo "================================================"

# Verificar se estamos no diretório correto
if [ ! -f "src/main.py" ]; then
    echo "❌ Erro: Execute este script na raiz do projeto langsmith-rag"
    exit 1
fi

# Verificar se git está instalado
if ! command -v git &> /dev/null; then
    echo "❌ Git não está instalado. Instale o Git primeiro."
    exit 1
fi

# Inicializar git se não estiver inicializado
if [ ! -d ".git" ]; then
    echo "📁 Inicializando repositório git..."
    git init
fi

# Adicionar remote se não existir
if ! git remote get-url origin &> /dev/null; then
    echo "🔗 Adicionando remote origin..."
    git remote add origin https://github.com/onchainlabs1/langsmith-rag.git
fi

# Verificar status
echo "📊 Status atual do git:"
git status

# Adicionar todos os arquivos
echo "📝 Adicionando arquivos ao git..."
git add .

# Verificar se há mudanças para commit
if git diff --staged --quiet; then
    echo "ℹ️ Nenhuma mudança para commitar."
else
    # Fazer commit
    echo "💾 Fazendo commit inicial..."
    git commit -m "🚀 Initial commit: EU AI Act Compliance RAG System

- ✅ Groq + LangChain implementation
- ✅ LangSmith tracing integration  
- ✅ FastAPI with JWT authentication
- ✅ Streamlit UI interface
- ✅ Comprehensive testing suite
- ✅ Docker support
- ✅ Monitoring with Prometheus/Grafana
- ✅ Complete documentation
- ✅ Auto-detection: Groq > OpenAI > Mock
- ✅ Ultra-fast inference (~300 tokens/sec)
- ✅ Cost-effective (10x cheaper than OpenAI)
- ✅ EU-friendly (no data leaving EU)"

    # Subir para GitHub
    echo "⬆️ Subindo para GitHub..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo "✅ Sucesso! Projeto subido para GitHub."
        echo "🔗 Acesse: https://github.com/onchainlabs1/langsmith-rag"
    else
        echo "❌ Erro ao subir para GitHub. Verifique sua conexão e credenciais."
        exit 1
    fi
fi

echo ""
echo "🎉 Configuração concluída!"
echo "📋 Próximos passos:"
echo "1. Configure suas chaves API:"
echo "   export GROQ_API_KEY='sua_chave_groq'"
echo "   export LANGCHAIN_API_KEY='sua_chave_langsmith'"
echo "   export OPENAI_API_KEY='sua_chave_openai'"
echo ""
echo "2. Teste o sistema:"
echo "   python3 test_groq_langchain.py"
echo ""
echo "3. Inicie o servidor:"
echo "   uvicorn src.main:app --reload"
echo ""
echo "4. Acesse a documentação:"
echo "   http://localhost:8000/docs"
echo ""
echo "🔗 Repositório: https://github.com/onchainlabs1/langsmith-rag"
