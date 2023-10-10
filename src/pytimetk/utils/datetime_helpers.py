import pandas as pd
import numpy as np
import pandas_flavor as pf

import re
from datetime import datetime
from dateutil import parser
from warnings import warn
from typing import Union, List

from pytimetk.utils.checks import check_series_or_datetime

try: 
    import holidays
except ImportError:
    pass


@pf.register_series_method
def floor_date(
    idx: Union[pd.Series, pd.DatetimeIndex], 
    unit: str = "D",
) -> pd.Series:
    '''Round a date down to the specified unit (e.g. Flooring).
    
    The `floor_date` function takes a pandas Series of dates and returns a new Series with the dates rounded down to the specified unit.
    
    Parameters
    ----------
    idx : pd.Series or pd.DatetimeIndex
        The `idx` parameter is a pandas Series or pandas DatetimeIndex object that contains datetime values. It represents the dates that you want to round down.
    unit : str, optional
        The `unit` parameter in the `floor_date` function is a string that specifies the time unit to which the dates in the `idx` series should be rounded down. It has a default value of "D", which stands for day. Other possible values for the `unit` parameter could be
    
    Returns
    -------
    pd.Series 
        The `floor_date` function returns a pandas Series object containing datetime64[ns] values.
    
    Examples
    --------
    ```{python}
    import pytimetk as tk
    import pandas as pd
    
    dates = pd.date_range("2020-01-01", "2020-01-10", freq="1H")
    dates
    ```
    
    ```{python}
    # Works on DateTimeIndex
    tk.floor_date(dates, unit="D")
    ```
    
    ```{python}
    # Works on Pandas Series
    dates.to_series().floor_date(unit="D")
    ```
    '''
    # Common checks
    check_series_or_datetime(idx)
    
    # If idx is a DatetimeIndex, convert to Series
    if isinstance(idx, pd.DatetimeIndex):
        idx = pd.Series(idx, name="idx")
    
    # Fix for pandas bug: When unit is greater than the frequency of the index, the floor function returns the first day of the year
    days_in_sequence = idx.iloc[-1] - idx.iloc[0]
    days_in_unit = freq_to_timedelta(unit)
    
    if days_in_unit > days_in_sequence:
        # fill series with first value
        idx.iloc[1:] = idx.iloc[0]
        
    # Convert to period
    nm = idx.name
    date = pd.Series(
        pd.PeriodIndex(idx.values, freq = unit).to_timestamp(),
        name=nm
    )       

    return date

@pf.register_series_method
def ceil_date(
    idx: Union[pd.Series, pd.DatetimeIndex], 
    unit: str = "D",
) -> pd.Series:
    '''Round a date up to the specified unit (e.g. Ceiling).
    
    The `ceil_date` function takes a pandas Series of dates and returns a new Series with the dates rounded down to the specified unit.
    
    Parameters
    ----------
    idx : pd.Series or pd.DatetimeIndex
        The `idx` parameter is a pandas Series or pandas DatetimeIndex object that contains datetime values. It represents the dates that you want to round down.
    unit : str, optional
        The `unit` parameter in the `ceil_date` function is a string that specifies the time unit to which the dates in the `idx` series should be rounded down. It has a default value of "D", which stands for day. Other possible values for the `unit` parameter could be
    
    Returns
    -------
    pd.Series 
        The `ceil_date` function returns a pandas Series object containing datetime64[ns] values.
    
    Examples
    --------
    ```{python}
    import pytimetk as tk
    import pandas as pd
    
    dates = pd.date_range("2020-01-01", "2020-01-10", freq="1H")
    dates
    ```
    
    ```{python}
    # Works on DateTimeIndex
    tk.ceil_date(dates, unit="D")
    ```
    
    ```{python}
    # Works on Pandas Series
    dates.to_series().ceil_date(unit="D")
    ```
    '''
    # Common checks
    check_series_or_datetime(idx)
    
    # If idx is a DatetimeIndex, convert to Series
    if isinstance(idx, pd.DatetimeIndex):
        idx = pd.Series(idx, name="idx")
    
    # Convert to period
    date = idx.dt.ceil(unit)

    return date



def freq_to_timedelta(freq_str):
    # Adjusted regex to account for potential absence of numeric part
    match = re.match(r'(\d+)?([A-Z]+)', freq_str)
    if not match:
        raise ValueError(f"Invalid frequency string: {freq_str}")
    
    quantity, unit = match.groups()
    
    # Assume quantity of 1 if it's not explicitly provided
    quantity = int(quantity) if quantity else 1
    
    if unit == 'D':  # Days
        return pd.Timedelta(days=quantity)
    elif unit == 'H':  # Hours
        return pd.Timedelta(hours=quantity)
    elif unit == 'T' or unit == 'min':  # Minutes
        return pd.Timedelta(minutes=quantity)
    elif unit == 'S':  # Seconds
        return pd.Timedelta(seconds=quantity)
    elif unit == 'L' or unit == 'U':  # Milliseconds
        return pd.Timedelta(milliseconds=quantity)
    elif unit == 'N':  # Nanoseconds
        return pd.Timedelta(nanoseconds=quantity)
    elif unit in ['Y', 'A', 'AS', 'YS']:  # Years (approximated as 365.25 days per year)
        return pd.Timedelta(days=quantity*365.25)
    elif unit == 'W':  # Weeks
        return pd.Timedelta(weeks=quantity)
    elif unit in ['Q', 'QS']:  # Quarters (approximated as 3*30.44 days)
        return pd.Timedelta(days=quantity*3*30.44)
    elif unit in ['M', 'MS']:  # Months (approximated as 30.44 days)
        return pd.Timedelta(days=quantity*30.44)
    # ... add other units if needed
    else:
        raise ValueError(f"Unsupported frequency unit: {unit}")


