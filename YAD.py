import typer
import re
import os



app = typer.Typer()

#This function is responsible for putting classes and functinos into comment blocks using /**/
def commentMaker(pointer: int, retrievedAST: str, source: str):
    #Find where the classes or functions start
    rowStart = int(retrievedAST[pointer])
    colStart = int(retrievedAST[pointer+1].split(',')[0])
    if retrievedAST[pointer+1].split(',')[1] == " col":
        rowEnd = int(retrievedAST[pointer])
        colEnd = int(retrievedAST[pointer+2].split('>')[0])
    else:
        rowEnd = int(retrievedAST[pointer+2])
        colEnd = int(retrievedAST[pointer+3].split('>')[0])

    #Get all the code to edit it
    with open(source, 'r') as f:
        lines = f.readlines()
    
    #Comment out class
    lines[rowStart-1] = lines[rowStart - 1][:colStart-1] + "/*" + lines[rowStart - 1][colStart-1:]

    if rowStart == rowEnd:
        colEnd += 2

    lines[rowEnd-1] = lines[rowEnd - 1][:colEnd+1] + "*/" + lines[rowEnd - 1][colEnd+1:]
    
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
    #System call to get ast dump of anything containing the string inputted in cls (cls stands for class)
    systemCall = "clang-check -ast-dump -ast-dump-filter={} test.cpp --".format(cls)
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
    #fnc stands for function
    functionName = fnc.split('(')[0].split(' ')[1]

    #System call to get ast dump of anything containing the string in funcName (funcName stands for function name)
    systemCall = "clang-check -ast-dump -ast-dump-filter={} test.cpp --".format(functionName)
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
    unFilteredParameters = fnc.split('(')[1].split(',')
    inputtedParameters = fnc.split('(')[0].split(' ')[0]+" ("
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

        commentMaker(pointer, retrieveOne, source)


if __name__ == "__main__":
    app()
