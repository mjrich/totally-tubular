#def thousand_separator(string):
#	str_len = len(string)
#	num_commas = str_len / 3


#thousand_separator('1000')

def splitthousands(s, sep=','):  
    if len(s) <= 3: return s  
    return splitthousands(s[:-3], sep) + sep + s[-3:]


string_num = '1000002828729'

print splitthousands(string_num,',')
