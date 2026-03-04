

import pandas as pd
import numpy as np
from scipy import interpolate
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge, Lasso, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
import warnings
warnings.filterwarnings('ignore')
from io import BytesIO

def interpolate_col(pdf, df, peak_year=2023, columns='None', method='linear'):
    """
    Interpolate missing values in the pivot DataFrame `pdf` using the specified method.

    Parameters:
    - pdf: pivot DataFrame with countries as index and metrics as columns (including 'source' and 'assumptions')
    - df: original DataFrame (not used directly here but kept for compatibility)
    - peak_year: year used for filtering or reference (not used here but kept for compatibility)
    - columns: list of columns to interpolate or 'None' to interpolate all numeric columns
    - method: interpolation method as string

    Returns:
    - DataFrame with interpolated values
    """
    # Copy to avoid modifying original
    df_interp = pdf.copy()

    # Select columns to interpolate
    if columns == 'None':
        # Select numeric columns only (exclude 'source' and 'assumptions')
        cols_to_interp = df_interp.select_dtypes(include=[np.number]).columns.tolist()
    else:
        cols_to_interp = columns

    # Define supported methods mapping to pandas interpolate methods or custom
    pandas_methods = ['linear', 'polynomial', 'spline', 'nearest', 'pad', 'ffill', 'bfill']
    # Map your method names to pandas or custom
    method_map = {
        'linear': 'linear',
        'polynomial': 'polynomial',
        'spline': 'spline',
        'nearest_neighbour': 'nearest',
        'piecewise_constant': 'pad',  # forward fill as piecewise constant approx
        'logarithmic': 'logarithmic'  # custom implementation below
    }

    if method not in method_map:
        raise ValueError(f"Interpolation method '{method}' not supported.")

    interp_method = method_map[method]

    # For polynomial and spline, define order
    order = 2

    # Interpolate each column separately
    for col in cols_to_interp:
        series = df_interp[col]

        if series.isnull().all():
            # Skip columns with all NaNs
            continue

        if interp_method == 'logarithmic':
            # Custom logarithmic interpolation:
            # Interpolate on log scale, then exponentiate back
            # Handle zeros or negative values by shifting data if needed
            s = series.copy()
            # Shift to positive if needed
            min_val = s.min()
            shift = 0
            if min_val <= 0:
                shift = abs(min_val) + 1
                s = s + shift

            # Log transform
            s_log = np.log(s)

            # Interpolate on log scale using linear method
            s_log_interp = s_log.interpolate(method='linear', limit_direction='both')

            # Exponentiate back and shift
            s_interp = np.exp(s_log_interp) - shift

            df_interp[col] = s_interp

        elif interp_method in ['polynomial', 'spline']:
            # Use pandas interpolate with order
            try:
                df_interp[col] = series.interpolate(method=interp_method, order=order, limit_direction='both')
            except Exception as e:
                # fallback to linear if polynomial/spline fails
                df_interp[col] = series.interpolate(method='linear', limit_direction='both')

        else:
            # Use pandas interpolate for other methods
            # Note: pandas interpolate does not support 'nearest_neighbour' but supports 'nearest'
            # 'piecewise_constant' approximated by 'pad' (forward fill)
            try:
                df_interp[col] = series.interpolate(method=interp_method, limit_direction='both')
            except Exception as e:
                # fallback to linear if error
                df_interp[col] = series.interpolate(method='linear', limit_direction='both')

    return df_interp

def cagr(start, end, periods):
    """Compound Annual Growth Rate"""
    return (end / start) ** (1 / periods) - 1 if start > 0 and periods > 0 else 0

