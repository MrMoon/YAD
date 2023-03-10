import typer
import re
import os



app = typer.Typer()



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
def comment_Out_Class(input: str  = typer.Argument(...), cls: str  = typer.Argument(...)):
    """
    This tool will comment out a class implementation from a C++ file (equivalent to deleting the class).
    """
    #System call to get ast dump of anything containing the string inputted in cls (cls stands for class)
    sys = "clang-check -ast-dump -ast-dump-filter={} test.cpp --".format(cls)
    ret = os.popen(sys).read()
    if ret == "":
        print("Class not found.")
        return

    #Filter the code using regex to keep what is important
    regex = r"Dumping {}:\nCXXRecordDecl.*?\n(\|)".format(cls)
    ret = re.search(regex, ret).group(0)
    ret = ret.split(':')
    rowStart = int(ret[3])
    colStart = int(ret[4].split(',')[0])
    if ret[4].split(',')[1] == " col":
        rowEnd = int(ret[3])
        colEnd = int(ret[5].split('>')[0])
    else:
        rowEnd = int(ret[5])
        colEnd = int(ret[6].split('>')[0])

    #Get all the code to edit it
    with open(input, 'r') as f:
        lines = f.readlines()
    
    #Comment out class
    lines[rowStart-1] = lines[rowStart - 1][:colStart-1] + "/*" + lines[rowStart - 1][colStart-1:]

    if rowStart == rowEnd:
        colEnd += 2

    lines[rowEnd-1] = lines[rowEnd - 1][:colEnd+1] + "*/" + lines[rowEnd - 1][colEnd+1:]
    
    #Write the modified code into the file.
    with open(input, 'w') as f:
        f.writelines(lines)



if __name__ == "__main__":
    app()
