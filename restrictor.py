import yaml
import orjson, json
import typer
import re
import codeParser

app = typer.Typer()

@app.command("restrict")
def Restrict(source: str  = typer.Argument(..., help="The path of the .cpp or .h file the user wants restrictor to work on."), rules: str  = typer.Argument(..., help="The path of the YAML file containing user requiremnets")):
    with open(rules) as file:
        yamlFile = yaml.load(file, Loader=yaml.FullLoader)
    jsonFormat = json.dumps(yamlFile, indent=4)
    jsonData = json.loads(jsonFormat)
    for criteria, critData in jsonData.items():
        # print(criteria + ":")
        # print(critData['restriction'])
        if criteria == libraries:
            print("hi")


#Function to restrict a single library, no need for the YAML file, further explanation available exactly below function definition.
@app.command("library")
def LibRestrict(source: str  = typer.Argument(..., help="The path of the .cpp or .h file the user wants restrictor to work on."),
                 restriction: str = typer.Argument(..., help="The restriction type used for 3 ways of checking:\n\nat_least: The library being checked must exist (It can be with other libraries).\n\nexactly: The library being checked must only exist (It can not be with other libraries).\n\nforbidden: The library being checked must not exist."),
                 lib: str = typer.Argument(..., help="The name of the library the user wants to check.")):
    """
    This tool will check if a certain library inputted by the user follows as certain restriction type of (at_least/exactly/forbidden) in a .cpp or .h file also inputted by the user.
    """

    #Makes sure that restriction inputted is a viable restriction
    if restriction.lower() not in ["exactly", "forbidden", "at_least"]:
        print("Invalid Restriction Input")
        return
    
    with open(source, 'r') as f:
        source = f.read()

    #Handles restriction type "exactly"
    if restriction.lower() == "exactly":
        header = re.findall(r'^#include\s*[\s\S][<"]\S+[>"]$', source, flags=re.MULTILINE)
        if len(header) == 1:
            header = header[0].split("<")[1].split(">")[0] if len(header[0].split("<")) > 1 else header[0].split("\"")[1]
            if header == lib:
                print("True")
            else:
                print("False")

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
                print("True")
            else:
                print("False")
        elif restriction.lower() == "at_least":
            if existFlag == True:
                print("True")
            else:
                print("False")


#Function to restrict a single keyword, no need for the YAML file, further explanation available exactly below function definition.
@app.command("keyword")
def WordRestrict(source: str  = typer.Argument(..., help="The path of the .cpp or .h file the user wants restrictor to work on."),
                 restriction: str = typer.Argument(..., help="The restriction type used for 2 ways of checking:\n\nat_least: The keyword being checked must exist (It can be with other keywords).\n\nforbidden: The keyword being checked must not exist.\n\nexactly not available for keywords, will work as at_least"),
                 keyword: str = typer.Argument(..., help="The keyword the user wants to check."),
                 scope: str = typer.Argument(..., help="The scope the user wants to check inside (Function or Class).")):
    """
    This tool will check if a certain keyword inputted by the user follows as certain restriction type of (at_least/exactly/forbidden) in a .cpp or .h file also inputted by the user.
    """

    #Makes sure that restriction inputted is a viable restriction
    if restriction.lower() not in ["exactly", "forbidden", "at_least"]:
        print("Invalid Restriction Input")
        return
    
    #Check if global scope or not
    if scope.lower() == "global" or scope == "":
        with open(source, 'r') as f:
            source = f.read()
    else:
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
        #Ask doctor if inheritence part of scope !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
    
    #Check if keyword exists and print true or false according to restriction
    if re.search(fr"(?:(?<=\s)|(?<=^)){keyword}(?=\s|$)", source):
        if restriction.lower() == "at_least" or restriction.lower() == "exactly":
            print("True")
        elif restriction.lower() == "forbidden":
            print("False")
    else:
        if restriction.lower() == "at_least" or restriction.lower() == "exactly":
            print("False")
        elif restriction.lower() == "forbidden":
            print("True")


if __name__ == "__main__":
    app()
