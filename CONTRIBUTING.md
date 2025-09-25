# 🤝 Contributing to LangSmith RAG

Thank you for considering contributing to the LangSmith RAG project! This document provides guidelines for contributing to the project.

## 🚀 How to Contribute

### 1. **Fork and Clone**

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/langsmith-rag.git
cd langsmith-rag

# Add the original repository as upstream
git remote add upstream https://github.com/onchainlabs1/langsmith-rag.git
```

### 2. **Create a Branch**

```bash
# Create a branch for your feature
git checkout -b feature/new-feature
# or
git checkout -b fix/bug-fix
```

### 3. **Develop**

- Make your changes
- Add tests if necessary
- Keep documentation updated
- Follow code conventions

### 4. **Test**

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python test_mock_langchain.py
python test_langsmith_config.py

# Check linting
ruff check src/
mypy src/ --ignore-missing-imports
```

### 5. **Commit and Push**

```bash
# Add changes
git add .

# Commit with descriptive message
git commit -m "feat: add new feature X"

# Push to your branch
git push origin feature/new-feature
```

### 6. **Pull Request**

1. Go to the original repository on GitHub
2. Click "Compare & pull request"
3. Fill in the PR template
4. Wait for review

## 📋 Conventions

### **Commits**

Use the [Conventional Commits](https://www.conventionalcommits.org/) pattern:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `style:` formatting
- `refactor:` refactoring
- `test:` tests
- `chore:` maintenance tasks

### **Branches**

- `feature/feature-name`
- `fix/fix-name`
- `docs/documentation-name`
- `refactor/refactoring-name`

### **Code**

- Use type hints in Python
- Document functions with docstrings
- Keep functions small and focused
- Use descriptive names for variables

## 🧪 Testing

### **Test Structure**

```
tests/
├── test_api.py              # API tests
├── test_services.py         # Service tests
├── test_ai_act_compliance.py # Compliance tests
└── performance/
    └── k6-load-test.js      # Performance tests
```

### **Run Tests**

```bash
# All tests
pytest tests/

# Specific test
pytest tests/test_api.py

# With coverage
pytest --cov=src tests/
```

## 📚 Documentation

### **Update Documentation**

- README.md for major changes
- DOCS/ for detailed documentation
- Docstrings for Python code
- Comments for complex logic

### **Documentation Structure**

```
docs/
├── SETUP.md              # Installation guide
├── API.md                # API documentation
├── DEPLOYMENT.md         # Deployment guide
└── CONTRIBUTING.md       # This file
```

## 🐛 Bug Reports

### **Bug Report Template**

```markdown
## 🐛 Bug Description

Clear description of the bug.

## 🔄 Steps to Reproduce

1. Go to '...'
2. Click on '...'
3. See error

## 🎯 Expected Behavior

What should happen.

## 📸 Screenshots

If applicable, add screenshots.

## 🔧 Environment

- OS: [e.g. macOS, Linux, Windows]
- Python: [e.g. 3.11]
- Version: [e.g. v1.0.0]

## 📝 Logs

Add relevant logs.
```

## 💡 Feature Suggestions

### **Feature Request Template**

```markdown
## 🚀 Feature Request

### Description
Clear description of the feature.

### Use Case
Why would this feature be useful?

### Alternatives Considered
Other solutions you considered.

### Additional Context
Any other relevant information.
```

## 🏷️ Releases

### **Versioning**

We follow [Semantic Versioning](https://semver.org/):

- `MAJOR`: incompatible changes
- `MINOR`: compatible new feature
- `PATCH`: compatible bug fixes

### **Release Process**

1. Update CHANGELOG.md
2. Create tag: `git tag -a v1.1.0 -m "Release v1.1.0"`
3. Push tag: `git push origin v1.1.0`
4. Create release on GitHub

## 🤝 Code of Conduct

### **Our Commitments**

- Welcoming and inclusive environment
- Mutual respect
- Constructive feedback
- Focus on what's best for the community

### **Unacceptable Behavior**

- Offensive language or images
- Derogatory comments
- Personal or political attacks
- Public or private harassment

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/onchainlabs1/langsmith-rag/issues)
- **Discussions**: [GitHub Discussions](https://github.com/onchainlabs1/langsmith-rag/discussions)
- **Email**: [Your email if desired]

## 🙏 Acknowledgments

- Thank you to all contributors!
- Special thanks to early users
- LangChain and Groq communities

---

**Thank you for contributing! 🎉**
