import re
import os
import orjson, json
import clang.cindex 

def findLocationFunction(data, prototype: str, source):
    #label function by its type 
    if len(prototype.split("template"))> 1 :
        if len(prototype.split("::")) > 1 :
            type = "template_member_function"
        else:
            type = "template_function"
    elif len(prototype.split("::")) > 1:
        type = "member_function"
    else:
        type="function"
    
    #extract information from function prototype
    if type == "member_function" or type == "template_member_function":
        parent_class = prototype.split("::")[0].strip().split(" ")[-1]
        returntype = prototype.split(parent_class)[0].strip().split(" ")[-1]
        prototype=prototype.replace(" ", "")
        name = prototype.split("::")[1].split("(")[0]
    else:
        if type == "template_function":
            prototype = prototype.split(">")[1].strip()
        name = prototype.split('(')[0].split(" ")[-1].strip()
        returntype = prototype.split(name)[0].strip()
    params = prototype.split(name)[1]
    qualtype = returntype + params
    qualtype = qualtype.replace(" ", "")
    
    #retrieve position of function
    pos=[]
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

def findLocationClass(data, prototype: str, source, type: str, iteration = 0):
    #classes list stores all classes that inherits from\friend with main class in order to parse their member functions and nested classes   
    classes =  [prototype]
    pos=[]
    for class_i in classes:
        name = class_i.split(" ")[1]
        class_start = -1
        class_end = -1
        flag=0
        i=0 
        while i < len(data['nodes']):
            item = data['nodes'][i]
            #find start and end positions of a class given its name
            if item['spelling'] == name:
                if ((item['is_class'] == True and type == "class") or (item['is_struct'] == True and type == "struct")):
                    start = item['start']
                    end = item['end']
                    class_start = start 
                    class_end = end
                    if iteration == 1:
                        pos = [start, end, type]
                        return pos
                    pos+=[start, end, type]
                    flag =1
            if flag  == 0 : 
                i = i+1
                continue
            #check member functions implemented outside the class
            if item['start'] < class_start or item['end'] > class_end:
                if item['mangled_name'].startswith('?'):
                    mangledName= item['mangled_name'].split("@")
                    if len(mangledName) > 1 and mangledName[1] == name:
                        if item['kind'] == "CXX_METHOD":
                            returnType = item['prototype'].split(" ")[0]
                            func_prototype = returnType +" " + name + "::" +item['displayname']
                            pos+= findLocationFunction(data, func_prototype, source)
            #check template member functions  
            if item["kind"] == "FUNCTION_TEMPLATE":
                start_line = item['start']
                j = i+1
                template_node = data['nodes'][j]
                while template_node['start'] == start_line:
                    if template_node['kind'] == "TEMPLATE_TYPE_PARAMETER":
                        template = template_node['spelling']
                    if template_node['kind'] == "TYPE_REF" and template_node['spelling'] == prototype:
                        returnType = item['prototype'].split(" ")[0]
                        func_prototype = "template <typename " + template + "> " + returnType +" " + name + " :: " +item['displayname']
                        pos += findLocationFunction(data, func_prototype, source)
                    j += 1
                    template_node = data['nodes'][j]     
            #find start and end positions of all classes that inherits from this class       
            for inherit in item['inherits_from']:
                if inherit == name:
                    start = item['start']
                    end = item['end']
                    classes += [type + " "+  item['spelling']]            
            #find start and end positions of all classes with friendship with this class
            for friend in item['friend_with']:
                if friend == class_i:
                    start = item['start']
                    end = item['end']
                    classes +=  [type + " "+  item['spelling']]
            i = i+1
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

def positions ( source: str, type: str, prototype: str , type1=0):
    
    data = prepareData(source)
    pos =[]
    
    if type == "class": # or type == "struct":
        pos = findLocationClass(data, prototype , source, type, type1)  
        
    if type == "function":
        pos = findLocationFunction( data, prototype, source)  
        
    return pos
                    