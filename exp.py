import pandas as pd
import numpy as np
import re
from glob import glob
import os

a = np.array([1, 2, 3, 4, 5])
b = np.array([1, 2, 3, 4, 5])
c = np.array([1, 2, 3, 4, 5])

df = pd.DataFrame({'a': a, 'b': b, 'c': c})

print(df)

d = np.array([1, 2, 3, 4, 5])

list_ = [1, 2, 3, 4, 5]

txt = "芝3200"

distance = re.search(r'\d+', txt).group()
print(distance)

data_dir = "jra_race_data"

files = glob(f"{data_dir}/*")
file = files[0]
print(os.path.basename(file))

list_ = [1, 2, 3, 4, 5]
target = 1

if target in list_:
    print("OK")
