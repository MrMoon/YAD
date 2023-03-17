import typer
import codeParser  
import commentController 

app = typer.Typer()

@app.command("isolateFunction")
def isolateFunction(source: str  = typer.Argument(...), destination: str  = typer.Argument(...), prototype: str  = typer.Argument(...)):
    """
    This tool will isolate out a function 
    """
    findFunction = codeParser.findLocationFunction(source, prototype )
    if findFunction == None or findFunction == []:
        print("Warning: Function doesn't exist in " + source +" file")
        return 
    sz = len(findFunction)
    retrievedAST = findFunction[sz-1][1]
    pointer = findFunction[sz-1][0]
    AST = codeParser.positions(pointer, retrievedAST)
    
    start_line = AST[0]
    end_line = AST[2]
    type = AST[4]
    
    # Open the source file and read its contents
    with open(source, "r") as source_file:
        lines = source_file.readlines() 
    if type == 5:
        className = prototype.split('::')[0].split(' ')[1]
        functionName = prototype.split('::')[1].split('(')[0]
        retrieved = codeParser.findLocationClass(destination, className)
        AST = codeParser.positions(3, retrieved[0])
        if AST == []:
            return 
        class_end = AST[2]
    commentController.CommentOutFunction(destination, prototype)
    # Extract the lines you want to copy
    implementation = lines[start_line - 1:end_line]

    # Open the destination file and insert the copied lines at the appropriate position
    with open(destination, "r") as destination_file:
        lines = destination_file.readlines()
        if type == 3:
            # Insert the copied lines at the appropriate position
            lines = [prototype +";\n"]+ lines[0:] + ['\n'] + implementation
        else:
            lines = lines[0: class_end-1] + [prototype.split(className)[0] + prototype.split("::")[1] +";\n"] + lines[class_end-1:]+['\n'] + [implementation[0].split(functionName)[0] + className+"::" + functionName + implementation[0].split(functionName)[1]] + implementation[1:]
            
    # Write the modified lines to the destination file
    with open(destination, "w") as destination_file:
        destination_file.writelines(lines)

@app.command("isolateClass")
def isolateClass(source: str  = typer.Argument(...), destination: str  = typer.Argument(...), prototype: str  = typer.Argument(...)):
    findClass = codeParser.findLocationClass(source, prototype)
    AST = codeParser.positions(3, findClass[0])
    if AST == None:
        print("EROOR")
        return 
    start_line = AST[0]
    end_line = AST[2]
    with open(source, "r") as source_file:
        lines = source_file.readlines()
    # Extract the lines you want to copy
    classdef = lines[start_line - 1:end_line]
    implementation = []
    findClass.pop(0)
    for function in findClass:
        AST = codeParser.positions(5, function)
        start_line = AST[0]
        end_line = AST[2]
        implementation += lines[start_line - 1:end_line]        
        
    with open(destination, "r") as destination_file:
        lines = destination_file.readlines()
        # Insert the copied lines at the appropriate position
        lines = classdef + lines + implementation
    with open(destination, "w") as destination_file:
        destination_file.writelines(lines)
            

if __name__ == "__main__":
    app()