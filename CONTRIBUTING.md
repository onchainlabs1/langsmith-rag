# 🤝 Contribuindo para LangSmith RAG

Obrigado por considerar contribuir para o projeto LangSmith RAG! Este documento fornece diretrizes para contribuir com o projeto.

## 🚀 Como Contribuir

### 1. **Fork e Clone**

```bash
# Fork o repositório no GitHub
# Depois clone seu fork
git clone https://github.com/SEU_USUARIO/langsmith-rag.git
cd langsmith-rag

# Adicione o repositório original como upstream
git remote add upstream https://github.com/onchainlabs1/langsmith-rag.git
```

### 2. **Criar uma Branch**

```bash
# Crie uma branch para sua feature
git checkout -b feature/nova-funcionalidade
# ou
git checkout -b fix/correcao-bug
```

### 3. **Desenvolver**

- Faça suas alterações
- Adicione testes se necessário
- Mantenha a documentação atualizada
- Siga as convenções de código

### 4. **Testar**

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar testes
python test_mock_langchain.py
python test_langsmith_config.py

# Verificar linting
ruff check src/
mypy src/ --ignore-missing-imports
```

### 5. **Commit e Push**

```bash
# Adicionar mudanças
git add .

# Commit com mensagem descritiva
git commit -m "feat: adiciona nova funcionalidade X"

# Push para sua branch
git push origin feature/nova-funcionalidade
```

### 6. **Pull Request**

1. Vá para o repositório original no GitHub
2. Clique em "Compare & pull request"
3. Preencha o template do PR
4. Aguarde a revisão

## 📋 Convenções

### **Commits**

Use o padrão [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` documentação
- `style:` formatação
- `refactor:` refatoração
- `test:` testes
- `chore:` tarefas de manutenção

### **Branches**

- `feature/nome-da-funcionalidade`
- `fix/nome-da-correcao`
- `docs/nome-da-documentacao`
- `refactor/nome-da-refatoracao`

### **Código**

- Use type hints em Python
- Documente funções com docstrings
- Mantenha funções pequenas e focadas
- Use nomes descritivos para variáveis

## 🧪 Testes

### **Estrutura de Testes**

```
tests/
├── test_api.py              # Testes da API
├── test_services.py         # Testes dos serviços
├── test_ai_act_compliance.py # Testes de conformidade
└── performance/
    └── k6-load-test.js      # Testes de performance
```

### **Executar Testes**

```bash
# Todos os testes
pytest tests/

# Teste específico
pytest tests/test_api.py

# Com coverage
pytest --cov=src tests/
```

## 📚 Documentação

### **Atualizar Documentação**

- README.md para mudanças principais
- DOCS/ para documentação detalhada
- Docstrings para código Python
- Comentários para lógica complexa

### **Estrutura de Documentação**

```
docs/
├── SETUP.md              # Guia de instalação
├── API.md                # Documentação da API
├── DEPLOYMENT.md         # Guia de deploy
└── CONTRIBUTING.md       # Este arquivo
```

## 🐛 Reportar Bugs

### **Template de Bug Report**

```markdown
## 🐛 Descrição do Bug

Descrição clara do bug.

## 🔄 Passos para Reproduzir

1. Vá para '...'
2. Clique em '...'
3. Veja o erro

## 🎯 Comportamento Esperado

O que deveria acontecer.

## 📸 Screenshots

Se aplicável, adicione screenshots.

## 🔧 Ambiente

- OS: [e.g. macOS, Linux, Windows]
- Python: [e.g. 3.11]
- Versão: [e.g. v1.0.0]

## 📝 Logs

Adicione logs relevantes.
```

## 💡 Sugestões de Features

### **Template de Feature Request**

```markdown
## 🚀 Feature Request

### Descrição
Descrição clara da funcionalidade.

### Caso de Uso
Por que esta funcionalidade seria útil?

### Alternativas Consideradas
Outras soluções que você considerou.

### Contexto Adicional
Qualquer outra informação relevante.
```

## 🏷️ Releases

### **Versionamento**

Seguimos [Semantic Versioning](https://semver.org/):

- `MAJOR`: mudanças incompatíveis
- `MINOR`: nova funcionalidade compatível
- `PATCH`: correções de bugs compatíveis

### **Processo de Release**

1. Atualizar CHANGELOG.md
2. Criar tag: `git tag -a v1.1.0 -m "Release v1.1.0"`
3. Push tag: `git push origin v1.1.0`
4. Criar release no GitHub

## 🤝 Código de Conduta

### **Nossos Compromissos**

- Ambiente acolhedor e inclusivo
- Respeito mútuo
- Feedback construtivo
- Foco no que é melhor para a comunidade

### **Comportamentos Inaceitáveis**

- Linguagem ou imagens ofensivas
- Comentários depreciativos
- Ataques pessoais ou políticos
- Assédio público ou privado

## 📞 Contato

- **Issues**: [GitHub Issues](https://github.com/onchainlabs1/langsmith-rag/issues)
- **Discussions**: [GitHub Discussions](https://github.com/onchainlabs1/langsmith-rag/discussions)
- **Email**: [Seu email se quiser]

## 🙏 Reconhecimentos

- Obrigado a todos os contribuidores!
- Agradecimentos especiais aos primeiros usuários
- Comunidade LangChain e Groq

---

**Obrigado por contribuir! 🎉**
