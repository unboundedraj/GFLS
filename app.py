

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
