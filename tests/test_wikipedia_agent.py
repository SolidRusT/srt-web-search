import subprocess

def test_synthetic_diamond():
    result = subprocess.run(
        ["python", "main.py", "--mode", "wikipedia", "--interface", "cli"],
        input="Synthetic_diamond\nWhat is a BARS apparatus?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "AI: A BARS apparatus is" in result.stdout
