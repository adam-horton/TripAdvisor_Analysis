import pandas as pd


def concatenate(name, sheets):    
    frames = []

    for x in range(0, len(sheets)):
        frames.append(pd.read_excel(sheets[x], usecols = 'B:R'))

    merger = pd.concat(frames, ignore_index=True)

    merger.to_excel(name)
