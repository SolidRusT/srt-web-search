import pytest
import subprocess

def test_basic_interaction():
    result = subprocess.run(
        ["python", "main.py", "--mode", "chat", "--interface", "cli"],
        input="Hello, how are you?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: I am an artificial intelligence" in result.stdout

def test_complex_query():
    result = subprocess.run(
        ["python", "main.py", "--mode", "chat", "--interface", "cli"],
        input="Can you explain the theory of relativity?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: The Theory of Relativity, proposed by Albert Einstein" in result.stdout