def extrapolate_col(pdf, df, peak_year=2023, columns='None', method='linear', order=2, ma_window=3):
    """
    Extrapolate missing values in pdf for peak_year, using historical data from df
    Methods: 'cagr', 'linear_regression', 'polynomial_regression', 'moving_average_growth', 'arima'
    """
    import warnings
    warnings.filterwarnings("ignore")
    
    df_extrap = pdf.copy()

    if columns == 'None':
        cols_to_extrap = df_extrap.select_dtypes(include=[np.number]).columns.tolist()
    else:
        cols_to_extrap = columns

    for country in df_extrap.index:
        for col in cols_to_extrap:
            mask = (df['country'] == country) & (df['metric'] == col)
            hist = df[mask].sort_values('year')
            years = hist['year'].values
            values = hist['value'].values

            # Only extrapolate if missing
            if pd.isnull(df_extrap.loc[country, col]) and len(years) >= 2:
                target_year = peak_year

                if method == 'cagr':
                    # Use only first and last actual values
                    start, end = values[0], values[-1]
                    periods = years[-1] - years[0]
                    if start > 0 and periods > 0:
                        growth_rate = cagr(start, end, periods)
                        n_extrap = target_year - years[-1]
                        if n_extrap > 0:
                            y_pred = end * ((1 + growth_rate) ** n_extrap)
                            df_extrap.loc[country, col] = y_pred

                elif method == 'linear_regression':
                    # y = beta0 + beta1 * year
                    beta = np.polyfit(years, values, 1)
                    y_pred = np.polyval(beta, target_year)
                    df_extrap.loc[country, col] = y_pred

                elif method == 'polynomial_regression':
                    deg = order if len(years) > order else 2
                    beta = np.polyfit(years, values, deg)
                    y_pred = np.polyval(beta, target_year)
                    df_extrap.loc[country, col] = y_pred

                elif method == 'moving_average_growth':
                    # Compute yearly growth rates, moving average, then extrapolate
                    if len(values) >= ma_window + 1:
                        growth_rates = values[1:] / values[:-1] - 1
                        avg_growth = pd.Series(growth_rates).rolling(ma_window).mean().iloc[-1]
                        if np.isnan(avg_growth):
                            avg_growth = np.mean(growth_rates)
                        n_extrap = target_year - years[-1]
                        y_pred = values[-1] * ((1 + avg_growth) ** n_extrap)
                        df_extrap.loc[country, col] = y_pred

                elif method == 'arima':
                    try:
                        from statsmodels.tsa.arima.model import ARIMA
                        if len(values) > 3:  # ARIMA needs more data
                            years_full = np.arange(years[0], target_year + 1)
                            n_extrap = target_year - years[-1]
                            model = ARIMA(values, order=(1,1,0))
                            model_fit = model.fit()
                            forecast = model_fit.forecast(steps=n_extrap)
                            y_pred = forecast.values[-1]
                            df_extrap.loc[country, col] = y_pred
                    except ImportError:
                        # No statsmodels installed
                        pass
                # You can add more methods!
    return df_extrap

def regression_analysis(years, values, target_year, method='linear', poly_order=2, C=1.0, alpha=1.0, hidden_layer_sizes=(10,)):
    # Converts years and values to proper numpy arrays
    X = np.array(years).reshape(-1, 1)
    y = np.array(values)
    X_pred = np.array([[target_year]])

    def perform_linear_regression():
        model = LinearRegression()
        model.fit(X, y)
        return model.predict(X_pred)[0]

    def perform_polynomial_regression():
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.linear_model import LinearRegression
        pf = PolynomialFeatures(degree=poly_order)
        X_poly = pf.fit_transform(X)
        X_pred_poly = pf.transform(X_pred)
        model = LinearRegression()
        model.fit(X_poly, y)
        return model.predict(X_pred_poly)[0]

    def perform_ridge_regression():
        model = Ridge(alpha=alpha)
        model.fit(X, y)
        return model.predict(X_pred)[0]

    def perform_lasso_regression():
        model = Lasso(alpha=alpha)
        model.fit(X, y)
        return model.predict(X_pred)[0]

    def perform_logistic_regression():
        # For binary response; convert y to labels if necessary
        model = LogisticRegression(C=C)
        y_bin = (y > np.median(y)).astype(int)  # Example binarization
        model.fit(X, y_bin)
        return model.predict(X_pred)[0]

    def perform_decision_tree_regression():
        model = DecisionTreeRegressor()
        model.fit(X, y)
        return model.predict(X_pred)[0]

    def perform_random_forest_regression():
        model = RandomForestRegressor()
        model.fit(X, y)
        return model.predict(X_pred)[0]

    def perform_svm_regression():
        model = SVR(C=C)
        model.fit(X, y)
        return model.predict(X_pred)[0]

    def perform_neural_network_regression():
        model = MLPRegressor(hidden_layer_sizes=hidden_layer_sizes, max_iter=1000)
        model.fit(X, y)
        return model.predict(X_pred)[0]

    method_dispatch = {
        'linear': perform_linear_regression,
        'polynomial': perform_polynomial_regression,
        'ridge': perform_ridge_regression,
        'lasso': perform_lasso_regression,
        'logistic': perform_logistic_regression,
        'decision_tree': perform_decision_tree_regression,
        'random_forest': perform_random_forest_regression,
        'svm': perform_svm_regression,
        'neural_network': perform_neural_network_regression,
    }

    if method not in method_dispatch:
        raise ValueError(f"Unknown regression method: {method}")

    return method_dispatch[method]()

