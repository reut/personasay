# Contributing to PersonaSay

Thank you for your interest in contributing to PersonaSay! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/personasay/issues)
2. If not, create a new issue with:
 - Clear title and description
 - Steps to reproduce
 - Expected vs actual behavior
 - Environment details (OS, Python/Node version, deployment method)
 - Screenshots if applicable

### Suggesting Features

1. Check [Discussions](https://github.com/yourusername/personasay/discussions) for similar ideas
2. Create a new discussion or issue explaining:
 - The problem you're trying to solve
 - Your proposed solution
 - Any alternatives you've considered
 - How it benefits other users

### Code Contributions

#### Development Setup

1. **Fork the repository**
 ```bash
 git clone https://github.com/yourusername/personasay.git
 cd personasay
 ```

2. **Automated setup** (Recommended)
 ```bash
 ./setup.sh
 nano backend/.env # Add your OPENAI_API_KEY
 ```

 Or manually:
 
 **Backend:**
 ```bash
 cd backend
 python -m venv venv
 source venv/bin/activate
 pip install -r config/requirements.txt -r config/requirements-dev.txt
 cp config/config.env.example .env
 # Add your OPENAI_API_KEY to .env
 ```

 **Frontend:**
 ```bash
 cd frontend
 npm install
 ```

3. **Create a feature branch**
 ```bash
 git checkout -b feature/amazing-feature
 ```

4. **Start development servers**
 ```bash
 # Option 1: Using Make commands
 make dev-backend # Terminal 1
 make dev-frontend # Terminal 2
 
 # Option 2: Using Docker
 make docker-up
 
 # Option 3: Manually
 cd backend && source venv/bin/activate && python main.py
 cd frontend && npm run dev
 ```

#### Code Style

**Python (Backend)**
- Follow PEP 8
- Use type hints where appropriate
- Add docstrings to functions and classes
- Run linter: `flake8 app/`

**TypeScript/React (Frontend)**
- Use TypeScript for all new components
- Follow React best practices
- Use functional components with hooks
- Run linter: `npm run lint`

**Commits**
- Use conventional commits format:
 - `feat: add new persona selector`
 - `fix: resolve CORS issue`
 - `docs: update deployment guide`
 - `refactor: simplify chat logic`

#### Testing

**Quick way:**
```bash
make test # Runs backend tests + frontend type-check
```

**Manual way:**

**Backend Tests**
```bash
cd backend
source venv/bin/activate
pytest tests/ -v # Verbose output
```

**Frontend Type Check**
```bash
cd frontend
npm run type-check # TypeScript validation
```

> **Note:** Frontend unit/component tests are not yet implemented. The test command runs TypeScript type checking for now.

#### Pull Request Process

1. **Update your branch**
 ```bash
 git fetch origin
 git rebase origin/main
 ```

2. **Test thoroughly**
 - Run all tests
 - Test manually in both dev and production modes
 - Check that health endpoints work

3. **Update documentation**
 - Update README.md if adding features
 - Add inline comments for complex logic
 - Update API documentation if changing endpoints

4. **Create Pull Request**
 - Write a clear title and description
 - Reference related issues
 - Add screenshots/videos for UI changes
 - Request review from maintainers

5. **Address feedback**
 - Respond to review comments
 - Make requested changes
 - Push updates to your branch

## Development Guidelines

### Adding a New Persona

1. Create JSON file in `backend/app/personas/`:
 ```json
 {
 "id": "unique_id",
 "name": "Name",
 "role": "Job Title",
 "company": "Company Type",
 "empathy_map": {
 "think_and_feel": "...",
 "hear": "...",
 "see": "...",
 "say_and_do": "...",
 "pain": "...",
 "gain": "..."
 }
 }
 ```

2. Add avatar image: `frontend/public/avatars/name.png`

3. Test with multiple conversations

### Adding a New API Endpoint

1. Create route in `backend/app/routes/`
2. Add request/response models in `backend/app/models.py`
3. Update health check if it affects system health
4. Add tests in `backend/tests/`
5. Document in code comments

### Frontend Component Guidelines

1. Place in appropriate directory:
 - `src/components/` - Reusable UI components
 - `src/pages/` - Page-level components
 - `src/hooks/` - Custom React hooks

2. Use TypeScript interfaces for props
3. Add JSDoc comments for complex components
4. Keep components focused (single responsibility)

## Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead, email: security@yourcompany.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Guidelines

- Never commit API keys or secrets
- Validate all user input
- Use environment variables for configuration
- Follow OWASP best practices
- Keep dependencies updated

## Useful Commands

PersonaSay provides convenient Make commands for development:

```bash
make help # Show all available commands
make setup # Run automated setup script
make dev-backend # Start backend server
make dev-frontend # Start frontend dev server 
make test # Run all tests
make clean # Clean build artifacts
make docker-build # Build Docker images
make docker-up # Start with Docker Compose
make docker-down # Stop Docker Compose
```

---

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unprofessional conduct

## Development Priorities

Current focus areas (good first contributions):

1. **Testing**: Increase test coverage
2. **Documentation**: Improve inline comments and guides
3. **Personas**: Add personas for different industries
4. **UI/UX**: Improve mobile responsiveness
5. **Performance**: Optimize API calls and caching

## Getting Help

- **Questions**: GitHub Discussions
- **Real-time chat**: Discord (if available)
- **Documentation**: README.md and inline comments

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

---

Thank you for contributing to PersonaSay! 

