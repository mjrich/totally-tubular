crs = open("country_codes.txt", "r")
for columns in ( raw.strip().split('\t') for raw in crs ):
    print '<option value="%s">%s</option>' % (columns[1], columns[0])
