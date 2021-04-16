import random
import csv
import pandas as pd

trials = [(1,3),(1,3),(1,3),(1,3),
        (4,1,4),(4,1,4),(1,4),(1,4),
        (2,3),(2,3),(2,3),(2,3),
        (4,2,4),(4,2,4),(2,4),(2,4)]

for i in range(16):
    random.shuffle(trials)
    # using list comprehension
    out = [item for t in trials for item in t]
    df = pd.DataFrame(out)
    df.columns=['trial_type']
    df.to_excel('stimOrder'+str(i+1)+'.xlsx', index=False)


