import re
#TODO count tabs? 
def AlignRegex(text, regex):
    """Aligns some text based on a regular expression.  Spaces are inserted until proper alignment is reached."""
    max_spot = {}
    max_spot['start'] = 0
    #Step 1 figure out max position
    lines = text.split('\n')
    regex = '(\s*)' + regex
    spots = []
    for line in lines:
        m = re.search( regex, line)
        if m == None:
            spots.append(0)
            continue
        spot = {}
        start =  m.start(0)
        spot['start'] = start
        #Trim off extra whitespace...
        spot['end']   = start + len(m.group(1))
        
        spots.append(spot)
        if spot['start'] > max_spot['start']:
            max_spot = spot
    
    #Step 2 make the new output.
    ind = 0
    output = ""
    for line in lines:
        if(spots[ind] == 0):
            output += line + '\n'
            ind +=1
            continue
        start = line[:spots[ind]['start']]
        end = line[spots[ind]['end']:]
        
        output += start
        
        for dum in range(max_spot['start'] - spots[ind]['start']+1):
            output += ' '
        
        output += end + '\n'
        
        ind +=1
    
    #Last character shouldnt have been added
    return output[0:-1]
if  __name__ == "__main__":
    text = """
    int blah                  = 55555; //taco tuesday
abc
    uint32 blah2 = 59283;          //waca
    uint8 hihi = yay; //Sweet
    """
    print text
    text = AlignRegex(text, "=")
    print AlignRegex(text, "//")
