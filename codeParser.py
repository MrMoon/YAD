import re
import os



def findLocationFunction(source: str, fnc: str):
    #Validate that the function prototype is correct
    # validFunctionNamePattern = r'^\s*(?:(?:\w+\s+)*\w+\s*::\s*)?(?:\w+\s+)*\w+\s*\(\s*(?:\w+\s+\w+\s*(?:,\s*\w+\s+\w+\s*)*)?\)\s*$'
    # if re.match(validFunctionNamePattern, fnc) is None:
    #     print("Function name is not valid syntactically.")
    #     return

    fnc = fnc.strip()
    #fnc stands for function
    functionNameHelper = fnc.split('(')[0].split(' ')
    functionName = functionNameHelper[len(functionNameHelper)-1]

    #System call to get ast dump of anything containing the string in funcName (funcName stands for function name)
    systemCall = "clang-check -ast-dump -ast-dump-filter={} {} -- 2>&1".format(functionName, source)
    retrieveSystemCall = os.popen(systemCall).read()
    if retrieveSystemCall == "":
        print("Function not found.")
        return
    
    #Flag to check if function is part of class (cls = class)
    isFunctionInClass = False
    #Flag to check if function is using template
    isFunctionTemplate = False
    #Flag to check if function is static
    isFunctionStatic = False

    #Filter the code using regex to keep what is important (True condition of if statement means that it is only a function not a function inside a class)
    if fnc[:8] == "template":
        isFunctionTemplate = True
    if fnc.find("static") != -1:
        isFunctionStatic = True

    if len(functionName.split("::")) == 1:
        if isFunctionTemplate:
            regex = r"Dumping {}:\nFunctionTemplateDecl.*?\n.*?\n.*?FunctionDecl.*?\n".format(functionName)
        else:
            regex = r"^Dumping {}:\nFunctionDecl.*\n+".format(functionName)
    else:
        if isFunctionTemplate:
            regex = r"Dumping {}:\nFunctionTemplateDecl.*?\n.*?\n.*?CXXMethodDecl.*?\n".format(functionName)
        else:
            regex = r"Dumping {}:\nCXXMethodDecl.*?".format(functionName)
        isFunctionInClass = True

    #Regex to get all of the functions that have the inputted name
    retrieveAll = re.findall(regex, retrieveSystemCall, re.MULTILINE)
    print(retrieveAll)
    #Create the same syntax used in CLang to check if same prototype by making a new file with the function prototype to run CLang on it
    f = open("temp" + source, "w")
    #if isFunctionTemplate and isFunctionInClass:
    if isFunctionStatic and isFunctionInClass:
        f.write("class " + fnc.split("::")[0].strip().split(" ")[-1] + "{\n" + fnc + ";\n};" + "\n" + fnc.replace("static","").strip() + "{}")
    elif isFunctionInClass:
        f.write("class " + fnc.split("::")[0].strip().split(" ")[-1] + "{\n" + fnc + ";\n};" + "\n" + fnc + "{}")
    else:
        f.write(fnc + "{}")
    f.close()
    systemCall = "clang-check -ast-dump -ast-dump-filter={} {} -- 2>&1".format(functionName, "temp" + source)
    retrieveNewCall = os.popen(systemCall).read()
    #os.remove("temp" + source)
    if isFunctionTemplate:
        if isFunctionInClass:
            regexNew = r"Dumping {}:\nFunctionTemplateDecl.*?\n.*?\n.*?CXXMethodDecl.*?\n".format(functionName)
        else:
            regexNew = r"Dumping {}:\nFunctionTemplateDecl.*?\n.*?\n.*?FunctionDecl.*?\n".format(functionName)
    else:
        if isFunctionInClass:
            regexNew = r"Dumping {}:\nCXXMethodDecl.*?\n".format(functionName)
        else:
            regexNew = r"Dumping {}:\nFunctionDecl.*?\n".format(functionName)
    retrieveNew = re.findall(regexNew, retrieveNewCall, re.MULTILINE)[0]

    #The line below finds all the parameters of the function inputted by the user
    inputtedParameters = retrieveNew.split('\'')
    lst =[]
    for retrieveOne in retrieveAll:
        presentParameters = retrieveOne.split('\'')
        if inputtedParameters[len(inputtedParameters)-2] != presentParameters[len(presentParameters)-2]:
            continue
        
        if isFunctionTemplate:
            retrieveOne = retrieveOne.split("FunctionTemplateDecl")[1].split(':')
        else:
            if isFunctionInClass:
                retrieveOne = retrieveOne.split("CXXMethodDecl")[1].split(':')
            else:
                retrieveOne = retrieveOne.split("FunctionDecl")[1].split(':')
        pointer = 2
        lst += [ [pointer, retrieveOne, isFunctionTemplate] ]
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

    #Template
    regex = r"Dumping {}::.*?:[\s\S]*CXXMethodDecl.*?\n".format(cls)
    retrieveAll = re.findall(regex, retrieveSystemCall, re.MULTILINE)
    for retrieveOne in retrieveAll:        
        checkDump = retrieveOne.split("FunctionTemplateDecl")[1].split(':')
        clsList += [ [2, checkDump, True] ]
        
    #Saves informtion about the constructor and copy constructors outside the class
    regex = r"Dumping {}::.*?:\nCXXConstructorDecl.*?\n".format(cls)
    retrieveAll = re.findall(regex, retrieveSystemCall, re.MULTILINE)
    for retrieveOne in retrieveAll:        
        checkDump = retrieveOne.split("CXXConstructorDecl")[1].split(':')
        clsList += [ [2, checkDump] ]

    #Saves informtion about the destructors outside the class
    regex = r"Dumping {}::.*?:\nCXXDestructorDecl.*?\n.*?\n".format(cls)
    retrieveAll = re.findall(regex, retrieveSystemCall, re.MULTILINE)
    for retrieveOne in retrieveAll:        
        checkDump = retrieveOne.split("CXXDestructorDecl")[1].split(':')
        clsList += [ [2, checkDump] ]

    #Returuns informtion
    return clsList 

#This function is responsible for finding where classes or functions start and end (returns positions as a list)   
def positions(pointer: int, retrievedAST: str, isTemplate: bool):
    rowStart = int(retrievedAST[pointer])
    colStart = int(retrievedAST[pointer+1].split(',')[0])
    if isTemplate:
        position = [rowStart, colStart, -1, -1]
        return position
    if retrievedAST[pointer+1].split(',')[1] == " col":
        rowEnd = int(retrievedAST[pointer])
        colEnd = int(retrievedAST[pointer+2].split('>')[0])
    else:
        rowEnd = int(retrievedAST[pointer+2])
        colEnd = int(retrievedAST[pointer+3].split('>')[0])
    position = [rowStart, colStart, rowEnd, colEnd, pointer]
    return position
        
