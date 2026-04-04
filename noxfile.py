"""Nox Sessions."""

# Copyright 2024 Birdseye Global Inc.
import os

from nox_poetry import Session, session


@session(python=["3.13.5"])
def ruff(session: Session) -> None:
    """Run the linter."""
    session.run_always("poetry", "install", external=True)
    session.run("ruff", "format", ".", "--config", "./pyproject.toml")
    session.run("ruff", "check", "--fix", ".", "--config", "./pyproject.toml")
    session.run("ruff", "format", "--check", ".", "--config", "./pyproject.toml")
    session.run("ruff", "check", ".", "--config", "./pyproject.toml")


@session()
def prettier(session: Session) -> None:
    """Run the prettier linter."""
    session.run(
        "npx",
        "prettier",
        "--config",
        "../prettier.config.js",
        "--ignore-path",
        "../.gitignore",
        "--write",
        ".",
        external=True,
    )
    session.run(
        "npx",
        "prettier",
        "--config",
        "../prettier.config.js",
        "--ignore-path",
        "../.gitignore",
        "--check",
        ".",
        external=True,
    )


@session(python=["3.13.5"])
def mypy(session: Session) -> None:
    """Run the type checker."""
    session.run_always("poetry", "install", external=True)
    session.run(
        "mypy",
        "--config-file=./pyproject.toml",
        "--html-report=./htmlmypy",
        "app",
    )


@session(python=["3.13.5"])
def test(session: Session) -> None:
    """Run the unit test suite."""
    session.run_always("poetry", "install", external=True)
    session.run(
        "py.test",
        "-vvv",
        "--tb=native",
        "--timeout=300",
        "--cov=app",
        "--cov-report=term",
        "--cov-report=html",
        os.path.join("tests", "".join(session.posargs)),
    )
