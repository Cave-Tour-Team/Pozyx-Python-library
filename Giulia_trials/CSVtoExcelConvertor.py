from xlwt import Workbook
import xlsxwriter

wb = xlsxwriter.Workbook('results.xlsx')
worksheet = wb.add_worksheet()
old = open('results.csv', mode='r') # csv file with results


worksheet.write('A1', 'ms')
worksheet.write('B1', 'mm')
worksheet.write('C1', 'dBm')

j = 1
for row in old:
    row = row.replace('"', '')
    lista = row.split(",")
    i = 0
    for word in lista:
        worksheet.write(j, i, word)
        i+=1
    j+=1

wb.close()
old.close()
