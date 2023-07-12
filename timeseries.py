import pandas as pd 
from glob import glob
import matplotlib.pyplot as plt 

dir = 'citation_data/'


plots = pd.DataFrame()
for file in glob(dir+'*'):
    name = file.split('/')[1].split('__')[0]
    print(name)
    df = pd.read_csv(file)
    # counts = df.groupby('year').count().values[:,0]

    cumsum  = df.groupby('year').count().cumsum().mean(axis=1)

    plots[name] = cumsum.fillna(0)


plots.plot()
plt.show()