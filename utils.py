import pandas as pd 


def build_midprice_from_df_OB(df_OB: pd.DataFrame,
                              time_col: str = 'Time',
                              ask_col: str = 'AskPrice_1',
                              bid_col: str = 'BidPrice_1',
                              price_scale: float = 10000.0) -> pd.DataFrame:
    """
    Return DataFrame with columns ['Time','midprice'].
    Assumes df_OB.index or a column contains timestamp in seconds after midnight (float).
    Prices in df_OB are integers scaled by e.g. 10000 -> we divide by price_scale.
    """
    # If there's no explicit Time column, we assume index holds it.
    if time_col in df_OB.columns:
        times = df_OB[time_col].values
    else:
        times = df_OB.index.values.astype(float)

    mid = 0.5 * (df_OB[ask_col].astype(float) + df_OB[bid_col].astype(float)) / price_scale
    out = pd.DataFrame({'Time': times, 'midprice': mid})
    out = out.sort_values('Time').reset_index(drop=True)
    return out

def to_regular_time_series(mid_df: pd.DataFrame, dt_seconds: float = 1.0) -> pd.DataFrame:
    """
    Resample the midprice onto a regular time grid with step dt_seconds.
    Time in mid_df['Time'] is assumed seconds after midnight (float).
    Returns DataFrame with index = DateTimeIndex (constructed from Time) and 'price'.
    """
    # Build a "datetime" index relative to arbitrary date (so plotting is nice)
    base = pd.to_datetime('2020-01-01')  # day doesn't matter
    times = base + pd.to_timedelta(mid_df['Time'], unit='s')
    s = pd.Series(mid_df['midprice'].values, index=times)
    # forward-fill to get a continuous series, then resample
    s = s.resample(f'{int(dt_seconds*1000)}L').ffill()  # milliseconds
    df = s.to_frame(name='price').dropna()
    return df