from xlwt import Workbook
wb = Workbook()
sheet1 = wb.add_sheet('new1') # add_sheet is used to create sheet.
old = open('results.csv', mode='r') # csv file with results

j = 0
for row in old:
    row = row.replace('"', '')
    lista = row.split(",")
    i = 0
    for word in lista:
        sheet1.write(j, i, word)
        i+=1
    j += 1

wb.save('results.xls')
old.close()
