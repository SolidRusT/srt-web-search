import pytest
import subprocess


def test_basic_interaction():
    result = subprocess.run(
        ["python", "main.py", "--mode", "chat", "--interface", "cli"],
        input="Hello, how are you?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "friendly greeting" in result.stdout


def test_complex_query():
    result = subprocess.run(
        ["python", "main.py", "--mode", "chat", "--interface", "cli"],
        input="Can you explain the theory of relativity?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "detailed explanation of the theory of relativity" in result.stdout
