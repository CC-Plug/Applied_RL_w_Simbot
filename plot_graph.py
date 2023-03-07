import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style


# dataplot1 = []
# dataplot2 = []

# import csv

# x = []
# y = []

# with open('learning_score.csv','r') as csvfile:
#     plots = csv.reader(csvfile, delimiter=',')
#     for row in plots:
#         x.append(int(row[1]))
#         y.append(int(row[2]))

# plt.plot(x,y, label='Loaded from file!')
# plt.xlabel('x')
# plt.ylabel('y')
# plt.title('Interesting Graph\nCheck it out')
# plt.legend()
# plt.show()

# import numpy as np

# x, y = np.loadtxt('learning_score.csv', delimiter=',', unpack=True)
# plt.plot(x,y, label='Loaded from file!')

# plt.xlabel('x')
# plt.ylabel('y')
# plt.title('Interesting Graph\nCheck it out')
# plt.legend()
# plt.show()
import pandas as pd

df = pd.read_csv('learning_score-test-3.csv')

print (df)
dataplot1 = df['eat_rate'].to_numpy()
dataplot2 = df['hit_rate'].to_numpy()

plt.plot(dataplot1)
plt.title('Eat-Rate per iterations(61070507229), seed 123')
plt.show()
plt.plot(dataplot2)
plt.title('Hit-Rate per iterations(61070507229), seed 123')
plt.show()