# Contributing to AI Hotel Receptionist

Thank you for considering contributing to the AI Hotel Receptionist project! We welcome contributions from the community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)

## 📜 Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## 🤝 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/rayani2001/ai-hotel-receptionist/issues)
2. If not, create a new issue with:
   - **Clear title and description**
   - **Steps to reproduce** the bug
   - **Expected vs actual behavior**
   - **System information** (OS, Python version, browser, etc.)
   - **Screenshots** if applicable

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Windows 10]
 - Python Version: [e.g. 3.9.7]
 - Browser: [e.g. Chrome 96]
```

### Suggesting Features

1. Check existing [Issues](https://github.com/rayani2001/ai-hotel-receptionist/issues) for similar suggestions
2. Create a new issue with:
   - **Clear description** of the feature
   - **Use cases and benefits**
   - **Possible implementation** approach
   - **Alternative solutions** considered

**Feature Request Template:**
```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context or screenshots.
```

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Write clear, concise commit messages
   - Follow the code style guidelines
   - Add tests for new features
   - Update documentation
4. **Test your changes**:
   ```bash
   pytest tests/
   ```
5. **Commit** your changes:
   ```bash
   git commit -m 'Add some amazing feature'
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** on GitHub

**Pull Request Template:**
```markdown
**Description**
Brief description of changes.

**Type of Change**
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

**Testing**
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated documentation

**Checklist**
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Commented complex code
- [ ] Documentation updated
```

## 🛠️ Development Setup

### 1. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/ai-hotel-receptionist.git
cd ai-hotel-receptionist
```

### 2. Add Upstream Remote

```bash
git remote add upstream https://github.com/rayani2001/ai-hotel-receptionist.git
```

### 3. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 6. Make Changes and Test

```bash
# Run the application
python main.py

# Run tests
pytest tests/

# Check code style
flake8 .
```

### 7. Keep Your Fork Updated

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

## 🎨 Code Style

### Python Code Style

We follow **PEP 8** guidelines:

- **Indentation**: 4 spaces
- **Line length**: Maximum 100 characters
- **Imports**: Grouped and sorted
- **Naming conventions**:
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_CASE`

### Documentation

- Add **docstrings** to all functions and classes
- Use **type hints** where appropriate
- Keep comments clear and concise

**Example:**

```python
def process_message(user_message: str, session_id: str) -> Dict:
    """
    Process user message and generate response.
    
    Args:
        user_message: The user's input message
        session_id: Unique session identifier
        
    Returns:
        Dictionary containing response and metadata
    """
    # Implementation here
    pass
```

### Commit Messages

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**
```
feat(dialogue): add support for German language

Added German language support with translations for all
common intents and responses.

Closes #42
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=. tests/

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v tests/
```

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names

**Example:**

```python
def test_detect_intent_room_inquiry():
    """Test intent detection for room inquiry"""
    dm = DialogueManager()
    result = dm.detect_intent("What room types do you have?", "en")
    assert result["intent"] == "room_inquiry"
    assert result["confidence"] > 0.8
```

## 📝 Documentation

### Updating Documentation

When adding new features:
1. Update relevant `.py` file docstrings
2. Update `README.md` if needed
3. Add examples to documentation
4. Update API documentation

### Documentation Style

- Use **Markdown** for documentation files
- Include **code examples** where helpful
- Add **screenshots** for UI changes
- Keep language clear and simple

## ❓ Questions?

If you have questions:
- Check existing [Issues](https://github.com/rayani2001/ai-hotel-receptionist/issues)
- Open a new issue with `question` label
- Start a [Discussion](https://github.com/rayani2001/ai-hotel-receptionist/discussions)
- Email: fminoli92@gmail.com

## 🎉 Recognition

Contributors will be recognized in:
- Project README
- Release notes
- Contributors page

Thank you for contributing! 🙏

---

**Project Maintainer**: Rayani ([@rayani2001](https://github.com/rayani2001))  
**Contact**: fminoli92@gmail.com
