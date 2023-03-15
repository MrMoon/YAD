import typer
import codeParser  

app = typer.Typer()

@app.command("isolateFunction")
def isolateFunction(source: str  = typer.Argument(...), destination: str  = typer.Argument(...), prototype: str  = typer.Argument(...)):
    """
    This tool will isolate out a function 
    """
    findFunction = codeParser.findLocationFunction(source, prototype )
    retrievedAST = findFunction[1]
    pointer = findFunction[0]
    AST = codeParser.positions(pointer, retrievedAST)
    
    if AST == None:
        print("Warning: Function doesn't exist in source file")
        return 
    start_line = AST[0]
    end_line = AST[2]
    type = AST[4]
    
    # Open the source file and read its contents
    with open(source, "r") as source_file:
        lines = source_file.readlines()
        
    if type == 5:
        className = prototype.split('::')[0].split(' ')[1]
        functionName = prototype.split('::')[1].split('(')[0]
        AST = codeParser.findLocationClass(destination, className)
        if AST == None:
            return 
        class_start = AST[0]
        class_end = AST[2]
        # start_line = AST[5]
        # end_line = AST[7]

    # Extract the lines you want to copy
    implementation = lines[start_line - 1:end_line]

    # Open the destination file and insert the copied lines at the appropriate position
    with open(destination, "r") as destination_file:
        lines = destination_file.readlines()
        if type == 3:
            # Insert the copied lines at the appropriate position
            lines = [prototype +";\n"]+ lines[0:] + ['\n'] + implementation
        else:
            lines = lines[0: class_end-1] + [prototype.split(className)[0] + prototype.split("::")[1] +";\n"] + lines[class_end-1:]+['\n'] + [ implementation[0].split(functionName)[0] + className+"::" + functionName + implementation[0].split(functionName)[1]] + implementation[1:]
            

    # Write the modified lines to the destination file
    with open(destination, "w") as destination_file:
        destination_file.writelines(lines)

@app.command("isolateClass")
def isolateClass(source: str  = typer.Argument(...), destination: str  = typer.Argument(...), prototype: str  = typer.Argument(...)):
    return
    

if __name__ == "__main__":
    app()