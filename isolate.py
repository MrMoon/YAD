import typer
import codeParser  
import newCommenter
import json
import clang.cindex

app = typer.Typer()

@app.command("isolateFunction")
def isolateFunction(source: str  = typer.Argument(...), destination: str  = typer.Argument(...), prototype: str  = typer.Argument(...)):
    """
    This tool will isolate out a function 
    """
    findFunction = codeParser.positions(source,"Function", prototype)
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
    newCommenter.CommentOutFunction(destination, prototype)
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
    
    position = codeParser.positions(source, "class", prototype)
    print(position)
    if position == []:
        print("Class not found in " + source)
        return
    
    with open(source, "r") as source_file:
        lines = source_file.readlines()
        
    n = len(position)
    implementation = []
    class_to_insert = []
    things = []
    for i in range(0, int(n), 3):
        start_line = position[i]
        end_line = position[i+1]
        type= position[i+2]
        # if type == "class":
        #     class_to_insert = lines[start_line-1: end_line]
        # if type == "member_function_outside":
        #     implementation += lines[start_line - 1:end_line]
        # else:
        things += lines[start_line - 1:end_line]
            
    newCommenter.CommentOutClass(destination, prototype)
    
    beginning = 0 #codeParser.positions(destination, "start", "")
    with open(destination, "r") as destination_file:
        lines = destination_file.readlines()
        lines =  lines[0: beginning-1]  + class_to_insert + lines[beginning-1: ]+ ["\n"] + implementation + ["\n"] + things
    with open(destination, "w") as destination_file:
        destination_file.writelines(lines)

@app.command("trythis")
def trythis():
    codeParser.newposition("testfiles\\test.cpp", "class", "class Animal")

if __name__ == "__main__":
    app()