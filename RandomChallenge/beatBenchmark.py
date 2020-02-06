
import pandas as pd

OFFSET = 1000000

ids    = [x         for x in range(10000)]
values = [x+OFFSET for x in range(10000)]

out = pd.DataFrame({"Id":ids,"Predicted":values})
out.to_csv("beatBenchmark.csv",index=False)