#Function that has straight up same values:
def df_format1(file_name, sheet_name='Sheet1', column_mapping=None, header=0, usecols=None, is_excel=True):
    from pandas import read_excel, read_csv
    
    try:
        # Read the data
        if is_excel:
            df = read_excel(file_name, sheet_name=sheet_name, header=header, usecols=usecols)
        else:
            df = read_csv(file_name, header=header, usecols=usecols)
        
        # Apply column mapping if provided
        if column_mapping:
            df = df.rename(columns=column_mapping)
            print(f"Columns renamed using mapping: {column_mapping}")
        
        print(f"Final columns: {list(df.columns)}")
        return df
        
    except Exception as e:
        print(f"Error reading or transforming file: {e}")
        raise

#Function that has different years as columns
def df_format2(file_name, sheet_name='Sheet1', header=0, usecols=None, is_excel=True):
    from pandas import read_excel, read_csv
    
    try:
        # Read the data
        if is_excel:
            df = read_excel(file_name, sheet_name=sheet_name, header=header, usecols=usecols)
        else:
            df = read_csv(file_name, header=header, usecols=usecols)
        
        # Transform to long format using the row-based function
        transformed_df = transform_rows_to_long_format(df)
        
        return transformed_df
        
    except Exception as e:
        print(f"Error reading or transforming file: {e}")
        raise

def transform_rows_to_long_format(df):
    import pandas as pd
    import re
    
    # Debug: Print structure
    print("Column names:", df.columns.tolist())
    print("First 3 rows:")
    print(df.head(3))
    
    # Find country column
    country_col = None
    for col in df.columns:
        if 'country' in str(col).lower():
            country_col = col
            break
    
    if country_col is None:
        print("Available columns:")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col} - Sample values: {df[col].dropna().head(3).tolist()}")
        # Manually specify if needed
        country_col = df.columns[0]  # Change this index if needed
        print(f"Using column: {country_col}")
    
    print(f"Selected country column: {country_col}")
    
    # Find parameter/metric column
    param_col = None
    for col in df.columns:
        if any(keyword in str(col).lower() for keyword in ['parameter', 'metric', 'variable', 'indicator']):
            param_col = col
            break
    
    if param_col is None:
        # Look for a column that seems to contain parameter names
        for col in df.columns:
            if col != country_col and df[col].dtype == 'object':
                sample_values = df[col].dropna().astype(str).head(5)
                if any(len(str(val)) > 5 for val in sample_values):  # Assuming parameter names are longer
                    param_col = col
                    break
    
    if param_col is None:
        print("Available columns for parameters:")
        for i, col in enumerate(df.columns):
            if col != country_col:
                print(f"{i}: {col} - Sample values: {df[col].dropna().head(3).tolist()}")
        param_col = df.columns[1]  # Default to second column
        print(f"Using parameter column: {param_col}")
    
    print(f"Selected parameter column: {param_col}")
    
    # Find year columns (Y1 2021, Y2 2022, etc.)
    year_columns = []
    for col in df.columns:
        if col not in [country_col, param_col]:
            # Extract year from column name
            year_match = re.search(r'(19\d{2}|20\d{2})', str(col))
            if year_match:
                year_columns.append({
                    'column': col,
                    'year': int(year_match.group(1))
                })
    
    print(f"Found year columns: {[(yc['column'], yc['year']) for yc in year_columns]}")
    
    # Create long format data
    long_format_data = []
    
    for _, row in df.iterrows():
        country = row[country_col]
        parameter = row[param_col]
        
        # Skip if country or parameter is null/empty
        if pd.isna(country) or pd.isna(parameter):
            continue
            
        # Skip if parameter is empty string
        if str(parameter).strip() == '':
            continue
        
        # Process each year column
        for year_col_info in year_columns:
            col_name = year_col_info['column']
            year = year_col_info['year']
            value = row[col_name]
            
            # Skip if value is null, empty, or zero
            if pd.isna(value) or value == '' or value == 0:
                continue
                
            # Convert to float if possible
            try:
                value = float(value)
                # Skip if value is zero (after conversion)
                if value == 0:
                    continue
            except (ValueError, TypeError):
                # Keep as string if can't convert to float
                pass
            
            long_row = {
                'country': str(country).strip(),
                'year': year,
                'metric': str(parameter).strip(),
                'value': value,
                'source': 'Original Dataset',
                'assumption': None
            }
            long_format_data.append(long_row)
    
    # Create the final dataframe
    result_df = pd.DataFrame(long_format_data)
    
    print(f"\nOriginal shape: {df.shape}")
    print(f"Long format shape: {result_df.shape}")
    print(f"Countries found: {result_df['country'].nunique()}")
    print(f"Parameters found: {result_df['metric'].nunique()}")
    print(f"Years found: {sorted(result_df['year'].unique())}")
    
    return result_df

