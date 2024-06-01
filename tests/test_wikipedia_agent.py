import subprocess

def test_list_of_nobel_laureates():
    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="List_of_Nobel_laureates\nList the Nobel laureates from 1999.\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: Nobel laureates from 1999 include" in result.stdout

def test_synthetic_diamond():
    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="Synthetic_diamond\nWhat is a BARS apparatus?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: A BARS apparatus is" in result.stdout

def test_ecuadorian_security_crisis():
    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="Ecuadorian_security_crisis\nTell me about what is going on the Ecuadorian security crisis?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: The Ecuadorian security crisis" in result.stdout
    assert "AI: criminal groups in Ecuador" in result.stdout
    assert "AI: Choneros" in result.stdout
