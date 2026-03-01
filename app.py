

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
