import yaml
import orjson, json
import typer
import re
import codeParser
import newCommenter

app = typer.Typer()

#Returns everything in the scope the user defined
def scopeGetter(source:str, scope:str, ):
    #Checks if scope for function or class
        type = scope.split(" ")[0]
        if type != "class":
            type = "function"
        
        #Find where function or class is
        pos = codeParser.positions(source, type, scope)
        searchPos = []
        count = 0
        for p in pos:
            if count != 2:
                searchPos.append(p)
                count += 1
            else:
                count = 0

        #Get back only the lines in the specified scope
        with open(source, 'r') as f:
            source = f.readlines()
        scopeLines = []
        i = 0
        while i < len(searchPos):
            j = searchPos[i] - 1
            while j < searchPos[i+1]:
                scopeLines.append(source[j])
                j += 1
            i += 2

        source = '\n'.join(scopeLines)
        return source



@app.command("restrict")
def Restrict(source: str  = typer.Argument(..., help="The path of the .cpp or .h file the user wants restrictor to work on."),
             rules: str  = typer.Argument(..., help="The path of the YAML file containing user requiremnets")):
    with open(rules) as file:
        yamlFile = yaml.load(file, Loader=yaml.FullLoader)
    jsonFormat = json.dumps(yamlFile, indent=4)
    jsonData = json.loads(jsonFormat)

    #Used to remove comments from file, important for all restrictors (library only one that needs to work without it)
    newSource = "commentDeletedFileForRestrictor.cpp"
    newCommenter.delete_comments(source, newSource)

    #Following variables are needed to print everything in a readable manner for the user and for the loop to function correctly
    critCount = 1
    critOld = "start"
    critAns = True
    exactCount = 0
    compareCount = 0
    for criteria, critData in jsonData.items():
        #The following code is to print the findings of the code for each criteria in the YAML file
        if critOld != "start":
            if exactCount != 0 and compareCount != exactCount:
                critAns = critAns & False
            print(str(critCount) + ". " + critOld + " restriction result is " + str(critAns))
            critCount += 1
            critAns = True
            compareCount = 0
            exactCount = 0

        critOld = criteria

        #Handles libraries in YAML file
        if criteria == 'libraries':
            for lib in critData['names']:
                if critData['restriction'].lower() != 'exactly':
                    critAns = critAns & LibRestrict(source, critData['restriction'], lib, True)
                else:
                    critAns = critAns & LibRestrict(source, 'at_least', lib, True)
                    exactCount += 1
                    if exactCount == 1:
                        with open(source, 'r') as f:
                            data = f.read()
                            compareCount =  len(re.findall(r'^#include\s*[\s\S][<"]\S+[>"]$', data, flags=re.MULTILINE))

        #Handles keywords in YAML file
        elif criteria == 'keywords':
            keyCount = True
            for kword in critData['names']:
                if critData['restriction'].lower() != 'exactly':
                    critAns = critAns & WordRestrict(newSource, critData['restriction'], kword, critData['scope'], True)
                else:
                    if keyCount:
                        print("Exactly not supported for keywords, at_least will be used instead.")
                        keyCount = False
                    critAns = critAns & WordRestrict(newSource, 'at_least', kword, critData['scope'], True)
    
    #To print the last criteria in the loop
    if exactCount != 0 and compareCount != exactCount:
        critAns = critAns & False
    print(str(critCount) + ". " + critOld + " restriction result is " + str(critAns))


#Function to restrict a single library, no need for the YAML file, further explanation available exactly below function definition
@app.command("library")
def LibRestrict(source: str  = typer.Argument(..., help="The path of the .cpp or .h file the user wants restrictor to work on."),
                 restriction: str = typer.Argument(..., help="The restriction type used for 3 ways of checking:\n\nat_least: The library being checked must exist (It can be with other libraries).\n\nexactly: The library being checked must only exist (It can not be with other libraries).\n\nforbidden: The library being checked must not exist."),
                 lib: str = typer.Argument(..., help="The name of the library the user wants to check."),
                 hide:bool = typer.Argument(False, hidden=True, help="A hidden variable for developers use, used to return boolean")):
    """
    This tool will check if a certain library inputted by the user follows as certain restriction type of (at_least/exactly/forbidden) in a .cpp or .h file also inputted by the user.
    """

    #Makes sure that restriction inputted is a viable restriction
    if restriction.lower() not in ["exactly", "forbidden", "at_least"]:
        print("Invalid Restriction Input")
        return False
    
    with open(source, 'r') as f:
        source = f.read()

    #Handles restriction type "exactly"
    if restriction.lower() == "exactly":
        header = re.findall(r'^#include\s*[\s\S][<"]\S+[>"]$', source, flags=re.MULTILINE)
        if len(header) == 1:
            header = header[0].split("<")[1].split(">")[0] if len(header[0].split("<")) > 1 else header[0].split("\"")[1]
            if header == lib:
                if hide == False:
                    print("True")
                return True
            else:
                if hide == False:
                    print("False")
                return False

    #Handles restriction types "at_least" and "forbidden"
    else:
        existFlag = False
        header = re.findall(r'^#include\s*[\s\S][<"]\S+[>"]$', source, flags=re.MULTILINE)
        lib1 = "#include <" + lib + ">"
        lib2 = "#include \""+ lib + "\""

        for library in header:
            if library == lib1 or library == lib2:
                existFlag = True

        if restriction.lower() == "forbidden":
            if existFlag == False:
                if not hide:
                    print("True")
                return True
            else:
                if not hide:
                    print("False")
                return False
        elif restriction.lower() == "at_least":
            if existFlag == True:
                if not hide:
                    print("True")
                return True
            else:
                if not hide:
                    print("False")
                return False



