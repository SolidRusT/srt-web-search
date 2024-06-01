import pytest
import subprocess


def test_list_of_nobel_laureates():
    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="List_of_Nobel_laureates\nList the Nobel laureates from 1999.\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "Nobel laureates from 1999" in result.stdout

    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="What were the prizes given to the winners?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "prizes given to the winners in 1999" in result.stdout


def test_synthetic_diamond():
    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="Synthetic_diamond\nWhat is a BARS apparatus?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "detailed explanation of a BARS apparatus" in result.stdout


def test_ecuadorian_security_crisis():
    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="Ecuadorian_security_crisis\nTell me about what is going on the Ecuadorian security crisis?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "overview of the current Ecuadorian security crisis" in result.stdout

    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="Who are the criminal groups in Ecuador?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "criminal groups in Ecuador" in result.stdout

    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="Who are Choneros?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "information about the Choneros group" in result.stdout
