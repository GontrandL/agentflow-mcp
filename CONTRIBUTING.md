# Contributing to AgentFlow MCP

Thank you for considering contributing to AgentFlow MCP! 🎉

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

---

## Code of Conduct

This project adheres to a simple Code of Conduct:

**Be respectful, be constructive, be helpful.**

We're all here to build something great together. Treat others with kindness and respect.

---

## How Can I Contribute?

### Reporting Bugs

Found a bug? Help us fix it!

1. **Check existing issues** - Someone may have already reported it
2. **Create a new issue** with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages or logs

**Template:**
```markdown
**Bug Description:**
Brief description of the issue

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: Ubuntu 22.04
- Python: 3.11.2
- AgentFlow version: 0.1.0-beta.1
```

### Suggesting Features

Have an idea? We'd love to hear it!

1. **Check existing feature requests**
2. **Create a new issue** labeled "enhancement"
3. **Describe:**
   - The problem it solves
   - Proposed solution
   - Alternative solutions considered
   - Use cases

### Improving Documentation

Documentation improvements are always welcome!

- Fix typos
- Clarify confusing sections
- Add examples
- Translate to other languages

### Contributing Code

Want to write code? Awesome!

1. **Find an issue** or create one
2. **Comment** that you're working on it
3. **Fork the repository**
4. **Create a branch** (`git checkout -b feature/amazing-feature`)
5. **Make your changes**
6. **Write tests**
7. **Submit a pull request**

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/agentflow-mcp.git
cd agentflow-mcp/agentflow-src
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov black ruff mypy
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 5. Run Tests

```bash
pytest tests/ -v
# Should show: 28/28 passing
```

---

## Pull Request Process

### Before Submitting

- ✅ Code follows style guide (see below)
- ✅ All tests pass
- ✅ New tests added for new features
- ✅ Documentation updated
- ✅ CHANGELOG.md updated (if applicable)
- ✅ Commit messages are clear

### Commit Message Format

```
type(scope): Brief description

Detailed description if needed.

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance

**Examples:**
```
feat(apc): Add streaming context compression

fix(agentflow): Handle OpenRouter rate limits

docs(readme): Update installation instructions

test(apc): Add compression ratio edge cases
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## How Has This Been Tested?
Describe tests you ran

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Code follows style guide
```

---

## Coding Standards

### Python Style

We follow **PEP 8** with these specifics:

- **Line length:** 100 characters
- **Indentation:** 4 spaces
- **Imports:** Organized (stdlib, third-party, local)
- **Type hints:** Required for public APIs
- **Docstrings:** Google style

**Example:**

```python
from typing import List, Dict, Any
import structlog

logger = structlog.get_logger(__name__)


def compress_context(
    conversation: List[Dict[str, str]],
    target_tokens: int = 8000
) -> Dict[str, Any]:
    """
    Compress conversation history to target token count.
    
    Args:
        conversation: List of message dictionaries
        target_tokens: Target token count for compression
        
    Returns:
        Dictionary with compressed context and metadata
        
    Raises:
        ValueError: If conversation is empty
    """
    if not conversation:
        raise ValueError("Conversation cannot be empty")
        
    # Implementation...
    return result
```

### Code Formatting

Use **Black** and **Ruff**:

```bash
# Format code
black agentflow/

# Lint
ruff check agentflow/

# Type check
mypy agentflow/
```

### Best Practices

1. **Keep functions small** - Single responsibility
2. **Use type hints** - Helps catch bugs early
3. **Write docstrings** - Explain what, not how
4. **Handle errors** - Don't let exceptions bubble silently
5. **Log appropriately** - Use structlog
6. **Test thoroughly** - Aim for 80%+ coverage

---

## Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_apc_integration.py -v

# Specific test
pytest tests/test_apc_integration.py::TestContextGenerator::test_initialization -v

# With coverage
pytest tests/ --cov=agentflow --cov-report=html
```

### Writing Tests

**Location:** `tests/test_*.py`

**Structure:**

```python
import pytest
from agentflow.core.context_generator import ContextGenerator


class TestContextGenerator:
    """Test suite for ContextGenerator class."""
    
    def test_initialization(self):
        """Test ContextGenerator initializes correctly."""
        generator = ContextGenerator()
        assert generator is not None
        assert generator.target_tokens == 8000
    
    def test_compression_ratio(self):
        """Test compression achieves expected ratio."""
        generator = ContextGenerator()
        conversation = [...]  # Test data
        
        result = generator.generate_context(conversation, "task")
        
        assert result.compression_ratio > 1.0
        assert result.total_tokens <= 8000
```

### Test Guidelines

- **Test one thing** - Each test should verify one behavior
- **Use descriptive names** - `test_compression_handles_empty_conversation`
- **Arrange-Act-Assert** - Clear test structure
- **Use fixtures** - For common setup
- **Mock external calls** - Don't hit real APIs in tests

---

## Documentation

### Code Documentation

- **Module docstrings** - Explain module purpose
- **Class docstrings** - Explain class responsibility
- **Function docstrings** - Args, Returns, Raises
- **Inline comments** - For complex logic only

### External Documentation

When adding features, update:

- **README.md** - If it affects quick start
- **INSTALL.md** - If it affects installation
- **EXAMPLES.md** - Add usage examples
- **CHANGELOG.md** - Document the change

---

## Project Structure

```
agentflow-src/
├── agentflow/
│   ├── core/           # Core functionality
│   ├── orchestration/  # Orchestration logic
│   ├── integration/    # Integration components
│   ├── mcp/            # MCP server implementations
│   └── utils/          # Utility functions
├── tests/              # Test suite
├── docs/               # Documentation
├── examples/           # Usage examples
└── scripts/            # Development scripts
```

---

## Release Process

### Versioning

We use **Semantic Versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes

### Creating a Release

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. GitHub Actions will create release

---

## Getting Help

**Questions?** Ask in:
- **GitHub Discussions** - General questions
- **GitHub Issues** - Bug reports and features
- **Email** - gontrand@local

---

## Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

**Thank you for contributing!** 🎉

---

**First time contributing?** Look for issues labeled `good-first-issue`!
