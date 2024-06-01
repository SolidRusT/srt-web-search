import pytest
import subprocess

def test_list_of_nobel_laureates():
    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="List_of_Nobel_laureates\nList the Nobel laureates from 1999.\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: Fetched and processed Wikipedia page for title 'List_of_Nobel_laureates'" in result.stdout

    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="List_of_Nobel_laureates\nWhat were the prizes given to the winners?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: Fetched and processed Wikipedia page for title 'List_of_Nobel_laureates'" in result.stdout

def test_synthetic_diamond():
    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="Synthetic_diamond\nWhat is a BARS apparatus?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: Fetched and processed Wikipedia page for title 'Synthetic_diamond'" in result.stdout

def test_ecuadorian_security_crisis():
    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="Ecuadorian_security_crisis\nTell me about what is going on the Ecuadorian security crisis?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: Fetched and processed Wikipedia page for title 'Ecuadorian_security_crisis'" in result.stdout

    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="Ecuadorian_security_crisis\nWho are the criminal groups in Ecuador?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: Fetched and processed Wikipedia page for title 'Ecuadorian_security_crisis'" in result.stdout

    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="Ecuadorian_security_crisis\nWho are Choneros?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: Fetched and processed Wikipedia page for title 'Ecuadorian_security_crisis'" in result.stdout
