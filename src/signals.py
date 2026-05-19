import pandas as pd
import numpy as np



def generate_signals(zscore, entry_z=2.0, stop_z=3.5):
    signals = pd.Series(index=zscore.index, data=0)

    position = 0

    for i in range(len(zscore)):
        z = zscore.iloc[i]

        if np.isnan(z):
            continue

        if position == 0:
            if z < -entry_z:
                position = 1
            elif z > entry_z:
                position = -1

        elif position == 1:
            if z >= 0 or z < -stop_z:
                position = 0

        elif position == -1:
            if z <= 0 or z > stop_z:
                position = 0

        signals.iloc[i] = position

    return signals