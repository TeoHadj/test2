import numpy as np
from math import sqrt




def mod(lst):
    magnitude = 0
    initial_sum = 0
    for num in lst:
        initial_sum += num**2
    magnitude = sqrt(initial_sum)

    return magnitude

def cosine_similarity(list1, list2): #closer to 1 the better
    dotted = np.dot(list1, list2)
    mod1 = mod(list1)
    mod2 = mod(list2)
    similarity_value = dotted/(mod1*mod2)

    return float(round(similarity_value, 3))