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
    findFunction = codeParser.positions(source,"function", prototype)
    if findFunction == None or findFunction == []:
        print("Warning: Function doesn't exist in " + source +" file")
        return 
    
    # Open the source file and read its contents
    with open(source, "r") as source_file:
        lines = source_file.readlines() 
         
    #commenting out the function in destination file 
    newCommenter.CommentOutFunction(destination, prototype)
    
    #check if its a member function and parent class exists in destination file 
    if findFunction[2] == "member_function" or findFunction[2] == "template_member_function":
        print(prototype)
        if len(prototype.split("::")) == 1:
            return
        parent_class = prototype.split("::")[0].split(" ")[-1]
        print(parent_class)
        findClass = codeParser.positions(destination, "class", "class " + parent_class)
        if findClass == []:
            print("Warning: Parent Class doesn't exist in " +destination +" file")
            return 
        class_end = findClass[1]
        #fixing protoype
        prototype = prototype.split(parent_class)[0] + prototype.split(parent_class)[1]
        prototype = prototype.split("::")[0] + prototype.split("::")[1]
        
    
    #incase of forward declaration or memebr functions implemented outside a class
    i=0
    if len(findFunction) > 3:
        i=3
    start_line = findFunction[i+0]
    end_line = findFunction[i+1]
    
    # Extract the lines you want to copy
    implementation = lines[start_line - 1:end_line]
    
    # Open the destination file and insert the copied lines at the appropriate position
    with open(destination, "r") as destination_file:
        lines = destination_file.readlines()
        
    if findFunction[2] == "function" or findFunction[2] == "template_function":
        lines = [prototype +";\n"]+ lines[0:] + ['\n'] + implementation  
        
    if findFunction[2] == "member_function" or findFunction[2] == "template_member_function":
        #if function implemented outside the class 
        if  i == 3:
            lines = lines[0: class_end-1] + [prototype + ";\n"] + lines[class_end-1: ] + implementation 
        #if function implemented inside the class
        else:
            lines = lines[0: class_end-1] + implementation + ["\n"] + lines[class_end-1: ]
       
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
    codeParser.positions("testfiles\\test.cpp", "class", "class Animal")

if __name__ == "__main__":
    app()