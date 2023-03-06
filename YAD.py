import typer
import re

app = typer.Typer()

@app.command("extract")
def extract_comments(file: str  = typer.Argument(...), output: str  = typer.Argument(...)):
    """
    This is a test run for Comment Remover
    """
    with open(file, 'r') as f:
        contents = f.read()
    
    # Remove all comments from the input file
    contents = re.sub(r'\/\/.*?$|\/\*[\s\S]*?\*\/', '', contents, flags=re.MULTILINE)

    # Write the modified contents to the output file
    with open(output, 'w') as f:
        f.write(contents)

@app.command("test")
def test():
    print("hello")

if __name__ == "__main__":
    app()