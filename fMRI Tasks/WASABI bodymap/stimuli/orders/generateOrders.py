import random
import csv
import pandas as pd

# Include every combination of Non-stimulation followed by Stimulation trials, resulting in 10 stimulation trials and 11 non stimulation trials per condition
# 10 heat trials (1)
# 10 warm trials (2)
# 11 imagination trials (3)
# 11 rest trials (4)
# A consequence of this is we always start with a Non-stimulation trial
trials = [(3,1,3),(3,1,4),(3,2,3),(3,2,4),
        (4,1,3),(4,1,4),(4,2,3),(4,2,4),
        (3,1),(3,1),(3,1),
        (4,1),(4,1),(4,1),
        (3,2),(3,2),(3,2),
        (4,2),(4,2),(4,2)]

for i in range(16):
    random.shuffle(trials)
    # For testing: using list comprehension
    # print([item for t in trials for item in t])
    out = [item for t in trials for item in t]
    df = pd.DataFrame(out)
    df.columns=['trial_type']
    df.to_excel('stimOrder'+str(i+1)+'.xlsx', index=False)