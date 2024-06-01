import pytest
import subprocess

def test_simple_web_search():
    result = subprocess.run(
        ["python", "main.py", "--mode", "web_search", "--interface", "cli"],
        input="What is the capital of France?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: Paris" in result.stdout

def test_research_document_generation():
    result = subprocess.run(
        ["python", "main.py", "--mode", "web_search", "--interface", "cli"],
        input="Write a detailed report on the impact of climate change.\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: Detailed report on the impact of climate change" in result.stdout