#Function to restrict a single keyword, no need for the YAML file, further explanation available exactly below function definition.
@app.command("keyword")
def WordRestrict(source: str  = typer.Argument(..., help="The path of the .cpp or .h file the user wants restrictor to work on."),
                 restriction: str = typer.Argument(..., help="The restriction type used for 2 ways of checking:\n\nat_least: The keyword being checked must exist (It can be with other keywords).\n\nforbidden: The keyword being checked must not exist.\n\nexactly not available for keywords, will work as at_least"),
                 keyword: str = typer.Argument(..., help="The keyword the user wants to check."),
                 scope: str = typer.Argument(..., help="The scope the user wants to check inside (Function or Class)."),
                 hide:bool = typer.Argument(False, hidden=True, help="A hidden variable for developers use, used to return boolean")):
    """
    This tool will check if a certain keyword inputted by the user follows as certain restriction type of (at_least/exactly/forbidden) in a .cpp or .h file also inputted by the user.
    """

    #Makes sure that restriction inputted is a viable restriction
    if restriction.lower() not in ["exactly", "forbidden", "at_least"]:
        print("Invalid Restriction Input")
        return False
    
    #Check if global scope or not, if not then use scopeGetter to get everything in the scope defined by the user
    if scope.lower() == "global" or scope == "":
        with open(source, 'r') as f:
            source = f.read()
    else:
        source = scopeGetter(source, scope)
    
    #Check if keyword exists and print true or false according to restriction
    if re.search(fr"(?:(?<=\s)|(?<=^)){keyword}(?=\s|$)", source):
        print(re.search(fr"(?:(?<=\s)|(?<=^)){keyword}(?=\s|$)", source))
        if restriction.lower() == "at_least" or restriction.lower() == "exactly":
            if not hide:
                print("True")
            return True
        elif restriction.lower() == "forbidden":
            if not hide:
                print("False")
            return False
    else:
        if restriction.lower() == "at_least" or restriction.lower() == "exactly":
            if not hide:
                print("False")
            return False
        elif restriction.lower() == "forbidden":
            if not hide:
                print("True")
            return True



#Function to restrict a single class, no need for the YAML file, further explanation available exactly below function definition.
@app.command("class")
def ClassRestrict(source: str  = typer.Argument(..., help="The path of the .cpp or .h file the user wants restrictor to work on."),
                 restriction: str = typer.Argument(..., help="The restriction type used for 3 ways of checking:\n\nat_least: The class being checked must exist (It can be with other keywords).\n\nexactly: The class being checked must only exist (It can not be with other libraries).\n\nforbidden: The class being checked must not exist."),
                 prototype: str = typer.Argument(..., help="The class the user wants to check (Must input like this: \"class name\")."),
                 scope: str = typer.Argument(..., help="The scope the user wants to check inside (Function or Class).")):
    """
    This tool will check if a certain class inputted by the user follows as certain restriction type of (at_least/exactly/forbidden) in a .cpp or .h file also inputted by the user.
    """

    #Makes sure that restriction inputted is a viable restriction
    if restriction.lower() not in ["exactly", "forbidden", "at_least"]:
        print("Invalid Restriction Input")
        return
    
    #Check if global scope or not, if not then use scopeGetter to get everything in the scope defined by the user
    if scope.lower() == "global" or scope == "":
        with open(source, 'r') as f:
            source = f.read()
    else:
        source = scopeGetter(source, scope)

    prototype = prototype.strip()
    #Check if class exists and print true or false according to restriction
    if re.search(fr"(?:(?<=\s)|(?<=^)){prototype}\s*{'{'}(?=\s|$)", source):
        if restriction.lower() == "exactly":
            if len(re.findall(r"(?:(?<=\s)|(?<=^))class.*?\{(?=\s|$)", source, flags=re.MULTILINE)) > 1:
                print("False")
            else:
                print("True")
        elif restriction.lower() == "at_least":
            print("True")
        elif restriction.lower() == "forbidden":
            print("False")
    else:
        if restriction.lower() == "at_least" or restriction.lower() == "exactly":
            print("False")
        elif restriction.lower() == "forbidden":
            print("True")



