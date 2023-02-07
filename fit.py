import numpy as np


# polynomial fit with n degree
def polyfit(x, y, degree):
    model = np.poly1d(np.polyfit(x, y, degree))
    return model


