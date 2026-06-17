# AGENTS.md

## Python environment

This project uses a local virtual environment managed through the Makefile and stored in `venv/`.

Agents must always use the project virtual environment and never rely on the system Python installation.

---

## Environment management

Create the environment:

```bash
make venv
```

Upgrade/update the environment and dependencies:

```bash
make venv_upgrade
```

Before running Python commands, ensure `.venv/` exists.  
If it does not exist, create it with:

```bash
make venv
```

---

## Python execution

Always use the virtual environment executables directly:

```bash
.venv/bin/python
.venv/bin/pip
```

Examples:

```bash
.venv/bin/python main.py
.venv/bin/python -m pytest
```

---

## Dependency management

This project uses `requirements.txt`.

When installing a new package:

```bash
.venv/bin/pip install <package>
```

the agent must also update `requirements.txt`:

```bash
.venv/bin/pip freeze > requirements.txt
```

Never install packages globally.

---

## Agent rules

The agent must:

1. Ensure `.venv/` exists before executing Python code.
2. Use `.venv/bin/python` for Python execution.
3. Use `.venv/bin/pip` for package installation.
4. Update `requirements.txt` whenever dependencies change.
5. Prefer Makefile targets when available.
6. Never use the system Python environment or global package installation.