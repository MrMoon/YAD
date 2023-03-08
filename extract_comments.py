import typer
import re
import os 


app = typer.Typer()

@app.command("extract")
def extract_comments(file: str):
    
    with open(file, "r") as f:
        source_code = f.read()
   
    pattern = r"/\*[\s\S]*?\*/|//.*"
    
    #Extract all comments from the input file
    comments = re.findall(pattern, source_code)
    
    #Create a text file and write the extracted comments into it
    file_name, file_path = os.path.splitext(file)
    output = "out"+file_name+".txt"
    with open(output, 'x') as f:
        for comment in comments:
            size = len(comment)
            if ( comment[1] == '*' ):
                f.write(comment[2:size-2].strip()+ "\n")
            else:
                f.write(comment[2:size-1].strip() + "\n")
     
        
@app.command("delete")
def extract_comments(file: str  = typer.Argument(...)):

    with open(file, "r") as f:
        source_code = f.read()
    
    pattern = r"\/\/.*?$|\/\*[\s\S]*?\*\/"
    
    #Remove all comments from the input file
    content = re.sub(pattern, '', source_code, flags=re.MULTILINE)
    
    #Create an output .cpp file and write the modified contents to it 
    output = "out"+file
    with open(output, 'x') as f:
        for line in content:
            f.write(line)
        
if __name__ == "__main__":
    app()

