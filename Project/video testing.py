a = "agr\rhfj"
print(a)

import string as ammo
gun = list(ammo.ascii_uppercase)
print(gun.pop())

rainbow = ["blue", "red", "yellow", "purple", "green", "cyan", "pink"]
import matplotlib.pyplot as plt
import numpy as np
val = np.random.randint(1,10,10)


plt.bar(range(len(val)), val, color = rainbow)
plt.title(label='TEST', fontsize = 20, loc='center', color = 'blue', fontname = 'Consolas', rotation = 90)


x = np.arange(0,10,0.1)
y=np.cos(x)
plt.plot(x,y)
plt.show()

# while True:
#     val = np.random.randint(1,10,10)
#     plt.bar(range(len(val)), val)
#     plt.show()
print(*val)