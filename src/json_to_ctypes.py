import clang_to_json
from TextFormat import AlignRegex
from django.template import Context, Template
from django.conf import settings

from clang.cindex import CursorKind, TypeKind
from pprint import pprint
#TODO THis needs filled out more...
type_dictionary = {TypeKind.BOOL:       "ctypes.c_bool",
                   TypeKind.CHAR_U:     "ctypes.ubyte",
                   TypeKind.UCHAR:      "ctypes.c_ubyte", ## Is uchar always same as ubyte?
                   TypeKind.CHAR16:     "(ctypes.c_char * 2)",
                   TypeKind.CHAR32:     "(ctypes.c_char *4)",
                   TypeKind.USHORT:     "ctypes.c_ushort",
                   TypeKind.UINT:       "ctypes.c_uint",
                   TypeKind.ULONG:      "ctypes.c_ulong",
                   TypeKind.ULONGLONG:  "ctypes.c_ulonglong",
                   TypeKind.UINT128:    "(ctypes.c_ulonglong *2)", #TODO....
                   TypeKind.CHAR_S:     "ctypes.c_char",
                   TypeKind.SCHAR:      "ctypes.c_char",
                   TypeKind.WCHAR:      "ctypes.c_wchar",
                   TypeKind.SHORT:      "ctypes.c_short",
                   TypeKind.INT:        "ctypes.c_int",
                   TypeKind.LONG:       "ctypes.c_long",
                   TypeKind.LONGLONG:   "ctypes.c_longlong",                   
                   TypeKind.INT128:     "(ctypes.c_longlong*2)",
                   TypeKind.FLOAT:      "ctypes.c_float",
                   TypeKind.DOUBLE:     "ctypes.c_double",
                   TypeKind.LONGDOUBLE: "ctypes.c_longdouble",
                   "uint64_t":          "ctypes.c_uint64",
                   "size_t":            "ctypes.c_size_t",
                   "int64_t":           "ctypes.c_int64" 
                   }
#TODO make pointer types for char's, and voids, nulls
#Have to set this in order for django to work properly 
pointer_dictionary = { TypeKind.CHAR_S: "ctypes.c_char_p",
                       TypeKind.SCHAR:  "ctypes.c_char_p",
                       TypeKind.WCHAR:  "ctypes.c_wchar_p",
                       TypeKind.VOID:   "ctypes.c_void_p"
                      }
try:
    settings.configure(TEMPLATE_DIRS=('/path/to/template_dir',), DEBUG=False,TEMPLATE_DEBUG=False)
except:
    pass

def get_members(item):
    requires = []
    source = ""
    count = 0
        #TODO Handle pointers
    for var in item['members']:
        if count > 0:
            source += ",\n"
        var_item = {'var_type':'ugh'}
        var_item['var_name'] = var['name']

        required = {'name':var['basetype_name'], 'data':var['data'],'bitarray':False}

        #Bit arrays are annoying...
        if var['bitarray']:
            required['bitarray'] = True
            required['info'] = var
            var_item['var_type'] = item['name'] + "_" + var['name']
            required['name']     = var_item['var_type']
            requires += [required]
        elif var['basetype'] in type_dictionary:
            var_item['var_type'] = type_dictionary[var['basetype']]
        else:
            var_item['var_type'] = var['basetype_name']
            requires += [required]

        
        if var['is_pointer']: #TODO CHAR POINTER THING...
            if var['basetype'] in pointer_dictionary:
                var_item['var_type'] = pointer_dictionary[ var['basetype'] ]
            else:
                var_item['var_type'] = "POINTER(" + var_item['var_type'] + ")"
            
        from copy import copy
        if len(var['array']) > 0:
            ar  = copy(var['array']) #Do not destroy the array by popping stuff off it
            #print var_item['var_type']
            var_item['var_type'] = var_item['var_type'] +" * " + str(ar.pop(0))
            while(len(ar) > 0):
                var_item['var_type'] = "(" + var_item['var_type'] +") * " + str(ar.pop(0))
        
        t = Template( """ ("{{var_name}}", {{var_type}})""")
        source += t.render(Context(var_item))
        
        count += 1
    
    return [source,requires]
    


def json_to_union(item,depth=0):
    t = Template( """class {{name}}(ctypes.Union):\n    _fields_ = [""")
    source = t.render(Context(item))
    
    members,requires = get_members(item)
    
    source += members + "]\n\n"
    return [source,requires]

def json_to_record(item,depth=0):
    t = Template( """class {{name}}(ctypes.LittleEndianStructure):\n    \"""{{raw_comment}}""\"\n    _fields_ = [""")
#    item['raw_comment'] = item['data'].getRawComment()
#    if item['raw_comment'] == None:
#        item['raw_comment'] = ''
#    item['raw_comment'] = AlignRegex('    ' + item['raw_comment'],'\S')

    source = t.render(Context(item))
    
    members,requires = get_members(item)
    
    source += members + "]\n\n"
    return [source,requires]
def json_to_bitarray(item):
    source = ""
    t = Template( """class {{name}}(ctypes.LittleEndianStructure):\n    \"""{{raw_comment}}""\"\n    _fields_ = [""")
    source += t.render(Context(item))
    members = get_bitarray_members(item['info'])
    source += members + "]\n\n"
    source = AlignRegex(source,'\("')
    source = AlignRegex(source,',')   
    return source
def get_bitarray_members(item):
    t = Template( """ ("{{name}}",{{basetype}},{{bits}})""")

    basetype = type_dictionary[item['basetype']]
    source = ""
    for bit_stuff in item['members'][:-1]:
        bit_stuff['basetype'] = basetype
        source += t.render(Context(bit_stuff)) + ",\n"
    last = item['members'][-1]
    last['basetype'] = basetype
    source += t.render(Context(last))
    
    return source
def json_to_ctype(item,depth=0):
    """Converts an item into a ctype.  Returns text, and required other objects that need to procceed this one."""
    required_types = []
    text = ""
    required = []
    if item['kind'] == CursorKind.STRUCT_DECL:
        text, required_types = json_to_record(item,depth=0)
    elif item['kind'] == CursorKind.UNION_DECL:
        text, required_types = json_to_union(item,depth=0)
    #TODO Those darn bit arrays...
    
    #Clean up the text so all of the (" are aligned properly..., and then align the commas
    text = AlignRegex(text,'\("')
    text = AlignRegex(text,',')    
    return [text,required_types]

def json_to_ctype_full(item,txt="",used=[]):
    if(item['name'] in used):
        return [txt,used]
    [item_txt, requires] = json_to_ctype(item)

    #Put item txt at the end
    for req_item in requires:
        if req_item['name'] in used:
            continue
        if req_item['bitarray'] == False:

            req_json = req_item['data'].type.get_canonical()
            #Filter out silly array stuff...
            while req_json.kind == TypeKind.CONSTANTARRAY:
                req_json = req_json.element_type.get_canonical()
            req_json =req_json.get_declaration()

            req_json = clang_to_json.process_item(req_json)
    
            [txt,used] = json_to_ctype_full(req_json,txt,used)
        else:
            bittxt = json_to_bitarray(req_item)
            used += [req_item['name']]

            txt = bittxt + txt
         
    txt =txt + item_txt
    used += [item['name']]
    return [txt,used]


if __name__ == "__main__":
    from pprint import pprint

    items = clang_to_json.process_file('../example_cpp/test.h')
    source = ""
    used = []
    for item in items:
        #Initially we only want the 
        if clang_to_json.comment_contains(item['comments'],'ingroup','MESSAGES'):
            [source, used] = json_to_ctype_full(item,source,used)

    print source