#Function that has different metrics as columns and years as rows
def df_format3(file_name, sheet_name='Sheet1', header=0, usecols=None, is_excel=True):
    from pandas import read_excel, read_csv
    
    try:
        # Read the data
        if is_excel:
            df = read_excel(file_name, sheet_name=sheet_name, header=header, usecols=usecols)
        else:
            df = read_csv(file_name, header=header, usecols=usecols)
        
        # Transform to long format using the metrics-as-columns function
        transformed_df = transform_metrics_columns_to_long_format(df)
        
        return transformed_df
        
    except Exception as e:
        print(f"Error reading or transforming file: {e}")
        raise

def transform_metrics_columns_to_long_format(df):
    import pandas as pd
    import re
    
    # Debug: Print structure
    print("Column names:", df.columns.tolist())
    print("First 3 rows:")
    print(df.head(3))
    
    # Find country column
    country_col = None
    for col in df.columns:
        if 'country' in str(col).lower():
            country_col = col
            break
    
    if country_col is None:
        print("Available columns:")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col} - Sample values: {df[col].dropna().head(3).tolist()}")
        country_col = df.columns[0]  # Default to first column
        print(f"Using column: {country_col}")
    
    print(f"Selected country column: {country_col}")
    
    # Find year column
    year_col = None
    for col in df.columns:
        if any(keyword in str(col).lower() for keyword in ['year', 'period', 'date', 'time']):
            year_col = col
            break
    
    if year_col is None:
        # Look for a column that seems to contain years
        for col in df.columns:
            if col != country_col:
                sample_values = df[col].dropna().astype(str).head(5)
                if any(re.search(r'(19\d{2}|20\d{2})', str(val)) for val in sample_values):
                    year_col = col
                    break
    
    if year_col is None:
        print("Available columns for years:")
        for i, col in enumerate(df.columns):
            if col != country_col:
                print(f"{i}: {col} - Sample values: {df[col].dropna().head(3).tolist()}")
        year_col = df.columns[1]  # Default to second column
        print(f"Using year column: {year_col}")
    
    print(f"Selected year column: {year_col}")
    
    # Find metric columns (everything except country and year)
    metric_columns = []
    for col in df.columns:
        if col not in [country_col, year_col]:
            metric_columns.append(col)
    
    print(f"Found metric columns: {metric_columns}")
    
    # Create long format data
    long_format_data = []
    
    for _, row in df.iterrows():
        country = row[country_col]
        year_value = row[year_col]
        
        # Skip if country or year is null/empty
        if pd.isna(country) or pd.isna(year_value):
            continue
            
        # Skip if country is empty string
        if str(country).strip() == '':
            continue
        
        # Extract year from year_value if it's not already a clean year
        if isinstance(year_value, str):
            year_match = re.search(r'(19\d{2}|20\d{2})', str(year_value))
            if year_match:
                year = int(year_match.group(1))
            else:
                try:
                    year = int(year_value)
                except ValueError:
                    continue
        else:
            try:
                year = int(year_value)
            except (ValueError, TypeError):
                continue
        
        # Process each metric column
        for metric_col in metric_columns:
            value = row[metric_col]
            
            # Skip if value is null, empty, or zero
            if pd.isna(value) or value == '' or value == 0:
                continue
                
            # Convert to float if possible
            try:
                value = float(value)
                # Skip if value is zero (after conversion)
                if value == 0:
                    continue
            except (ValueError, TypeError):
                # Keep as string if can't convert to float
                pass
            
            long_row = {
                'country': str(country).strip(),
                'year': year,
                'metric': str(metric_col).strip(),
                'value': value,
                'source': 'Original Dataset',
                'assumption': None
            }
            long_format_data.append(long_row)
    
    # Create the final dataframe
    result_df = pd.DataFrame(long_format_data)
    
    print(f"\nOriginal shape: {df.shape}")
    print(f"Long format shape: {result_df.shape}")
    print(f"Countries found: {result_df['country'].nunique()}")
    print(f"Metrics found: {result_df['metric'].nunique()}")
    print(f"Years found: {sorted(result_df['year'].unique())}")
    
    return result_df

