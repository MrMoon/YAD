import typer
import codeParser  
import commentController 

app = typer.Typer()

@app.command("isolateFunction")
def isolateFunction(source: str  = typer.Argument(...), destination: str  = typer.Argument(...), prototype: str  = typer.Argument(...)):
    """
    This tool will isolate out a function 
    """
    findFunction = codeParser.findLocationFunction(source, prototype)
    if findFunction == None or findFunction == []:
        print("Warning: Function doesn't exist in " + source +" file")
        return 
    sz = len(findFunction)
    mx =0
    for func in findFunction:
        if len(func[1]) > mx:
            mx = len(func[1])
            imp = func
            
    retrievedAST = imp[1]
    pointer = imp[0]
    AST = codeParser.positions(pointer, retrievedAST, False)
    
    start_line = AST[0]
    end_line = AST[2]
    classFunc = prototype.split("::")
    type = len(classFunc)
    
    # Open the source file and read its contents
    with open(source, "r") as source_file:
        lines = source_file.readlines() 
        
    if type == 2:
        className = prototype.split('::')[0].split(' ')[1]
        functionName = prototype.split('::')[1].split('(')[0]
        className = "class " + className
        retrieved = codeParser.findLocationClass(destination, className)
        if retrieved == None:
            print ("Error: " + className + " doesn't exist in " + destination)
            return
        AST = codeParser.positions(retrieved[0][0], retrieved[0][1], False)
        if AST == []:
            return 
        class_end = AST[2]
    commentController.CommentOutFunction(destination, prototype)
    # Extract the lines you want to copy
    implementation = lines[start_line - 1:end_line]

    # Open the destination file and insert the copied lines at the appropriate position
    with open(destination, "r") as destination_file:
        lines = destination_file.readlines()
        if type == 1:
            # Insert the copied lines at the appropriate position
            lines = [prototype +";\n"]+ lines[0:] + ['\n'] + implementation
        else:
            lines = lines[0: class_end-1] + [prototype.split(className)[0] +";\n"] + lines[class_end-1:]+['\n'] + [implementation[0].split(functionName)[0] + functionName + implementation[0].split(functionName)[1]] + implementation[1:]
            
    # Write the modified lines to the destination file
    with open(destination, "w") as destination_file:
        destination_file.writelines(lines)

@app.command("isolateClass")
def isolateClass(source: str  = typer.Argument(...), destination: str  = typer.Argument(...), prototype: str  = typer.Argument(...)):
    # className = "class " + prototype
    findClass = codeParser.findLocationClass(source, prototype)
    if findClass == None:
        print("Class not found in " + source)
        return
    AST = codeParser.positions(findClass[0][0], findClass[0][1], False)
    if AST == None:
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
        AST = codeParser.positions(function[0], function[1], False)
        start_line = AST[0]
        end_line = AST[2]
        implementation += lines[start_line - 1:end_line]        

    commentController.CommentOutClass(destination, prototype)
    
    with open(destination, "r") as destination_file:
        lines = destination_file.readlines()
        # Insert the copied lines at the appropriate position
        lines = classdef + lines + implementation
    with open(destination, "w") as destination_file:
        destination_file.writelines(lines)
            

if __name__ == "__main__":
    app()