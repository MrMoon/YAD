import typer
import re
import os


app = typer.Typer()
def findLocationFunction(source: str, fnc: str, type: str ):
    validFunctionNamePattern = r'^\s*(?:(?:\w+\s+)*\w+\s*::\s*)?(?:\w+\s+)*\w+\s*\(\s*(?:\w+\s+\w+\s*(?:,\s*\w+\s+\w+\s*)*)?\)\s*$'
    if re.match(validFunctionNamePattern, fnc) is None:
        print("Function name is not valid syntactically.")
        return

    #fnc stands for function
    functionName = fnc.split('(')[0].split(' ')[1]

    #System call to get ast dump of anything containing the string in funcName (funcName stands for function name)
    systemCall = "clang-check -ast-dump -ast-dump-filter={} {} --".format(functionName, source)
    retrieveSystemCall = os.popen(systemCall).read()
    if retrieveSystemCall == "":
        print("Function not found.")
        return
    
    #Flag to check if function is part of class (cls = class)
    isFunctionInClass = False

    #Filter the code using regex to keep what is important (True condition of if statement means that it is only a function not a function inside a class)
    if len(functionName.split("::")) == 1:
        regex = r"Dumping {}:\nFunctionDecl.*?\n\|".format(functionName)
    else:
        regex = r"Dumping {}:\nCXXMethodDecl.*?\n".format(functionName)
        isFunctionInClass = True

    #Regex to get all of the functions that have the inputted name
    retrieveAll = re.findall(regex, retrieveSystemCall, re.MULTILINE)

    #Create the same syntax used in CLang to check if same prototype
    #The line below finds all the parameters of the function inputted by the user
    unFilteredParameters = fnc.split('(')[1].split(',')
    #The below line finds the return type of the function inputted by the user
    functionReturnType = fnc.split('(')[0].split(' ')[0].strip()+" ("
    #The below variable will be used to create the same syntax of a function protoype as CLang Ast Dump
    inputtedParameters = functionReturnType
    i = 0
    for parameter in unFilteredParameters:
        inputtedParameters += parameter.strip().split(" ")[0] + ", "
    inputtedParameters = inputtedParameters[:len(inputtedParameters)-2] + ")"

    #For each loop commenting out the functions
    for retrieveOne in retrieveAll:
        findClangParameters = retrieveOne.split('\'')
        presentParameters = findClangParameters[len(findClangParameters)-2]
        if inputtedParameters != presentParameters:
            continue
        
        retrieveOne = retrieveOne.split(':')

        pointer = 3
        if isFunctionInClass:
            pointer = 5

        if type == "commenting" :
            commentMaker(pointer, retrieveOne, source)
        else:
            AST = positions(3, retrieveOne)
            return AST
        
#This function is responsible for finding where classes or functions start and end (returns positions as a list)
def positions(pointer: int, retrievedAST: str):
    rowStart = int(retrievedAST[pointer])
    colStart = int(retrievedAST[pointer+1].split(',')[0])
    if retrievedAST[pointer+1].split(',')[1] == " col":
        rowEnd = int(retrievedAST[pointer])
        colEnd = int(retrievedAST[pointer+2].split('>')[0])
    else:
        rowEnd = int(retrievedAST[pointer+2])
        colEnd = int(retrievedAST[pointer+3].split('>')[0])
    position = [rowStart, colStart, rowEnd, colEnd]
    return position



#This function is responsible for putting classes and functinos into comment blocks using /**/
def commentMaker(pointer: int, retrievedAST: str, source: str):
    #Find where the classes or functions start
    position = positions(pointer, retrievedAST)

    #Get all the code to edit it
    with open(source, 'r') as f:
        lines = f.readlines()
    
    #Comment out class
    lines[position[0]-1] = lines[position[0] - 1][:position[1]-1] + "/*" + lines[position[0] - 1][position[1]-1:]

    if position[0] == position[2]:
        position[3] += 2

    lines[position[2]-1] = lines[position[2] - 1][:position[3]+1] + "*/" + lines[position[2] - 1][position[3]+1:]
    
    #Write the modified code into the file.
    with open(source, 'w') as f:
        f.writelines(lines)



@app.command("delete")
def delete_comments(input: str  = typer.Argument(...), output: str  = typer.Argument(...)):
    """
    This tool will delete all the comments from a C++ file and output the source code into the file of your choosing.
    """
    with open(input, 'r') as f:
        source = f.read()
    
    # Remove all comments from the input file
    source = re.sub(r'\/\/.*?$|\/\*[\s\S]*?\*\/', '', source, flags=re.MULTILINE)

    # Write the modified contents to the output file
    with open(output, 'w') as f:
        f.write(source)