#Function that has parameters in cols with labels having the year
def df_format4(file_name, sheet_name='Sheet1', header=0, usecols=None, is_excel=True):
    from pandas import read_excel, read_csv
    
    try:
        # Read the data
        if is_excel:
            df = read_excel(file_name, sheet_name=sheet_name, header=header, usecols=usecols)
        else:
            df = read_csv(file_name, header=header, usecols=usecols)
        
        # Transform to long format
        transformed_df = transform_cols_to_long_format(df)
        
        return transformed_df
        
    except Exception as e:
        print(f"Error reading or transforming file: {e}")
        raise

def transform_cols_to_long_format(df):
    import pandas as pd
    import re
    
    # Debug: Print column names and first few rows
    print("Column names:", df.columns.tolist())
    print("First 3 rows:")
    print(df.head(3))
    
    # Extract years from column names
    years = []
    for col in df.columns:
        year_matches = re.findall(r'(19\d{2}|20\d{2})', str(col))
        years.extend([int(year) for year in year_matches])
    
    unique_years = sorted(list(set(years)))
    print(f"Found years: {unique_years}")
    
    # Create an empty list to store all rows
    long_format_data = []
    
    # IMPROVED COUNTRY COLUMN DETECTION
    country_col = None
    
    # Method 1: Look for column with 'country' in name
    for col in df.columns:
        if 'country' in str(col).lower():
            country_col = col
            break
    
    # Method 2: If no 'country' column, look for columns with country-like values
    if country_col is None:
        for col in df.columns:
            # Check if this column contains country-like strings
            sample_values = df[col].dropna().astype(str).head(10)
            if any(len(str(val)) > 2 and str(val).isalpha() for val in sample_values):
                country_col = col
                break
    
    # Method 3: Let user specify or use a specific column index
    if country_col is None:
        print("Available columns:")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col} - Sample values: {df[col].dropna().head(3).tolist()}")
        
        # You can manually specify the column here
        country_col = df.columns[0]  # Change this index if needed
        print(f"Using column: {country_col}")
    
    print(f"Selected country column: {country_col}")
    print(f"Sample country values: {df[country_col].dropna().head(5).tolist()}")
    
    # Define columns to skip (non-metric columns)
    skip_columns = [country_col]
    
    # Add other non-metric columns that should be skipped
    for col in df.columns:
        if any(keyword in str(col).lower() for keyword in ['country', 'mapped', 'income', 'level', 'index']):
            skip_columns.append(col)
    
    # Remove duplicates from skip_columns
    skip_columns = list(set(skip_columns))
    
    # Iterate through each row in the dataframe
    for _, row in df.iterrows():
        country = row[country_col]
        
        # Skip if country is NaN or empty
        if pd.isna(country) or str(country).strip() == '':
            continue
        
        # Process each metric column
        for col in df.columns:
            if col in skip_columns:
                continue
                
            value = row[col]
            
            # Skip if value is empty, NaN, or whitespace
            if pd.isna(value) or str(value).strip() == '':
                continue
            
            # Clean the value
            if isinstance(value, str):
                value = value.strip().replace(',', '')
            
            # Try to convert to numeric and check if it's zero
            try:
                numeric_value = float(value)
                # SKIP ZERO VALUES
                if numeric_value == 0:
                    continue
            except (ValueError, TypeError):
                # If can't convert to numeric, keep as string but skip if it's "0"
                if str(value).strip() == "0":
                    continue
            
            # Clean the metric name by removing years
            clean_metric = col
            for year in unique_years:
                clean_metric = clean_metric.replace(f'({year})', '').replace(f'-{year}', '').replace(f' {year}', '')
            clean_metric = clean_metric.strip()
            
            # Extract years from THIS specific column
            column_years = [int(year) for year in re.findall(r'(19\d{2}|20\d{2})', str(col))]
            
            if column_years:
                # Column has specific year(s) - create row only for those years
                for year in column_years:
                    long_row = {
                        'country': country,
                        'year': year,
                        'metric': clean_metric,
                        'value': value,
                        'source': 'Original Dataset',
                        'assumption': None
                    }
                    long_format_data.append(long_row)
            else:
                # Column has no specific year - create rows for all years found in dataset
                if unique_years:
                    for year in unique_years:
                        long_row = {
                            'country': country,
                            'year': year,
                            'metric': clean_metric,
                            'value': value,
                            'source': 'Original Dataset',
                            'assumption': None
                        }
                        long_format_data.append(long_row)
                else:
                    # No years found anywhere, create row with None
                    long_row = {
                        'country': country,
                        'year': None,
                        'metric': clean_metric,
                        'value': value,
                        'source': 'Original Dataset',
                        'assumption': None
                    }
                    long_format_data.append(long_row)
    
    # Create the final dataframe
    result_df = pd.DataFrame(long_format_data)
    
    return result_df

