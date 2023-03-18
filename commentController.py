import os
import typer
import re
import codeParser
app = typer.Typer()

#This function is responsible for putting classes and functinos into comment blocks using /**/
def commentMaker(pointer: int, retrievedAST: str, source: str, isTemplate: bool):
    #Find where the classes or functions start
    position = codeParser.positions(pointer, retrievedAST, isTemplate)
    #Get all the code to edit it
    with open(source, 'r') as f:
        lines = f.readlines()
    
    if isTemplate:
        flag = lines[position[0] - 1].count('{') - lines[position[0] - 1].count('}')
        lines[position[0] - 1] = "//" + lines[position[0] - 1]
        count = 0
        while flag > 0:
            lines[position[0]+count] = "//" + lines[position[0]+count]
            flag += lines[position[0]+count].count('{')
            flag -= lines[position[0]+count].count('}')
            count += 1
    #Comment out class
    else:
        lines[position[0]-1] = "//" + lines[position[0]-1]
        for line in range(position[0], position[2]):
            lines[line] = "//" + lines[line]
    
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
    #Removing friendships
    clsFix = cls.split("class ")[1].split("::")
    clsInh = clsFix[len(clsFix)-1].strip()
    cls = "class " + clsInh

    #Accessing content of file
    with open(source, 'r') as f:
        sourceCode = f.read()

    #Handeling inheritence
    lstInh = []
    regex = r"class \w+:.*\s+{}.*\n".format(clsInh)
    retrieveAll = re.findall(regex, sourceCode, re.MULTILINE)
    for retrieveOne in retrieveAll:
        lstInh.append(retrieveOne.split(':')[0].strip())
        
    
    # Comment out all friendships from the source file
    sourceCode = re.sub(r'(//)?friend \s*{};\n'.format(cls), '//friend {};\n'.format(cls), sourceCode, flags=re.MULTILINE)

    # Write the modified contents to the source file
    with open(source, 'w') as f:
        f.write(sourceCode)

    #Commenting out the classes
    findClass = codeParser.findLocationClass(source, cls)
    for entry in findClass:
        if len(entry) == 2:
            commentMaker(entry[0], entry[1], source, False)
        else:
            commentMaker(entry[0], entry[1], source, entry[2])
    
    for entry in lstInh:
        CommentOutClass(source, entry)


@app.command("commentOutFunction")
def CommentOutFunction(source: str  = typer.Argument(...), fnc: str  = typer.Argument(...)):
    """
    This tool will comment out a function implementation from a C++ file using a function prototype (equivalent to deleting the function).
    """
    #Removing friendships
    fncFix = fnc.strip().split("const")[-1].strip().split("static")[-1].strip()
    fncFix = fncFix.replace("*", "\*")
    fncTemplate = ""
    if fncFix[:8] == "template":
        fncFix = fnc.split('>')[1].strip()
        fncTemplate = fnc.split('>')[0].strip() + '>'
    
    with open(source, 'r') as f:
        sourceCode = f.read()
    if fncFix[:8] == "template":
        sourceCode = re.sub(r'(//)?{}\s*\n?(//)?friend \s*{};\n'.format(fncTemplate, fncFix), "//{} friend {}".format(fncTemplate, fncFix),sourceCode, flags=re.MULTILINE)
    else:
        sourceCode = re.sub(r'(//)?friend \s*{};\n'.format(fncFix), "//friend {}".format(fncFix),sourceCode, flags=re.MULTILINE)

    with open(source, 'w') as f:
        f.write(sourceCode)

    findFunction = codeParser.findLocationFunction(source, fnc)
    if findFunction == None:
        return 
    for function in findFunction:
        commentMaker(function[0], function[1], source, function[2])


if __name__ == "__main__":
    app()