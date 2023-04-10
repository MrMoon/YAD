import re
import os
import orjson, json
import clang.cindex 

def findLocationFunction(data, prototype: str, source, type = ""):
    #prepare info for template functions
    if len(prototype.split("template"))> 1 :
        if len(prototype.split("::")) > 1 or type == "member_function":
            type = "template_member_function"
        else:
            type = "template_function"
        prototype = prototype.split(">")
        prototype[0] = prototype[0] + ">"
        regex =  re.split('template\\s*<\\s*typename\\s*([a-zA-Z])\\s*>\\s*',prototype[0])
        returntype = regex[1]
        prototype  = prototype[1]
        params = prototype
        prototype = prototype.split(returntype, 1)[1]
        if type == "template_function":
            name=re.split('\s+|\(', prototype)[1].strip()
    elif type != "member_function" and len(prototype.split("::")) == 1:
        type="function"
    else:
        type = "member_function"
    
    if type == "member_function" or type == "template_member_function":
        parent_class = prototype.split("::")[0].split(" ")[-1]
        if type == "member_function":
            returntype = prototype.split(parent_class)[0]
        prototype=prototype.replace(" ", "")
        print(prototype)
        if len(prototype.split("::")) == 1:
            return
        name = prototype.split("::")[1].split("(")[0]
    else:
        name=re.split('\s+|\(', prototype)[1].strip()
    
    if type == "function":
        returntype = prototype.split(name)[0].strip()
  
    params = prototype.split(name)[1]
    qualtype = returntype + params
    qualtype = qualtype.replace(" ", "")
    pos=[]
    print( name)
    print(returntype)
    print(qualtype)
    if type == "function":
        for item in data['nodes']:
            if item['kind'] == "FUNCTION_DECL" and item['spelling'].replace(" ", "") == name and item['prototype'].replace(" ", "") == qualtype:
                end = item['end']
                start = item['start']
                pos += [start, end, type]
      
    if type == "member_function":
        for item in data['nodes']:
            if item['kind'] == "CXX_METHOD" and item['spelling'].replace(" ", "") == name and item['prototype'].replace(" ", "") == qualtype:
                end = item['end']
                start = item['start']
                pos += [start, end, type]
                
    if type == "template_function" or type == "template_member_function":
        for item in data['nodes']:
            if item['kind'] == "FUNCTION_TEMPLATE" and item['spelling'].replace(" ", "") == name and item['prototype'].replace(" ", "") == qualtype:
                    start = item['start']
                    end =-1
                    with open(source, "r") as source_file:
                        lines = source_file.readlines()
                        
                    #check for forward declaration 
                    openb =0
                    for char in lines[start-1]:
                        if char == '{':
                            openb = openb+1
                    if openb == 0:
                        pos += [start, start, type]
                        continue
                    #find when the function ends 
                    i = start 
                    while(True):
                        for char in lines[i]:
                            if char == '{':
                                openb = openb+1
                            if char == '}':
                                openb = openb -1
                                if openb == 0:
                                    end = i+1
                                    break
                        i = i+1
                        if end != -1:
                            break
                    pos += [start, end, type]
        
    return pos

def findLocationClass(data, prototype: str, iter: int, source):
    name = prototype.split(" ")[1]
    pos=[]
    stc = -1
    enc = -1
    for item in data['nodes']:
        #find start and end positions of a class given its name
        if item['spelling'] == name and item['is_class'] == True:
            start = item['start']
            end = item['end']
            stc = start 
            enc = end
            if iter == 0:
                pos+=[start, end, "class"]
    
        #check member functions implemented outside the class
        if item['start'] < stc or item['end'] > enc:
            if item['mangled_name'].startswith('?'):
                mangledName= item['mangled_name'].split("@")
                if len(mangledName) >= 1 and mangledName[1] == name:
                    if item['kind'] == "CXX_METHOD":
                        returnType = item['prototype'].split(" ")[0]
                        prototype = returnType +" " +item['displayname']
                        if len(prototype.split("::")) > 1:
                            pos+= findLocationFunction(data, prototype, source, "member_function")
        
        #find start and end positions of all classes that inherits from this class       
        for inherit in item['inherits_from']:
            if inherit == name:
                start = item['start']
                end = item['end']
                pos+=[start, end, "inheritance"]
                pos += findLocationClass(data, "class "+  item['spelling'], iter+1, source)
                        
        #find start and end positions of all classes with friendship with this class
        for friend in item['friend_with']:
            if friend == prototype:
                start = item['start']
                end = item['end']
                pos+=[start, end, "friendship"]
                pos += findLocationClass(data,  "class " + item['spelling'], iter+1, source)
    return pos

        
def prepareData ( source: str):
   
    index = clang.cindex.Index.create()
    tu = index.parse(source)
    
    friendFlag = False
    classPointer = -1
    output = {"nodes": []}
    for node in tu.cursor.walk_preorder():
        if node.kind == clang.cindex.CursorKind.CLASS_DECL:
            classPointer = 0
            friendFlag = False
            
        elif node.kind == clang.cindex.CursorKind.CXX_BASE_SPECIFIER:
            inh = node.spelling
            output["nodes"][classPointer]["inherits_from"].append(inh)

        elif node.kind == clang.cindex.CursorKind.FRIEND_DECL:
            friendFlag = True

        elif friendFlag:
            friend = node.spelling
            if len(friend.split("class")) == 1:
                friend = node.type.spelling.split('(')[0] + node.displayname
            output["nodes"][classPointer]["friend_with"].append(friend)
            friendFlag = False

        classPointer = classPointer - 1
            
        node_dict = {
            "kind": str(node.kind.name),
            "spelling": node.spelling,
            "prototype": node.type.spelling,
            "displayname": node.displayname,
            "type": str(node.type),
            "start": int(node.location.line),
            "end": int(node.extent.end.line),
            "semantic_parent": str(node.semantic_parent),
            "lexical_parent": str(node.lexical_parent),
            "mangled_name": node.mangled_name,
            "is_const_method": node.is_const_method(),
            "is_const_method": node.is_const_method(),
            "is_virtual_method": node.is_virtual_method(),
            "is_pure_virtual_method": node.is_pure_virtual_method(),
            "is_template": node.kind == clang.cindex.CursorKind.FUNCTION_TEMPLATE,
            "is_struct": node.kind == clang.cindex.CursorKind.STRUCT_DECL,
            "is_class": node.kind == clang.cindex.CursorKind.CLASS_DECL,
            "is_enum": node.kind == clang.cindex.CursorKind.ENUM_DECL,
            "inherits_from": [],
            "friend_with": []
        }
        output["nodes"].append(node_dict)
        
    with open('C:\\Users\\Rund\\Desktop\\Yad\\jsonfile.json', 'w') as f:
        json.dump(output, f, indent = 4)
        
    with open("jsonfile.json", "rb") as f:
        data = orjson.loads(f.read())
    return data

def positions ( source: str, type: str, prototype: str):
    
    data = prepareData(source)
    pos =[]
    
    if type == "class" or type == "struct":
        pos = findLocationClass(data, prototype,0 , source)  
        
    if type == "function":
        pos = findLocationFunction( data, prototype, source)  
        
    return pos
                    