def pivot_with_assumptions(df, year):
    """
    Load CSV, filter by year, pivot metric values, and add a combined assumptions column per country.

    Returns:
    - pivot_df: DataFrame indexed by country, with metric columns and one 'assumptions' column.
    """
    
    # Handle None/NaN values in year column before converting to int
    df = df.copy()  # Don't modify original dataframe
    
    # Replace None/NaN with a default value or drop rows
    df['year'] = pd.to_numeric(df['year'], errors='coerce')  # Convert to NaN if can't convert
    
    # Option 1: Drop rows with invalid years
    df = df.dropna(subset=['year'])
    
    # Option 2: Or fill with a default year (uncomment if you prefer this)
    # df['year'] = df['year'].fillna(2023)  # Replace with appropriate default
    
    df['year'] = df['year'].astype(int)

    # Rest of your function remains the same...
    df_year = df[df['year'] == year]

    df_values = df_year.groupby(['country', 'metric'], as_index=False)['value'].mean()
    pivot_df = df_values.pivot(index='country', columns='metric', values='value')

    sources_per_country = (
        df_year.groupby('country')['source']
        .apply(lambda x: ', '.join(sorted(set(x.dropna().astype(str)))) if not x.dropna().empty else 'No source')
    )
    
    assumptions_per_country = (
        df_year.groupby('country')['assumption']
        .apply(lambda x: ', '.join(sorted(set(x.dropna().astype(str)))) if not x.dropna().empty else 'No assumption')
    )

    pivot_df['source'] = sources_per_country
    pivot_df['assumption'] = assumptions_per_country

    return pivot_df

def sparsity_ratio_column(df, col, sparse_value=None):
    """
    Calculate sparsity ratio of a column
    
    Parameters:
    df: DataFrame
    col: Column name
    sparse_value: Value to consider as sparse (None for NaN, 0 for zero, etc.)
    
    Returns:
    float: Sparsity ratio (0-1, where 1 means completely sparse)
    """
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found in DataFrame")
    
    total_count = len(df)
    
    if total_count == 0:
        return 0.0
    
    if sparse_value is None:
        # Count NaN/null values
        sparse_count = df[col].isnull().sum()
    else:
        # Count specific sparse value (including NaN)
        sparse_count = df[col].isnull().sum() + (df[col] == sparse_value).sum()
    
    sparsity_ratio = sparse_count / total_count
    return sparsity_ratio

def sparsity_ratio_row(df, row_index, sparse_value=None):
    """
    Calculate sparsity ratio of a row
    
    Parameters:
    df: DataFrame
    row_index: Row index
    sparse_value: Value to consider as sparse (None for NaN, 0 for zero, etc.)
    
    Returns:
    float: Sparsity ratio (0-1, where 1 means completely sparse)
    """
    if row_index not in df.index:
        raise ValueError(f"Row index '{row_index}' not found in DataFrame")
    
    row_data = df.loc[row_index]
    total_count = len(row_data)
    
    if total_count == 0:
        return 0.0
    
    if sparse_value is None:
        # Count NaN/null values
        sparse_count = row_data.isnull().sum()
    else:
        # Count specific sparse value (including NaN)
        sparse_count = row_data.isnull().sum() + (row_data == sparse_value).sum()
    
    sparsity_ratio = sparse_count / total_count
    return sparsity_ratio

def drop_sparse_columns(df, threshold=0.5, sparse_value=None):
    """
    Drop columns with insufficient data (high sparsity)
    
    Parameters:
    df: DataFrame
    threshold: Sparsity threshold (0-1, columns above this will be dropped)
    sparse_value: Value to consider as sparse (None for NaN, 0 for zero, etc.)
    
    Returns:
    DataFrame: DataFrame with sparse columns removed
    """
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1")
    
    df_copy = df.copy()
    columns_to_drop = []
    
    for col in df_copy.columns:
        sparsity = sparsity_ratio_column(df_copy, col, sparse_value)
        if sparsity > threshold:
            columns_to_drop.append(col)
    
    df_result = df_copy.drop(columns=columns_to_drop)
    
    return df_result

