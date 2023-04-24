import os
import typer
import re
import codeParser

app = typer.Typer()

#This function is responsible for putting classes and functinos into comment blocks using /**/
def commentMaker(source: str, type: str, name: str):
    
    #Find where the classes or functions start
    position = codeParser.positions(source, type , name)
    # return 
    if position == "Null" or position == []:
        print("NOT FOUND")
        return
    
    num = len(position)
    #Get all the code to edit it
    with open(source, 'r') as f:
        lines = f.readlines()
    
    for i in range(0, int(num), 3):
        lines[position[i]-1] = "//" + lines[position[i]-1]
        for line in range(position[i], position[i+1]):
            lines[line] = "//" + lines[line]
    
    #Write the modified code into the file.
    with open(source, 'w') as f:
        f.writelines(lines)
        


@app.command("commentOutClass")
def CommentOutClass(source: str  = typer.Argument(...), prototype: str  = typer.Argument(...)):
    """
    This tool will comment out a class implementation from a C++ file (equivalent to deleting the class).
    """    
    type = prototype.split(" ")[0]
    commentMaker(source, type , prototype)


@app.command("commentOutFunction")
def CommentOutFunction(source: str  = typer.Argument(...), prototype: str  = typer.Argument(...)):
    """
    This tool will comment out a function implementation from a C++ file using a function prototype (equivalent to deleting the function).
    """
    commentMaker(source, "function" , prototype)


if __name__ == "__main__":
    app()
