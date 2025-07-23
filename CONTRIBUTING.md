# 🤝 Contributing to Trading Agent with MCPs

Thank you for your interest in contributing to the Trading Agent with MCPs project! We welcome contributions from developers of all skill levels.

## 📋 Table of Contents

- [🚀 Quick Start for Contributors](#-quick-start-for-contributors)
- [🔧 Development Setup](#-development-setup)
- [📝 Contribution Guidelines](#-contribution-guidelines)
- [🧪 Testing Guidelines](#-testing-guidelines)
- [📖 Documentation Guidelines](#-documentation-guidelines)
- [🎯 Areas for Contribution](#-areas-for-contribution)
- [🐛 Bug Reports](#-bug-reports)
- [💡 Feature Requests](#-feature-requests)
- [📜 Code Style](#-code-style)
- [🔄 Pull Request Process](#-pull-request-process)

---

## 🚀 Quick Start for Contributors

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/Trading-Agent-with-MCPs.git
cd Trading-Agent-with-MCPs

# 3. Set up development environment
cp .env.example .env
# Edit .env with your API keys

# 4. Install dependencies
uv sync

# 5. Create a feature branch
git checkout -b feature/your-amazing-feature

# 6. Make your changes and test
uv run python -m pytest  # Run tests
uv run python app.py     # Test the app

# 7. Commit and push
git commit -m "feat: add amazing new feature"
git push origin feature/your-amazing-feature

# 8. Create a Pull Request on GitHub
```

---

## 🔧 Development Setup

### Prerequisites

- **Python 3.12+**
- **UV Package Manager**
- **Git**
- **API Keys** (see `.env.example`)

### Local Development Environment

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/YOUR-USERNAME/Trading-Agent-with-MCPs.git
cd Trading-Agent-with-MCPs

# Environment setup
cp .env.example .env
# Add your API keys to .env

# Install dependencies
uv sync

# Install pre-commit hooks (optional but recommended)
uv run pre-commit install
```

### Running the Development Environment

```bash
# Terminal 1: Start the web dashboard
uv run python app.py

# Terminal 2: Start the trading engine
uv run python trading_floor.py

# Terminal 3: Run tests (optional)
uv run python -m pytest --watch
```

---

## 📝 Contribution Guidelines

### 🎯 Types of Contributions

We welcome several types of contributions:

1. **🐛 Bug Fixes** - Fix existing issues
2. **✨ New Features** - Add new functionality
3. **📖 Documentation** - Improve docs and guides
4. **🧪 Tests** - Add or improve test coverage
5. **🎨 UI/UX** - Enhance the dashboard experience
6. **⚡ Performance** - Optimize system performance
7. **🔌 Integrations** - Add new API integrations

### 🏷️ Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```bash
# Format
<type>[optional scope]: <description>

# Examples
feat: add new trading strategy for crypto agents
fix: resolve portfolio calculation bug
docs: update installation guide
test: add unit tests for account management
style: format code with black
refactor: optimize MCP server communication
perf: improve real-time update performance
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `style`: Code formatting
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `ci`: CI/CD changes

---

## 🧪 Testing Guidelines

### Running Tests

```bash
# Run all tests
uv run python -m pytest

# Run specific test file
uv run python -m pytest tests/test_accounts.py

# Run with coverage
uv run python -m pytest --cov=. --cov-report=html

# Run tests in watch mode during development
uv run python -m pytest --watch
```

### Writing Tests

We use **pytest** for testing. Here's the structure:

```
tests/
├── test_accounts.py      # Account management tests
├── test_traders.py       # AI agent tests
├── test_mcp_servers.py   # MCP server tests
├── test_database.py      # Database tests
├── test_app.py          # UI tests
└── fixtures/            # Test data and fixtures
```

**Example Test:**

```python
import pytest
from accounts import Account

def test_account_creation():
    """Test creating a new trading account."""
    account = Account.create("test_trader", initial_balance=10000)
    assert account.balance == 10000
    assert account.name == "test_trader"
    assert len(account.holdings) == 0

def test_buy_shares():
    """Test buying shares updates balance and holdings."""
    account = Account.create("test_trader", initial_balance=10000)
    account.buy_shares("AAPL", 10, 150.0)
    
    assert account.balance == 8500  # 10000 - (10 * 150)
    assert account.holdings["AAPL"] == 10
```

### Test Categories

1. **Unit Tests** - Test individual functions/classes
2. **Integration Tests** - Test MCP server communication
3. **UI Tests** - Test Gradio interface functionality
4. **End-to-End Tests** - Test complete trading workflows

---

## 📖 Documentation Guidelines

### Writing Documentation

- Use clear, concise language
- Include code examples where helpful
- Add emojis for better readability
- Update relevant sections when adding features

### Documentation Structure

```
docs/
├── architecture.md      # System architecture details
├── api.md              # API reference
├── strategies.md       # Trading strategy documentation
├── mcp.md             # MCP server development guide
├── development.md     # Development setup guide
├── testing.md         # Testing guide
├── deployment.md      # Deployment guide
├── faq.md            # Frequently asked questions
└── troubleshooting.md # Common issues and solutions
```

### Updating Documentation

When contributing:

1. **Update relevant documentation** for new features
2. **Add code examples** for new APIs
3. **Update the README** if changing core functionality
4. **Add FAQ entries** for common questions

---

## 🎯 Areas for Contribution

### 🤖 AI Agent Development

**Easy:**
- Add new trading personality templates
- Improve existing agent prompts
- Add new risk management rules

**Medium:**
- Implement new decision-making algorithms
- Add portfolio optimization strategies
- Create agent performance analytics

**Hard:**
- Develop multi-agent coordination
- Implement reinforcement learning
- Add sentiment analysis integration

### 📊 MCP Server Development

**Easy:**
- Add new technical indicators
- Improve error handling
- Add data validation

**Medium:**
- Create new MCP servers (e.g., options, forex)
- Add real-time data streaming
- Implement caching strategies

**Hard:**
- Build distributed MCP architecture
- Add machine learning models
- Implement advanced risk analytics

### 🎨 UI/UX Improvements

**Easy:**
- Add new chart types
- Improve color schemes
- Add mobile responsiveness

**Medium:**
- Create interactive trading controls
- Add portfolio analytics dashboard
- Implement real-time notifications

**Hard:**
- Build advanced charting library
- Add 3D visualizations
- Implement custom trading interface

### 🔌 API Integrations

**Easy:**
- Add new data providers
- Improve error handling
- Add rate limiting

**Medium:**
- Integrate social media sentiment
- Add news aggregation
- Implement webhook support

**Hard:**
- Build real-time options data
- Add institutional data feeds
- Implement blockchain integration

---

## 🐛 Bug Reports

When reporting bugs, please include:

### 🔍 Bug Report Template

```markdown
## 🐛 Bug Description
A clear description of what the bug is.

## 🔄 Steps to Reproduce
1. Go to...
2. Click on...
3. See error...

## 💭 Expected Behavior
What you expected to happen.

## 📷 Screenshots
If applicable, add screenshots.

## 🖥️ Environment
- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.12.1]
- UV version: [e.g., 0.1.0]
- Browser: [e.g., Chrome 120]

## 📋 Additional Context
Any other context about the problem.
```

### 🏷️ Bug Labels

- `bug` - Confirmed bug
- `critical` - System-breaking issue
- `ui` - User interface issue
- `performance` - Performance problem
- `documentation` - Documentation issue

---

## 💡 Feature Requests

### 🚀 Feature Request Template

```markdown
## 💡 Feature Description
A clear description of the feature you'd like.

## 🎯 Problem Statement
What problem does this solve?

## 💭 Proposed Solution
Describe your proposed solution.

## 🔄 Alternatives Considered
Other solutions you've considered.

## 📋 Additional Context
Any other context about the feature.
```

### 🏷️ Feature Labels

- `enhancement` - New feature
- `ui` - User interface improvement
- `api` - API enhancement
- `performance` - Performance improvement
- `documentation` - Documentation improvement

---

## 📜 Code Style

### Python Code Style

We follow **PEP 8** with some modifications:

```python
# Use black for formatting
uv run black .

# Use isort for import sorting
uv run isort .

# Use flake8 for linting
uv run flake8 .

# Use mypy for type checking (optional)
uv run mypy .
```

### Code Style Guidelines

1. **Line Length**: 88 characters (black default)
2. **Imports**: Use isort for consistent import ordering
3. **Type Hints**: Use where helpful, especially for public APIs
4. **Docstrings**: Use Google-style docstrings
5. **Variables**: Use descriptive names, avoid abbreviations

### Example Code Style

```python
"""Account management for trading agents.

This module provides functionality for managing trading accounts,
including balance tracking, position management, and transaction history.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Transaction:
    """Represents a single trading transaction."""
    
    symbol: str
    quantity: int
    price: Decimal
    timestamp: str
    transaction_type: str  # 'buy' or 'sell'


class Account:
    """Manages a single trading account.
    
    Args:
        name: The account holder's name
        initial_balance: Starting cash balance
        
    Example:
        >>> account = Account("warren", Decimal("10000"))
        >>> account.buy_shares("AAPL", 10, Decimal("150.0"))
        >>> print(account.balance)
        8500.0
    """
    
    def __init__(self, name: str, initial_balance: Decimal) -> None:
        self.name = name
        self.balance = initial_balance
        self.holdings: Dict[str, int] = {}
        self.transactions: List[Transaction] = []
    
    def buy_shares(
        self, 
        symbol: str, 
        quantity: int, 
        price: Decimal
    ) -> bool:
        """Buy shares if sufficient balance exists.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            quantity: Number of shares to buy
            price: Price per share
            
        Returns:
            True if purchase successful, False otherwise
        """
        total_cost = quantity * price
        
        if self.balance >= total_cost:
            self.balance -= total_cost
            self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
            
            # Record transaction
            transaction = Transaction(
                symbol=symbol,
                quantity=quantity,
                price=price,
                timestamp=self._get_current_timestamp(),
                transaction_type="buy"
            )
            self.transactions.append(transaction)
            
            return True
            
        return False
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for transaction recording."""
        # Implementation details...
        pass
```

---

## 🔄 Pull Request Process

### 1. **Preparation**

- Fork the repository
- Create a feature branch
- Make your changes
- Test thoroughly
- Update documentation

### 2. **Before Submitting**

```bash
# Run the full test suite
uv run python -m pytest

# Check code formatting
uv run black --check .
uv run isort --check-only .

# Run linting
uv run flake8 .

# Test the application
uv run python app.py  # Verify it starts correctly
```

### 3. **Pull Request Template**

```markdown
## 📝 Description
Brief description of changes made.

## 🎯 Type of Change
- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 📖 Documentation update
- [ ] 🧪 Test improvement
- [ ] 🎨 UI/UX improvement

## 🧪 Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## 📖 Documentation
- [ ] Documentation updated
- [ ] README updated (if needed)
- [ ] Code comments added

## 📋 Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] No merge conflicts
- [ ] Ready for review
```

### 4. **Review Process**

1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: Maintainers review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Get approval from maintainers
5. **Merge**: Your contribution gets merged!

### 5. **After Merge**

- Delete your feature branch
- Pull the latest changes
- Celebrate your contribution! 🎉

---

## 🎉 Recognition

Contributors will be recognized in several ways:

- **README Contributors Section**: Listed as a contributor
- **Release Notes**: Mentioned in release announcements
- **Discord Channel**: Special contributor role
- **Future Opportunities**: Invited to beta test new features

---

## 📞 Getting Help

If you need help with your contribution:

1. **Check existing issues** for similar problems
2. **Search documentation** for relevant information
3. **Ask in Discord** for real-time help
4. **Create an issue** for specific questions
5. **Email maintainers** for urgent matters

---

## 📜 Code of Conduct

Please note that this project is released with a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.

---

**Thank you for contributing to Trading Agent with MCPs! 🚀** 