def drop_sparse_rows(df, threshold=0.5, sparse_value=None):
    """
    Drop rows with insufficient data (high sparsity)
    
    Parameters:
    df: DataFrame
    threshold: Sparsity threshold (0-1, rows above this will be dropped)
    sparse_value: Value to consider as sparse (None for NaN, 0 for zero, etc.)
    
    Returns:
    DataFrame: DataFrame with sparse rows removed
    """
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1")
    
    df_copy = df.copy()
    rows_to_drop = []
    
    for idx in df_copy.index:
        sparsity = sparsity_ratio_row(df_copy, idx, sparse_value)
        if sparsity > threshold:
            rows_to_drop.append(idx)
    
    df_result = df_copy.drop(index=rows_to_drop)
    
    return df_result

# Convenience functions for comprehensive sparsity analysis

def get_column_sparsity_summary(df, sparse_value=None):
    """
    Get sparsity summary for all columns
    
    Returns:
    DataFrame: Summary with columns, sparsity ratios, and recommendations
    """
    summary_data = []
    
    for col in df.columns:
        sparsity = sparsity_ratio_column(df, col, sparse_value)
        total_values = len(df)
        sparse_count = int(sparsity * total_values)
        non_sparse_count = total_values - sparse_count
        
        # Recommendation based on sparsity
        if sparsity < 0.1:
            recommendation = "Excellent - Keep column"
        elif sparsity < 0.3:
            recommendation = "Good - Keep column"
        elif sparsity < 0.5:
            recommendation = "Fair - Consider imputation"
        elif sparsity < 0.7:
            recommendation = "Poor - Consider dropping"
        else:
            recommendation = "Very Poor - Drop column"
        
        summary_data.append({
            'column': col,
            'sparsity_ratio': sparsity,
            'sparse_count': sparse_count,
            'non_sparse_count': non_sparse_count,
            'total_count': total_values,
            'recommendation': recommendation
        })
    
    summary_df = pd.DataFrame(summary_data)
    return summary_df.sort_values('sparsity_ratio', ascending=False)

