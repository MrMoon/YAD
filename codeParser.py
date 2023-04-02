import re
import os
import orjson, json
import clang.cindex 

def findLocationFunction(data, prototype: str):

    isTemplate = 0
    if len(prototype.split("template"))> 1 :
        isTemplate=1
        prototype = prototype.split(">")
        prototype[0] = prototype[0] + ">"
        regex =  re.split('template\\s*<\\s*typename\\s*([a-zA-Z])\\s*>\\s*',prototype[0])
        returntype = regex[1]
        prototype  = prototype[1]
        params = prototype
        prototype = prototype.split(returntype)[1]

    name=re.split('\s+|\(', prototype)[1]
    if isTemplate == 0:
        returntype = prototype.split(name)[0].strip()
        
    if isTemplate == 1:
        prototype = params
        
    params = prototype.split(name)[1].strip()
    qualType = returntype + params
    qualType = qualType.replace(" ", "")
    pos = []
    type = ""
    if isTemplate == 0:
        for item in data['nodes']:
            if item['kind'] == "FUNCTION_DECL":
                type  = "function"
            if item['kind'] == "CXX_METHOD":
                type = "member_function_outside"
            if type != "" and item['spelling'].strip() == name.strip() and returntype.strip() == item['prototype'].split("(")[0].strip() and params == "(" + item['prototype'].split("(")[1]:
                end = item['end']
                start = item['start']
                pos += [start, end, "function"]
    else:
            flag=0
            for item in data['nodes']:
                #not the best way!!
                if flag == 1 and item['kind'] == "FUNCTION_TEMPLATE" or  item['kind'] == "FUNCTION_DECL" or item['kind'] == "STRUCT_DECL" or item['kind'] == "CLASS_DECL":
                    end = item['start']-1 
                    pos+=[end]
                    break
                #strip is not enough, find better solution
                if item['kind'] == "FUNCTION_TEMPLATE" and item['spelling'].strip() == name.strip() and returntype.strip() == item['prototype'].split("(")[0].strip() and params.strip() == "(" + item['prototype'].split("(")[1].strip():
                    start = item['start']
                    flag=1
                    pos += [start]
            #fix this
            if flag == 0:
                pos+=[10000]
                
    return pos

def findLocationClass(data, prototype: str, iter: int):
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
        #need to add template  
        #where to put this?
        if item['start'] < stc or item['end'] > enc:
            if item['mangled_name'].startswith('?'):
                mangledName= item['mangled_name'].split("@")
                if len(mangledName) >= 1 and mangledName[1] == name:
                    if item['kind'] == "CXX_METHOD":
                        returnType = item['prototype'].split(" ")[0]
                        prototype = returnType +" " +item['displayname']
                        pos += findLocationFunction(data, prototype)
                    # start = item['start']
                    # end = item['end']
                    # pos+=[start, end, "member_function_outside"]
                    
        for inherit in item['inherits_from']:
            if inherit == name:
                start = item['start']
                end = item['end']
                pos+=[start, end, "inheritance"]
                pos += findLocationClass(data, "class "+  item['spelling'], iter+1)
                        
        #find start and end positions of all classes with friendship with this class
        for friend in item['friend_with']:
            if friend == prototype:
                start = item['start']
                end = item['end']
                pos+=[start, end, "friendship"]
                pos += findLocationClass(data,  "class " + item['spelling'], iter+1)
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
        pos = findLocationClass(data, prototype,0 )  
        
    if type == "function":
        pos = findLocationFunction( data, prototype)  
        
    return pos
                    