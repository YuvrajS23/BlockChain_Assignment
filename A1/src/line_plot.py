import matplotlib.pyplot as plt

# Data for the first line graph
x1 = [0.1, 0.2, 0.3, 0.4, 0.5]
y2 = [0.07353, 0.24138, 0.36538, 0.37500, 0.80769]

# Data for the second line graph
y1 = [0.09091, 0.02500, 0.33333, 0.54167, 0.94737]

# Plotting the first line graph
plt.plot(x1, y1, label='zeta_2 = 0.0')

# Plotting the second line graph
plt.plot(x1, y2, label='zeta_2 = 0.3')

# Adding labels and title
plt.xlabel('zeta_1')
plt.ylabel('R_pool of Adversary1')
plt.title('Variation of R_pool_adv1 with zeta_2 and zeta_1')

# Adding legend
plt.legend()

# Displaying the plot
plt.savefig('LinePlot.png')
