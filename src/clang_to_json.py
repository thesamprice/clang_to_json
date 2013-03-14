from clang.cindex import Index, CursorKind, TypeKind
from pprint import pprint

def process_comment(comment):
    import re

    if comment == None:
        return []
    comment = re.sub("(\n\s*)?\!\<", "\n", comment) #Drop !<
    comment = re.sub("\n\s*\*", "\n", comment) #Drop the *
    started= False

    result = []
    if comment != '':

        #Pull apart, This took a lot of fiddling to figure out... I used KODOS to figure this guy out
        reg = '\n?(\s*)@(\w+)((.(?!\n\s*@))*.)?'
        parts = re.findall(reg,comment)
        count = 0
        if(len(parts) == 0):
          comment = "@brief " + comment
          reg = '\n?(\s*)@(\w+)((.(?!\n\s*@))*.)?'
          parts = re.findall(reg,comment) 
        
        last_space_count = len(parts[0][0].replace('\n','')) #1st space count
        
        current_level = {'count':last_space_count,'data':result}
        stack = [current_level]

        
        for part in parts:
            space_count = len(part[0].replace('\n',''))
            key = part[1]
            val = part[2]
            val = val.strip()
            val = val.replace('\n' + ' '*space_count,'')
            if(key == 'children'):
                print "Warning key set to children changing to children1"
                key = "children1"
            json_com = {key:val,'children':[]}
            
            #Save the comment
            while space_count != current_level['count']:
                if(space_count < current_level['count']):
                    #print current_level['count'],space_count
                    #pprint(stack)
                    current_level = stack.pop()
                    if(current_level['count'] == space_count):
                        stack.append(current_level)
                    
                elif(space_count > current_level['count']):
                    #print current_level['count'],space_count
                    #pprint(stack)
                    new_container = {'count':space_count, 'data':current_level['data'][-1]['children']}
                    stack.append(new_container)
                    current_level = new_container

            current_level['data'].append(json_com)
            last_obj = json_com
    return result
def comment_contains(comment,key,value=None):
    for item in comment:

        if key in item:
            if value == None:
                return True
            if item[key] == value:
                return True
    return False
def get_key_from_comment(comment,key):
    for item in comment:
        if key in item:
            return item
    return {}
    
def get_array_info(type):
    result = []

    while type.get_array_size() != -1:
        result.append(type.get_array_size())
        type = type.get_array_element_type()    
    return result

def process_record_members(inst):
    members = []
    for child in inst.get_children():
        item = process_item(child)
        members.append(item)
    return members

#TODO figure out how to get classes in here.
record_item_types = [CursorKind.STRUCT_DECL, CursorKind.UNION_DECL]
canonical_kinds = [TypeKind.TYPEDEF, TypeKind.UNEXPOSED,TypeKind.CONSTANTARRAY]
def get_blank_item():
    result                  = {}
    result['comments']      = []
    result['array']         = []
    result['name']          = "not_set"
    result['is_pointer']    = False
    result['members']       = []
    result['kind']          = None 
    result['bitarray']      = False  
    result['basetype_name'] = None
    result['data']          = None
    return result
    
def process_item(item):
    result = get_blank_item()

    result['comments']   = process_comment(item.getRawComment())
    result['array']      = get_array_info(item.type)
    result['name']       = item.spelling
    result['is_pointer'] = item.type.kind == TypeKind.POINTER

    result['members']    = []
    if result['is_pointer'] == False:
        if  item.kind in record_item_types:
            result['members'] = process_record_members(item)
    
    result['kind']       = item.kind    
    type = item.type
    
    if result['is_pointer']:
        type = type.get_pointee()

    if type.kind in canonical_kinds:
        type = item.type.get_canonical()
    else:
        type = item.type

    while type.kind == TypeKind.CONSTANTARRAY:
        type = type.element_type.get_canonical()
    
    if result['is_pointer']:
        type = type.get_pointee()
        
    result['basetype'] = type.kind        
    result['basetype_name'] = type.get_declaration().spelling

    result['data'] = item
    

    #Checks for bit array...
    result = process_bitarray(item,result)


    return result
def process_bitarray(item,json):
    if comment_contains(json['comments'],'bitarray') == False:
        return json
    json['bitarray'] = True

    bitarray = get_key_from_comment(json['comments'],'bitarray')
    for bits in bitarray['children']:
        item = get_blank_item()

        item['comments'] = bits['children']
        item['bits']     = int(bits['bits'])
        try:
            name = get_key_from_comment(item['comments'],'name')
            item['name']     = name['name']
        except:
            pass
        
        json['members'].append(item)
    
    if json['bitarray'] == 'lsbf':
        json['members'].reverse()
        json['bitarray'] = 'msbf' #Always change to msbf...

    return json
def process_file(filename,my_args=""):
    index = Index.create()
    file_obj = index.parse(filename,args=my_args.split())
    cursor = file_obj.cursor
    child = cursor.get_children()
    result = []
    for inst in child:
        item = process_item(inst)
        result.append(item)
    return result


if __name__ == "__main__":
    from pprint import pprint
    a =  process_file('../example_cpp/test.h')
    pprint(a)
