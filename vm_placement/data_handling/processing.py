import pandas as pd

resource_columns = ['vCPU', 'Memory', 'Storage']


def duplicate_entry(data: pd.DataFrame, n_times: int) -> pd.DataFrame:
    return pd.concat([data] * n_times, ignore_index=True)


