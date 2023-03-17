import re
import os



def findLocationFunction(source: str, fnc: str):
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
    lst =[]
    for retrieveOne in retrieveAll:
        findClangParameters = retrieveOne.split('\'')
        presentParameters = findClangParameters[len(findClangParameters)-2]
        if inputtedParameters != presentParameters:
            continue
        
        retrieveOne = retrieveOne.split(':')
        pointer = 3
        if isFunctionInClass:
            pointer = 5
        lst += [ [pointer, retrieveOne] ]
    return lst



def findLocationClass(source: str, cls: str):
    #Checking if user input is correct and matches class prototype
    cls.strip()
    validClassNamePattern = r'^class [a-zA-Z_][a-zA-Z0-9_]*(\s*::\s*[a-zA-Z_][a-zA-Z0-9_]*)*$'
    if re.match(validClassNamePattern, cls) is None:
        print("Class name is not valid syntactically.")
        return
    
    cls = cls[5:]
    clsFix = cls.split("::")
    cls = ""
    for clsPart in clsFix:
        cls += clsPart.strip() + "::"
    cls=cls[:len(cls)-2]

    #System call to get ast dump of anything containing the string inputted in cls (cls stands for class)
    systemCall = "clang-check -ast-dump -ast-dump-filter={} {} -- 2>&1".format(cls, source)
    retrieveSystemCall = os.popen(systemCall).read()
    if retrieveSystemCall == "":
        print("Class not found.")
        return

    #Filter the code using regex to keep what is important
    regex = r"Dumping {}:\nCXXRecordDecl.*?\n".format(cls)
    retrieveAll = re.findall(regex, retrieveSystemCall, re.MULTILINE)

    clsList = []

    for retrieveOne in retrieveAll:
        checkDump = retrieveOne.split("CXXRecordDecl")
        if checkDump[0] != ("Dumping " + cls + ":\n"):
            continue
        
        checkDump = checkDump[1].split(':')

        clsList += [ [2, checkDump] ]    

    #Saves informtion about the implementations of functions outside the class
    regex = r"Dumping {}::.*?:\nCXXMethodDecl.*?\n".format(cls)
    retrieveAll = re.findall(regex, retrieveSystemCall, re.MULTILINE)
    for retrieveOne in retrieveAll:        
        checkDump = retrieveOne.split("CXXMethodDecl")[1].split(':')
        clsList += [ [2, checkDump] ]
        
    #Saves informtion about the constructor and copy constructors outside the class
    regex = r"Dumping {}::.*?:\nCXXConstructorDecl.*?\n".format(cls)
    retrieveAll = re.findall(regex, retrieveSystemCall, re.MULTILINE)
    for retrieveOne in retrieveAll:        
        checkDump = retrieveOne.split("CXXConstructorDecl")[1].split(':')
        clsList += [ [2, checkDump] ]

    #Saves informtion about the destructors outside the class
    regex = r"Dumping {}::.*?:\nCXXDestructorDecl.*?\n".format(cls)
    retrieveAll = re.findall(regex, retrieveSystemCall, re.MULTILINE)
    for retrieveOne in retrieveAll:        
        checkDump = retrieveOne.split("CXXDestructorDecl")[1].split(':')
        clsList += [ [2, checkDump] ]

    #Returuns informtion
    return clsList 

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
    position = [rowStart, colStart, rowEnd, colEnd, pointer]
    return position
        