#Function to restrict a single function, no need for the YAML file, further explanation available exactly below function definition.
@app.command("function")
def FuncRestrict(source: str  = typer.Argument(..., help="The path of the .cpp or .h file the user wants restrictor to work on."),
                 restriction: str = typer.Argument(..., help="The restriction type used for 3 ways of checking:\n\nat_least: The function being checked must exist (It can be with other keywords).\n\nexactly: The function being checked must only exist (It can not be with other libraries).\n\nforbidden: The function being checked must not exist."),
                 prototype: str = typer.Argument(..., help="The function the user wants to check (Must input like this: \"int functionName(int, int)\"."),
                 scope: str = typer.Argument(..., help="The scope the user wants to check inside (Function or Class).")):
    """
    This tool will check if a certain function inputted by the user follows as certain restriction type of (at_least/exactly/forbidden) in a .cpp or .h file also inputted by the user.
    """

    #Makes sure that restriction inputted is a viable restriction
    if restriction.lower() not in ["exactly", "forbidden", "at_least"]:
        print("Invalid Restriction Input")
        return
    
    #Check if global scope or not, if not then use scopeGetter to get everything in the scope defined by the user
    if scope.lower() == "global" or scope == "":
        with open(source, 'r') as f:
            source = f.read()
    else:
        source = scopeGetter(source, scope)

    #Making the regex suitable to find function no matter the user input
    prototype = prototype.strip()
    prototypeName = prototype.split("(")[0] + "\s*"
    prototypeName += '('
    prototypeVars = prototype.split("(")[1].split(")")[0].split(",")
    prototypeRegex = "(?:(?<=\s)|(?<=^))" + prototypeName
    for p in prototypeVars:
        prototypeRegex += ".*" + p.strip().split(' ')[0] + ".*,"
    prototypeRegex = prototypeRegex[:-1] + ').*\n*.*{[\s\S]*}(?=\s|$)'
    
    
    #Check if function exists and print true or false according to restriction
    if re.search(prototypeRegex, source) != None:
        if restriction.lower() == "exactly":
            if len(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*\{[^{}]*\}", source, flags=re.MULTILINE)) > 1:
                print("False")
            else:
                print("True")
        elif restriction.lower() == "at_least":
            print("True")
        elif restriction.lower() == "forbidden":
            print("False")
    else:
        if restriction.lower() == "at_least" or restriction.lower() == "exactly":
            print("False")
        elif restriction.lower() == "forbidden":
            print("True")



#Function to restrict a single (private/public/protected) function, no need for the YAML file, further explanation available exactly below function definition.
@app.command("access")
def PrivRestrict(source: str  = typer.Argument(..., help="The path of the .cpp or .h file the user wants restrictor to work on."),
                 restriction: str = typer.Argument(..., help="The restriction type used for 3 ways of checking:\n\nat_least: The function being checked must exist (It can be with other keywords).\n\nexactly: The function being checked must only exist (It can not be with other libraries).\n\nforbidden: The function being checked must not exist."),
                 prototype: str = typer.Argument(..., help="The function the user wants to check (Must input like this: \"int functionName(int, int)\" or \"int functionName(int x,int y)\")."),
                 scope: str = typer.Argument(..., help="The scope the user wants to check inside (Function or Class)."),
                 type: str = typer.Argument(..., help="The access type the user wants to check for (private/public/protected).")):
    """
    This tool will check if a certain (private/public/protected) function inputted by the user follows as certain restriction type of (at_least/exactly/forbidden) in a .cpp or .h file also inputted by the user.
    """
    #Makes sure that restriction inputted is a viable restriction
    if restriction.lower() not in ["exactly", "forbidden", "at_least"]:
        print("Invalid Restriction Input")
        return
    
    #Check if global scope or not, if not then use scopeGetter to get everything in the scope defined by the user as well as preparing data for access_type search
    if scope.lower() == "global" or scope == "":
        data = codeParser.prepareData(source)
    else:
        source = scopeGetter(source, scope)
        file = open("restrictorGen.cpp", "w")
        file.write(source)
        file.close()
        data = codeParser.prepareData("restrictorGen.cpp")

    #Variables used in the following if statement to find if function is private
    if prototype.split("virtual") == 1 and prototype.split("static" == 1):
        proto = prototype.split(' ')[0] + ' (' + prototype.split('(')[1][:-1].strip() + ')'
    else:
        proto = prototype.split(' ')[1] + ' (' + prototype.split('(')[1][:-1].strip() + ')'
    spelling = prototype.split('(')[0].split(' ')[-1]

    for decl in data['nodes']:
        if decl['kind'] == "FUNCTION_DECL" and decl['spelling'] == spelling and decl['prototype'] == proto and decl['access_type'] == type.upper():
            FuncRestrict(source, restriction, prototype, scope)
            return
    print("False")



if __name__ == "__main__":
    app()
