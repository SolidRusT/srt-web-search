import subprocess

def test_basic_interaction():
    result = subprocess.run(
        ["python", "main.py", "--mode", "chat", "--interface", "cli"],
        input="Hello, how are you?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "Hello" in result.stdout
    assert "how are you" in result.stdout.lower()

def test_complex_query():
    result = subprocess.run(
        ["python", "main.py", "--mode", "chat", "--interface", "cli"],
        input="Can you explain the theory of relativity?\nexit\n",
        text=True,
        capture_output=True,
    )
    assert "theory of relativity" in result.stdout.lower()
    assert "albert einstein" in result.stdout.lower()