@pf.register_series_method
def week_of_month(idx: Union[pd.Series, pd.DatetimeIndex]) -> pd.Series:
    '''The "week_of_month" function calculates the week number of a given date within its month.
    
    Parameters
    ----------
    idx : pd.Series or pd.DatetimeIndex
        The parameter "idx" is a pandas Series object that represents a specific date for which you want to determine the week of the month.
    
    Returns
    -------
    pd.Series
        The week of the month for a given date.
    
    Examples
    --------
    ```{python}
    import pytimetk as tk
    import pandas as pd
    
    dates = pd.date_range("2020-01-01", "2020-02-28", freq="1D")
    dates
    ```
    
    ```{python}
    # Works on DateTimeIndex
    tk.week_of_month(dates)
    ```
    
    ```{python}
    # Works on Pandas Series
    dates.to_series().week_of_month()
    ```
    
    '''
    # Common checks
    check_series_or_datetime(idx)
    
    if isinstance(idx, pd.DatetimeIndex):
        idx = pd.Series(idx, name="idx")
    
    ret = (idx.dt.day - 1) // 7 + 1
    
    ret = pd.Series(
        ret, 
        name="week_of_month", 
        index = idx.index
    )
    
    return ret


@pf.register_series_method
def is_holiday(
    idx: Union[str, datetime, List[Union[str, datetime]], pd.DatetimeIndex, pd.Series],
    country_name: str = 'UnitedStates',
    country: str = None
) -> pd.Series:
    """
    Check if a given list of dates are holidays for a specified country.
    
    Note: This function requires the `holidays` package to be installed.

    Parameters
    ----------
    idx : Union[str, datetime, List[Union[str, datetime]], pd.DatetimeIndex, pd.Series]
        The dates to check for holiday status.
    country_name (str, optional):
        The name of the country for which to check the holiday status. Defaults to 'UnitedStates' if not specified.
    country (str, optional):
        An alternative parameter to specify the country for holiday checking, overriding country_name.

    Returns:
    -------
    pd.Series:
        Series containing True if the date is a holiday, False otherwise.

    Raises:
    -------
    ValueError:
        If the specified country is not found in the holidays package.

    Examples:
    --------
    ```{python}
    import pandas as pd
    import pytimetk as tk
    
    tk.is_holiday('2023-01-01', country_name='UnitedStates')
    ```
    
    ```{python}
    # List of dates
    tk.is_holiday(['2023-01-01', '2023-01-02', '2023-01-03'], country_name='UnitedStates')
    ```
    
    ```{python}
    # DatetimeIndex
    tk.is_holiday(pd.date_range("2023-01-01", "2023-01-03"), country_name='UnitedStates')
    ```
    
    ```{python}
    # Pandas Series Method
    ( 
        pd.Series(pd.date_range("2023-01-01", "2023-01-03"))
            .is_holiday(country_name='UnitedStates')
    )
    ```
    """
    
    # This function requires the holidays package to be installed
    try:
        import holidays
    except ImportError:
        raise ImportError("The 'holidays' package is not installed. Please install it by running 'pip install holidays'.")

    if country:
        country_name = country  # Override the default country_name with the provided one

    # Find the country module from the holidays package
    for key in holidays.__dict__.keys():
        if key.lower() == country_name.lower():
            country_module = holidays.__dict__[key]
            break
    else:
        raise ValueError(f"Country '{country_name}' not found in holidays package.")
    
    if isinstance(idx, str) or isinstance(idx, datetime):
        idx = [idx]
    
    idx = pd.to_datetime(idx)  # Convert all dates to pd.Timestamp if not already
    
    # Check each date if it's a holiday and return the results as a Series
    ret = pd.Series([date in country_module(years=date.year) for date in idx], name='is_holiday')
    
    return ret



def is_datetime_string(x: Union[str, pd.Series, pd.DatetimeIndex]) -> bool:
    
    if isinstance(x, pd.Series):
        x = x.values[0]
    
    if isinstance(x, pd.DatetimeIndex):
        x = x[0]
    
    try:
        parser.parse(str(x))
        return True
    except ValueError:
        return False
    
def detect_timeseries_columns(data: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    
    df = data.head(1)
    
    if verbose:
        print(df)
    
    return df.map(is_datetime_string)

def has_timeseries_columns(data: pd.DataFrame, verbose: bool = False) -> bool:
    
    if verbose:
        print(detect_timeseries_columns(data).iloc[0])
    
    return detect_timeseries_columns(data).iloc[0].any()

def get_timeseries_colname(data: pd.DataFrame, verbose: bool = False) -> str:
    
    if verbose:
        print(detect_timeseries_columns(data).iloc[0])
        
    return detect_timeseries_columns(data).iloc[0].idxmax()



