import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_excel('results.xlsx')
range = df['mm'].tolist()

print("PLEASE, ENTER THE CALCULATED RANGE or press D to continue with the default one (1810 mm).")
resulted_range = input()
if resulted_range == 'D':
    resulted_range = 1810

# plotting the error
print("PLOTTING THE ERROR")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_excel('results.xlsx')
range = df['mm'].tolist()

abs_error_list = []
error_list = []

for element in range:
    cent = (element - resulted_range)/10
    abs_error_list.append(abs(cent))
    error_list.append(cent)

step = 200
a = min(0.3, min(abs_error_list) )
error_list = sorted(error_list)
mean_abs = np.mean(abs_error_list)
mean_real = np.mean(error_list)

fig = plt.figure()
plt.hist(abs_error_list, histtype='bar', label='abs values', rwidth=a+0.1, orientation='vertical', alpha=0.5)
plt.hist(error_list, histtype='bar', label='real values', rwidth=a+0.1, orientation='vertical', alpha=0.7)
plt.xlabel('error (cm)')
plt.axvline(mean_real, color='red', linestyle='-.', linewidth=3, label='mean error (real)')
plt.axvline(mean_abs, color='blue', linewidth=3, linestyle='-.',  label='mean error (abs)')

plt.legend()
# plt.xticks(np.arange(min(error_list), max(error_list), step))
plt.ylabel('# occurrences')
plt.grid(True, which='both')
plt.title('error for range'+str(resulted_range)+'cm')
plt.show()
fig.savefig('./error.png')