def get_row_sparsity_summary(df, sparse_value=None, top_n=10):
    """
    Get sparsity summary for rows
    
    Returns:
    DataFrame: Summary with row indices, sparsity ratios, and counts
    """
    summary_data = []
    
    for idx in df.index:
        sparsity = sparsity_ratio_row(df, idx, sparse_value)
        total_values = len(df.columns)
        sparse_count = int(sparsity * total_values)
        non_sparse_count = total_values - sparse_count
        
        if sparsity < 0.1:
            recommendation = "Excellent - Keep column"
        elif sparsity < 0.3:
            recommendation = "Good - Keep column"
        elif sparsity < 0.5:
            recommendation = "Fair - Consider imputation"
        elif sparsity < 0.7:
            recommendation = "Poor - Consider dropping"
        else:
            recommendation = "Very Poor - Drop column"

        summary_data.append({
            'row_index': idx,
            'sparsity_ratio': sparsity,
            'sparse_count': sparse_count,
            'non_sparse_count': non_sparse_count,
            'total_count': total_values,
            'recommendation': recommendation
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('sparsity_ratio', ascending=False)
    
    if top_n:
        return summary_df.head(top_n)
    
    return summary_df

def analyze_sparsity_patterns(df, sparse_value=None):
    """
    Comprehensive sparsity analysis
    
    Returns:
    dict: Comprehensive sparsity analysis results
    """
    total_elements = df.shape[0] * df.shape[1]
    
    if sparse_value is None:
        total_sparse = df.isnull().sum().sum()
    else:
        total_sparse = df.isnull().sum().sum() + (df == sparse_value).sum().sum()
    
    overall_sparsity = total_sparse / total_elements if total_elements > 0 else 0
    
    # Column analysis
    col_sparsity = [sparsity_ratio_column(df, col, sparse_value) for col in df.columns]
    
    # Row analysis
    row_sparsity = [sparsity_ratio_row(df, idx, sparse_value) for idx in df.index]
    
    results = {
        'overall_sparsity': overall_sparsity,
        'total_elements': total_elements,
        'total_sparse': total_sparse,
        'column_stats': {
            'mean_sparsity': np.mean(col_sparsity),
            'median_sparsity': np.median(col_sparsity),
            'min_sparsity': np.min(col_sparsity),
            'max_sparsity': np.max(col_sparsity),
            'std_sparsity': np.std(col_sparsity)
        },
        'row_stats': {
            'mean_sparsity': np.mean(row_sparsity),
            'median_sparsity': np.median(row_sparsity),
            'min_sparsity': np.min(row_sparsity),
            'max_sparsity': np.max(row_sparsity),
            'std_sparsity': np.std(row_sparsity)
        },
        'recommendations': {
            'columns_to_drop_50pct': [col for col in df.columns if sparsity_ratio_column(df, col, sparse_value) > 0.5],
            'columns_to_drop_70pct': [col for col in df.columns if sparsity_ratio_column(df, col, sparse_value) > 0.7],
            'rows_to_drop_50pct': len([idx for idx in df.index if sparsity_ratio_row(df, idx, sparse_value) > 0.5]),
            'rows_to_drop_70pct': len([idx for idx in df.index if sparsity_ratio_row(df, idx, sparse_value) > 0.7])
        }
    }
    
    return results

def optimize_dataframe_sparsity(df, column_threshold=0.5, row_threshold=0.5, sparse_value=None):
    """
    Optimize dataframe by removing sparse columns and rows
    
    Returns:
    dict: Optimized dataframe and optimization report
    """
    original_shape = df.shape
    
    # Step 1: Remove sparse columns
    df_step1 = drop_sparse_columns(df, column_threshold, sparse_value)
    
    # Step 2: Remove sparse rows
    df_optimized = drop_sparse_rows(df_step1, row_threshold, sparse_value)
    
    final_shape = df_optimized.shape
    
    report = {
        'original_shape': original_shape,
        'final_shape': final_shape,
        'columns_removed': original_shape[1] - final_shape[1],
        'rows_removed': original_shape[0] - final_shape[0],
        'data_retention': (final_shape[0] * final_shape[1]) / (original_shape[0] * original_shape[1]) if original_shape[0] * original_shape[1] > 0 else 0,
        'column_threshold': column_threshold,
        'row_threshold': row_threshold,
        'sparse_value': sparse_value
    }
    
    return {
        'optimized_df': df_optimized,
        'report': report
    }

def compare_sparsity_thresholds(df, thresholds=[0.3, 0.5, 0.7, 0.9], sparse_value=None):
    """
    Compare different sparsity thresholds and their impact
    
    Returns:
    DataFrame: Comparison results for different thresholds
    """
    comparison_data = []
    original_shape = df.shape
    
    for threshold in thresholds:
        # Test column dropping
        df_col_dropped = drop_sparse_columns(df, threshold, sparse_value)
        
        # Test row dropping
        df_row_dropped = drop_sparse_rows(df, threshold, sparse_value)
        
        # Test both
        df_both = drop_sparse_rows(
            drop_sparse_columns(df, threshold, sparse_value),
            threshold, sparse_value
        )
        
        comparison_data.append({
            'threshold': threshold,
            'columns_remaining': df_col_dropped.shape[1],
            'rows_remaining_col_drop': df_col_dropped.shape[0],
            'rows_remaining_row_drop': df_row_dropped.shape[0],
            'columns_remaining_row_drop': df_row_dropped.shape[1],
            'final_shape_both': df_both.shape,
            'data_retention_both': (df_both.shape[0] * df_both.shape[1]) / (original_shape[0] * original_shape[1]) if original_shape[0] * original_shape[1] > 0 else 0
        })
    
    return pd.DataFrame(comparison_data)

def identify_sparse_value_candidates(df, sample_size=1000):
    """
    Identify potential sparse values in the dataset
    
    Returns:
    dict: Potential sparse values and their frequencies
    """
    candidates = {}
    
    # Sample the dataframe if it's large
    if len(df) > sample_size:
        sampled_df = df.sample(n=sample_size, random_state=42)
    else:
        sampled_df = df
    
    for col in sampled_df.select_dtypes(include=[np.number]).columns:
        value_counts = sampled_df[col].value_counts()
        total_non_null = sampled_df[col].count()
        
        if total_non_null > 0:
            # Look for values that appear frequently and might be sparse indicators
            for value, count in value_counts.head(5).items():
                frequency = count / total_non_null
                if frequency > 0.1:  # If value appears in more than 10% of non-null values
                    if value not in candidates:
                        candidates[value] = []
                    candidates[value].append({
                        'column': col,
                        'frequency': frequency,
                        'count': count
                    })
    
    return candidates