@app.command("extract")
def extract_comments(input: str  = typer.Argument(...), output: str  = typer.Argument(...)):
    """
    This tool will extract all the comments from a C++ file and output the comments into the file of your choosing.
    """
    with open(input, 'r') as f:
        source = f.read()
    
    # Extract all comments from the input file
    comments = re.findall(r'\/\/.*?$|\/\*[\s\S]*?\*\/', source, flags=re.MULTILINE)

    # Write the comments to the output file
    with open(output, 'w') as f:
        for comment in comments:
            size = len(comment)
            if comment[0:2] == "/*":
                comment = comment[2:size-2].strip()
            else:
                comment = comment[2:size].strip()
            f.write(comment + "\n")



@app.command("header")
def extract_header(input: str  = typer.Argument(...), output: str  = typer.Argument(...)):
    """
    This tool will extract all header comments from a C++ file and output the comments into the file of your choosing.
    """
    with open(input, 'r') as f:
        source = f.read()

    header = re.findall(r'\/\/.*?$|\/\*[\s\S]*?\*\/', source, flags=re.MULTILINE)
    amount = 0

    while source[0:1] == '\n':
        source = source[1:]

    while source[0:2] == "//" or source[0:2] == "/*":
        source = re.sub(r'\/\/.*?$|\/\*[\s\S]*?\*\/', '',source, flags=re.MULTILINE, count=1)
        amount += 1
        while source[0:1] == '\n':
            source = source[1:]

    # Write the header comments to the output file
    with open(output, 'w') as f:
        for n in range(amount):
            comment = header[n]
            size = len(comment)
            if comment[0:2] == "/*":
                comment = comment[2:size-2]
            else:
                comment = comment[2:size]
            f.write(comment + "\n")



@app.command("commentOutClass")
def CommentOutClass(source: str  = typer.Argument(...), cls: str  = typer.Argument(...)):
    """
    This tool will comment out a class implementation from a C++ file (equivalent to deleting the class).
    """
    validClassNamePattern = r'^[A-Za-z_]\w*$'
    if re.match(validClassNamePattern, cls) is None:
        print("Class name is not valid syntactically.")
        return
    #System call to get ast dump of anything containing the string inputted in cls (cls stands for class)
    systemCall = "clang-check -ast-dump -ast-dump-filter={} {} --".format(cls, source)
    retrieveSystemCall = os.popen(systemCall).read()
    if retrieveSystemCall == "":
        print("Class not found.")
        return

    #Filter the code using regex to keep what is important
    regex = r"Dumping {}:\nCXXRecordDecl.*?\n(\|)".format(cls)
    retrieve = re.search(regex, retrieveSystemCall).group(0)
    if retrieve == "":
        print("Class not found.")
        return
    retrieve = retrieve.split(':')

    #Comment out the class
    commentMaker(3, retrieve, source)

    #Comment out implementations of functions outside the class
    regex = r"Dumping {}::.*?:\nCXXMethodDecl.*?\n".format(cls)
    retrieveAll = re.findall(regex, retrieveSystemCall, re.MULTILINE)

    for retrieveOne in retrieveAll:        
        retrieveOne = retrieveOne.split(':')
        commentMaker(5, retrieveOne, source)


@app.command("commentOutFunction")
def CommentOutFunction(source: str  = typer.Argument(...), fnc: str  = typer.Argument(...)):
    """
    This tool will comment out a function implementation from a C++ file using a function prototype (equivalent to deleting the function).
    """
    findLocationFunction(source, fnc, "commenting")

@app.command("isolate")
def isolate(source: str  = typer.Argument(...), destination: str = typer.Argument(...), fnc: str  = typer.Argument(...)):
    """
    This tool will isolate out a function 
    """
    AST = findLocationFunction(source, fnc, "isolate" )
     
    # Set the filenames of the source and destination files

    start_line = AST[0]
    end_line = AST[2]
    
    # Set the line number to insert the copied lines into
    insert_line = 10

    # Open the source file and read its contents
    with open(source, "r") as source_file:
        lines = source_file.readlines()

    # Extract the lines you want to copy
    lines_to_copy = lines[start_line - 1:end_line]

    # Open the destination file and insert the copied lines at the appropriate position
    with open(destination, "r") as destination_file:
        lines = destination_file.readlines()

        # Insert the copied lines at the appropriate position
        lines = "TEsting" + lines_to_copy + "BEYE"

    # Write the modified lines to the destination file
    with open(destination, "w") as destination_file:
        destination_file.writelines(lines)
    

if __name__ == "__main__":
    app()