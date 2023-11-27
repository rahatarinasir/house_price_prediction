# -*- coding: utf-8 -*-
"""House Prices - Advanced Regression Techniques.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12hwan5o_IvQEgijdx1wvwbDCeiZDxEq8

## **import libraries**
"""

import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

!wget https://raw.githubusercontent.com/h4pZ/rose-pine-matplotlib/main/themes/rose-pine-dawn.mplstyle -P /tmp
plt.style.use("/tmp/rose-pine-dawn.mplstyle")

pd.options.display.max_columns=100
pd.options.display.max_rows=100

"""## **connect to kaggle**"""

!pip install kaggle

from google.colab import files

# Choose the JSON file you downloaded from Kaggle here
files.upload()


#This code will prompt you to select the JSON file from your local machine and upload it to Colab.

!mkdir -p ~/.kaggle
!mv kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

!kaggle competitions download -c house-prices-advanced-regression-techniques

"""## **read zip data**"""

import zipfile
import pandas as pd

# Specify the path and filename of the downloaded zip file
zip_filepath = "/content/house-prices-advanced-regression-techniques.zip"

# Extract the contents of the zip file
with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
    zip_ref.extractall("/content/")

# Read the train.csv file
train_filepath = "/content/train.csv"
train = pd.read_csv(train_filepath).drop("Id", axis=1)

# Read the test.csv file
test_filepath = "/content/test.csv"
test = pd.read_csv(test_filepath).drop("Id", axis=1)

# Read the sample_submission.csv file
submission_filepath = "/content/sample_submission.csv"
sub = pd.read_csv(submission_filepath)

"""## **concat test and train**"""

def con_cat(train, test):
    df1, df2 = train.copy(), test.copy()
    df1["group"] = "train"
    df2["group"] = "test"

    return pd.concat([df1, df2], axis=0, ignore_index=True)

df = con_cat(train, test)
df.head()

"""👀 Features:

**SalePrice**: This is the target variable, and it represents the sale price of the property in dollars. In the context of the competition, your objective is to predict this variable.

**MSSubClass**: This field represents the building class of the property. It provides information about the type of dwelling involved.

**MSZoning** : This field indicates the general zoning classification of the property, which is a way to categorize and regulate land use.

**LotFrontage and LotArea**: These fields provide information about the size of the property. LotFrontage is the linear feet of street connected to the property, and LotArea is the size of the lot in square feet.

**Street and Alley**: These fields describe the type of road access (Street) and the type of alley access to the property.

LotShape: This field defines the general shape of the property.

LandContour: It describes the flatness of the property.

Utilities: This field indicates the type of utilities available in the property.

Neighborhood: This represents the physical locations within the Ames city limits.

OverallQual and OverallCond: These fields provide information about the overall material and finish quality, as well as the overall condition rating of the property.

YearBuilt and YearRemodAdd: They represent the original construction date and the remodel date of the property, respectively.

RoofStyle and RoofMatl: These fields describe the type of roof and the roofing material.

Exterior1st and Exterior2nd: They indicate the exterior covering on the house, with Exterior2nd being applicable if there is more than one material.

BsmtQual, BsmtCond, BsmtExposure, BsmtFinType1, BsmtFinSF1, BsmtFinType2, BsmtFinSF2, BsmtUnfSF, TotalBsmtSF: These fields provide information about the basement, including its quality, condition, exposure, finished area, and unfinished area.

Heating and HeatingQC: These fields describe the type of heating and the heating quality and condition.

CentralAir: Indicates whether the property has central air conditioning.

Electrical: Describes the electrical system in the house.

1stFlrSF, 2ndFlrSF, LowQualFinSF, GrLivArea: These fields represent the square footage of different floors and the above-grade (ground) living area square footage.

BsmtFullBath, BsmtHalfBath, FullBath, HalfBath: Provide information about the number of bathrooms on different levels.

Bedroom, Kitchen, KitchenQual, TotRmsAbvGrd: These fields provide information about the number of bedrooms, kitchens, and the quality of the kitchen.

Functional: Describes the home's functionality rating.

Fireplaces and FireplaceQu: Indicate the number of fireplaces and the quality of the fireplace.

GarageType, GarageYrBlt, GarageFinish, GarageCars, GarageArea, GarageQual, GarageCond: Provide information about the garage, including its type, year built, finish, size, and quality.

PavedDrive: Indicates whether the property has a paved driveway.

WoodDeckSF, OpenPorchSF, EnclosedPorch, 3SsnPorch, ScreenPorch: These fields represent the square footage of different types of porches.

PoolArea and PoolQC: Provide information about the pool area and its quality.

Fence: Describes the quality of the fence.

MiscFeature and MiscVal: Miscellaneous features not covered in other categories and their corresponding values.

MoSold and YrSold: Represent the month and year the property was sold.

SaleType and SaleCondition: Provide information about the type of sale and the condition of the sale.

## cleaning data
 FIND TYPE OF DATA COLUMNS WITH FUNCTION.
**num_cols**, **ordinals**, **cat_cols**
"""

def find_col_dtypes(data, ord_th):
    num_cols = data.select_dtypes("number").columns.to_list()
    cat_cols = data.select_dtypes("object").columns.to_list()

    ordinals = [col for col in num_cols if data[col].nunique() < ord_th]

    num_cols = [col for col in num_cols if col not in ordinals]

    return num_cols, ordinals, cat_cols

num_cols, ordinals, cat_cols = find_col_dtypes(test, 20)

print(f"Num Cols: {num_cols}", end="\n\n")
print(f"Cat Cols: {cat_cols}", end="\n\n")
print(f"Ordinal Cols: {ordinals}")

train.duplicated().sum()

"""## EDA"""

train["SalePrice"].quantile([0,0.25,0.50,0.75,0.99])

"""This output tells us the values at different quantiles of the "SalePrice" column. For instance, we can interpret that:


*   The **minimum **value (**0th percentile**) of the "SalePrice" column is $34,900.

*   **25% of the houses** have a sale price below or equal to $129,975

*   **The median (50th percentile**) sale price is $163,000.

*   **75% of the houses** have a sale price below or equal to $214,000.

*   **Only the top 1% **of houses have a sale price above $442,567.01.
















"""

train["SalePrice_Range"] = pd.cut(train["SalePrice"],
                                 bins=np.array([-np.inf, 100, 150, 200, np.inf])*1000,
                                 labels=["0-100k","100k-150k","150k-200k","200k+"])

import matplotlib.pyplot as plt

# Example: MSSubClass - Building class of the property
building_class_counts = train['MSSubClass'].value_counts()

plt.bar(building_class_counts.index, building_class_counts.values)
plt.xlabel('Building Class')
plt.ylabel('Count')
plt.title('Distribution of Building Classes')
plt.xticks(rotation=90)  # Rotate x-axis labels if needed
plt.show()

# Example: LotArea - Size of the lot in square feet
plt.hist(train['LotArea'], bins=20)
plt.xlabel('Lot Area')
plt.ylabel('Count')
plt.title('Distribution of Lot Area')
plt.show()

# Example: MSZoning - General zoning classification of the property
zone_counts = train['MSZoning'].value_counts()

plt.pie(zone_counts, labels=zone_counts.index, autopct='%1.1f%%')
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
plt.title('Zoning Classification')
plt.show()

# Example: OverallQual - Overall material and finish quality
plt.boxplot(train['OverallQual'])
plt.xlabel('Overall Quality')
plt.ylabel('Quality Rating')
plt.title('Distribution of Overall Quality')
plt.show()

# Calculate the count of properties in each sale price range
sale_price_counts = train['SalePrice_Range'].value_counts()

# Custom colors for bar chart
colors = ['#5E81AC', '#88C0D0', '#B48EAD', '#A3BE8C' ,'#EBCB8B']

# Bar chart - Sales price distribution
plt.bar(sale_price_counts.index, sale_price_counts.values, color=colors)
plt.xlabel('Sale Price Range')
plt.ylabel('Count')
plt.title('Sales Price Distribution')

# Add count values as text annotations above each bar
for i, count in enumerate(sale_price_counts.values):
    plt.text(i, count + 10, str(count), ha='center', fontsize=10)

plt.show()



# Pie chart - Sales price distribution
plt.pie(sale_price_counts, labels=sale_price_counts.index, autopct='%1.1f%%', colors=colors)
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
plt.title('Sales Price Distribution')
plt.show()

target = "SalePrice"
plt.figure(figsize=(14,len(cat_cols)*3))
for idx,column in enumerate(cat_cols ):
    data = df[df["group"] == "train"].groupby(column)[target].mean().reset_index().sort_values(by=target)
    plt.subplot(len(cat_cols)//2+1,2,idx+1)
    sns.barplot(y=column, x=target, data=data, palette="pastel")
    for p, count in enumerate(data[target].values,0):
        plt.text(count + 10, p+0.05/len(data), f"{int(count//1000)}k", color='black', fontsize=11)
    plt.title(f"{column} and {target}")
    plt.xticks(fontweight='bold')
    plt.box(False)
    plt.tight_layout()

plt.figure(figsize=(14,len(num_cols)*3))
for idx,column in enumerate(num_cols):
    plt.subplot(len(num_cols)//2+1,2,idx+1)
    sns.boxplot(x="SalePrice_Range", y=column, data=train,palette="pastel")
    plt.title(f"{column} Distribution")
    plt.tight_layout()

plt.figure(figsize=(12,10))
corr=df[num_cols].corr(numeric_only=True)
mask= np.triu(np.ones_like(corr))
sns.heatmap(corr, annot=True, fmt=".1f", linewidths=1, mask=mask, cmap=sns.color_palette("vlag"));

"""## **outliner_detector**"""

def outliner_detector(df, cols, take_care_outliners=False, print_outliners=False, q_1=0.25, q_3=0.75):
    temp = pd.DataFrame()
    data = df.copy()
    for col in cols:
        q1 = data[col].quantile(q_1)
        q3 = data[col].quantile(q_3)
        IQR = q3 - q1
        up = q3 + 1.5 * IQR
        low = q1 - 1.5 * IQR
        temp.loc[col, "Min"] = round(data[col].min())
        temp.loc[col, "Low_Limit"] = round(low)
        temp.loc[col, "Mean"] = round(data[col].mean())
        temp.loc[col, "Median"] = round(data[col].median())
        temp.loc[col,"Up_Limit"] = up
        temp.loc[col, "Max"] = data[col].max()
        temp.loc[col, "Outliner"] = "Min-Max-Outliner" if (data[col].max() > up) & (low > data[col].min())\
                                    else ("Max-Outliner" if data[col].max() > up \
                                    else ("Min-Outliner" if low > data[col].min() \
                                    else "No"))
        if take_care_outliners:
            data.loc[data[col] > up,col] = round(up-1)
            data.loc[data[col] < low,col] = round(low-1)
    if take_care_outliners:
        if print_outliners: return temp
        return data
    if print_outliners: return temp

outliner_detector(df, num_cols, print_outliners=True, q_1=0.01, q_3=0.99)

def mice_imput(df:pd.DataFrame, fill:str, based:list) -> pd.Series :
    """
    Impute missing values in a specified column of a DataFrame using the
    MICE (Multiple Imputation by Chained Equations) algorithm.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing the data.
    - fill (str): The column name with missing values to be imputed.
    - based (list): A list of column names considered as features for imputation.

    Returns:
    - pd.Series: A Series containing the imputed values for the specified column.

    MICE (Multiple Imputation by Chained Equations) is a statistical method used for imputing
    missing data in a dataset.
    It is an iterative algorithm that imputes missing values one variable at a time,
    considering the relationships between variables. In this implementation:

    1. Categorical columns are identified in the 'based' list.
    2. A temporary DataFrame is created by one-hot encoding categorical columns and
        selecting the target column ('fill').
    3. A missing value mask is generated for the temporary DataFrame.
    4. The IterativeImputer from scikit-learn is used to impute missing values iteratively.
    5. The imputed values are assigned to the original DataFrame in the specified column.
    """

    from sklearn.experimental import enable_iterative_imputer
    from sklearn.impute import IterativeImputer

    categoric_cols = [col for col in based if df[col].dtype == "O"]

    temp_df = pd.get_dummies(df[[fill] + based].copy(), columns=categoric_cols)

    missing_mask = temp_df.isna()

    imputer = IterativeImputer(max_iter=10, random_state=42)

    imputed_values = imputer.fit_transform(temp_df)

    temp_df[fill][temp_df[fill].isnull()] = imputed_values[missing_mask]

    return temp_df[fill]
df["LotFrontage"] = mice_imput(df, fill="LotFrontage", based=["LotArea","LotShape","LotConfig"])
df.loc[df["MasVnrArea"].isnull(),["MasVnrArea"]] = 0
df.loc[df["BsmtFinSF1"].isnull(),["BsmtFinSF1","BsmtFinSF2","BsmtUnfSF","TotalBsmtSF"]] = 0
df.loc[df["GarageYrBlt"].isnull(),"GarageYrBlt"] = 0
df.loc[df["GarageArea"].isnull(),"GarageArea"] = 0
df[cat_cols] = df[cat_cols].fillna("None")
df[ordinals] = df[ordinals].fillna(0)

df = outliner_detector(df, num_cols, take_care_outliners= True, print_outliners=False, q_1=0.01, q_3=0.99)
outliner_detector(df, num_cols, print_outliners=True, q_1=0.01, q_3=0.99)

df["Street"].value_counts() / len(df) * 100

def drop_feature(data,columns, percentage):
    data = data.copy()
    new_cat_cols=[]
    for col in columns:
        rank_1 = (data[col].value_counts().sort_values(ascending=False) / len(data)*100).iloc[0]
        if rank_1 > percentage:
            print(f"Feature {col} is Nonsense, Dropped")
            data.drop(col, axis=1, inplace=True)
        else:
            new_cat_cols.append(col)
    return data, new_cat_cols

df, new_cat_cols = drop_feature(df,cat_cols,percentage = 95)

df["HeatingQC"].value_counts() / len(df) * 100

def bag_rares(data, columns, percentage):
    data = data.copy()
    for col in columns:
        rares = data[col].value_counts().sort_values(ascending=False) / len(df) < percentage/100
        rare_names = rares[rares].index.to_list()
        data[col][data[col].isin(rare_names)] = "Rare"
    return data

df = bag_rares(df,new_cat_cols,percentage = 5)

df["HeatingQC"].value_counts() / len(df) * 100

def new_features(df):
    # Calculate the total area
    df['TotalArea'] = df['TotalBsmtSF'] + df['GrLivArea']

    # Calculate the number of new or renovated bathrooms
    df['TotalBathrooms'] = df['FullBath'] + df['HalfBath']*0.5 + df["BsmtHalfBath"]*0.5 + df["BsmtFullBath"]

    # Calculate the total room count
    df['TotalRooms'] = df['BedroomAbvGr'] + df['TotRmsAbvGrd']

    # Has pool?
    df['HasPool'] = [1 if pool > 0 else 0 for pool in df["PoolArea"]]

    # Calculate the total porch area
    df['TotalPorchArea'] = df['OpenPorchSF'] + df['EnclosedPorch'] + \
                            df["3SsnPorch"] + df["ScreenPorch"] + df["WoodDeckSF"]

    # Has Garage?
    df['HasGarage'] = [1 if gar > 0 else 0 for gar in df["GarageYrBlt"]]

    # House Overall
    df['Overal'] = df['OverallQual'] + df['OverallCond']

new_features(df)

df[["TotalArea","TotalBathrooms","TotalRooms","HasPool","TotalPorchArea","HasGarage","Overal"]].head()

df = pd.get_dummies(df, columns=new_cat_cols, dtype=int)

train = df[df["group"] == "train"].drop("group", axis = 1)
test = df[df["group"] == "test"].drop(["group","SalePrice"], axis = 1)

train.columns = [col.replace(" ", "_") for col in train.columns]
test.columns = [col.replace(" ", "_") for col in test.columns]

"""## **modeling**

**split**
"""

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

X = train.drop(["SalePrice"], axis=1)
y = np.log(train["SalePrice"])


X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.2, random_state = 1128)

"""**important feature**

## **linear regression**
"""

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score, mean_absolute_error
# Create a linear regression model
linear = LinearRegression()

# Fit the model to the training data
linear.fit(X_train, y_train)

# Make predictions on the test data
linear_pred = linear.predict(X_test)

# Calculate R-squared
r_squared = r2_score(y_test, y_pred)
print(f"R-squared: {r_squared}")

# Calculate Adjusted R-squared
n = X_test.shape[0]  # Number of samples in the test set
p = X_test.shape[1]  # Number of predictors
adj_r_squared = 1 - ((1 - r_squared) * (n - 1)) / (n - p - 1)
print(f"Adjusted R-squared: {adj_r_squared}")

# Calculate Mean Absolute Error (MAE)
mae = mean_absolute_error(y_test, y_pred)
print(f"Mean Absolute Error: {mae}")

mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

"""## lasso(l1 regresssion)"""

from sklearn.linear_model import Lasso
# Create a Lasso regression model
lasso = Lasso(alpha=0.4)  # Adjust the alpha parameter as desired

# Fit the model to the training data
lasso.fit(X_train, y_train)

# Make predictions on the test data
lasso_pred = lasso.predict(X_test)

# Calculate R-squared
r_squared = r2_score(y_test, y_pred)
print(f"R-squared: {r_squared}")

# Calculate Adjusted R-squared
n = X_test.shape[0]  # Number of samples in the test set
p = X_test.shape[1]  # Number of predictors
adj_r_squared = 1 - ((1 - r_squared) * (n - 1)) / (n - p - 1)
print(f"Adjusted R-squared: {adj_r_squared}")

# Calculate Mean Absolute Error (MAE)
mae = mean_absolute_error(y_test, y_pred)
print(f"Mean Absolute Error: {mae}")

mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

"""## Ridge regression (l2 regression)"""

from sklearn.linear_model import Ridge
# Create a Ridge regression model
ridge = Ridge(alpha=1.0)  # Adjust the alpha parameter as desired

# Fit the model to the training data
ridge.fit(X_train, y_train)

# Make predictions on the test data
ridge_pred = ridge.predict(X_test)

# Calculate R-squared
r_squared = r2_score(y_test, y_pred)
print(f"R-squared: {r_squared}")

# Calculate Adjusted R-squared
n = X_test.shape[0]  # Number of samples in the test set
p = X_test.shape[1]  # Number of predictors
adj_r_squared = 1 - ((1 - r_squared) * (n - 1)) / (n - p - 1)
print(f"Adjusted R-squared: {adj_r_squared}")

# Calculate Mean Absolute Error (MAE)
mae = mean_absolute_error(y_test, y_pred)
print(f"Mean Absolute Error: {mae}")

mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

"""**lightgbm**"""

import lightgbm
lgb = lightgbm.LGBMRegressor(objective = 'root_mean_squared_error')
lgb.fit(X_train, y_train)
lightgbm.plot_importance(lgb, max_num_features = 15);
y_pred = lgb.predict(X_test)
mean_squared_error(y_test,y_pred, squared=False)

"""**xgboost**"""

import xgboost
xgb = xgboost.XGBRegressor(objective = 'reg:squarederror')
xgb.fit(X_train, y_train)
xgboost.plot_importance(xgb, max_num_features = 15);
y_pred = xgb.predict(X_test)
mean_squared_error(y_test,y_pred, squared=False)

from sklearn.preprocessing import MinMaxScaler
lgb_importances = pd.DataFrame(dict(lgbm = lgb.feature_importances_), index=lgb.feature_name_)
xgb_importances = pd.DataFrame(dict(xgb = xgb.feature_importances_), index=xgb.feature_names_in_)
importances = pd.concat([lgb_importances,xgb_importances],axis=1)
min_max = MinMaxScaler((0.1,1))
importances["cross"] = min_max.fit_transform(importances[["lgbm"]]) * min_max.fit_transform(importances[["xgb"]])
sorted = importances.sort_values(by="cross", ascending=False).reset_index()
sorted

X_train.drop(sorted.tail(45)["index"],axis=1, inplace=True)
X_test.drop(sorted.tail(45)["index"],axis=1, inplace=True)
test.drop(sorted.tail(45)["index"],axis=1, inplace=True)

"""**cat boost regressor**"""

!pip install catboost

!pip install optuna

from catboost import CatBoostRegressor
import optuna

def objective_cat(trial):
    """Define the objective function"""

    params = {
        'objective': trial.suggest_categorical('objective', ['RMSE']),
        'logging_level': trial.suggest_categorical('logging_level', ['Silent']),
        "random_seed" : trial.suggest_categorical('random_seed', [42]),
        "iterations" : trial.suggest_int("iterations", 500, 1500),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.15),
        "depth" : trial.suggest_int("depth", 5, 8),
        'subsample': trial.suggest_float('subsample', 0.6, 0.9),
        "colsample_bylevel": trial.suggest_float("colsample_bylevel", 0.1, 0.5),
        'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 5, 20),
        'bagging_temperature' :trial.suggest_loguniform('bagging_temperature', 0.01, 1),
        'leaf_estimation_iterations': trial.suggest_int('leaf_estimation_iterations',10,30),
        'reg_lambda': trial.suggest_uniform('reg_lambda',50,100),

    }



    model_cat = CatBoostRegressor(**params)
    model_cat.fit(X_train, y_train)
    y_pred = model_cat.predict(X_test)
    return mean_squared_error(y_test,y_pred, squared=False)

study_cat = optuna.create_study(direction='minimize')
optuna.logging.set_verbosity(optuna.logging.WARNING)
study_cat.optimize(objective_cat, n_trials=50,show_progress_bar=True)

print('Best parameters', study_cat.best_params)

cat = CatBoostRegressor(**study_cat.best_params)
cat.fit(X_train, y_train)
cat_pred = cat.predict(X_test)

print('Error: ', mean_squared_error(y_test,y_pred, squared=False))

"""**LightGBM Regressor**




"""

from lightgbm import LGBMRegressor
import optuna

def objective_lgb(trial):
    """Define the objective function"""

    params = {
        'objective': trial.suggest_categorical('objective', ['root_mean_squared_error']),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'num_leaves': trial.suggest_int('num_leaves', 8, 1024),
        'min_child_samples': trial.suggest_int('min_child_samples', 5, 30),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.05, log=True),
        'n_estimators': trial.suggest_int('n_estimators', 700, 1600),
        'min_child_weight': trial.suggest_int('min_child_weight', 10, 25),
        'subsample': trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.01, 0.5),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.01, 0.5),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.5, 1.0),
        "random_state" : trial.suggest_categorical('random_state', [42]),
        "extra_trees" : trial.suggest_categorical('extra_trees', [True]),

    }


    model_lgb = LGBMRegressor(**params)
    model_lgb.fit(X_train, y_train)
    y_pred = model_lgb.predict(X_test)
    return mean_squared_error(y_test,y_pred, squared=False)

study_lgb = optuna.create_study(direction='minimize')
optuna.logging.set_verbosity(optuna.logging.WARNING)
study_lgb.optimize(objective_lgb, n_trials=30,show_progress_bar=True)

# Print the best parameters
print('Best parameters', study_lgb.best_params)

lgb = LGBMRegressor(**study_lgb.best_params)
lgb.fit(X_train, y_train)
lgb_pred = lgb.predict(X_test)

print('Error: ', mean_squared_error(y_test,y_pred, squared=False))

"""**XGBoost Regressor**"""

from xgboost import XGBRegressor
import optuna
def objective_xg(trial):
    """Define the objective function"""

    params = {
        'booster': trial.suggest_categorical('booster', ['gbtree']),
        'max_depth': trial.suggest_int('max_depth', 3, 12),
        'max_leaves': trial.suggest_int('max_leaves', 8, 1024),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
        'n_estimators': trial.suggest_int('n_estimators', 400, 1500),
        'min_child_weight': trial.suggest_int('min_child_weight', 10, 20),
        'subsample': trial.suggest_float('subsample', 0.3, 0.9),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.01, 0.5),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.5, 1.0),
        'colsample_bylevel': trial.suggest_float('colsample_bylevel', 0.3, 0.8),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1),
        'colsample_bynode': trial.suggest_float('colsample_bynode', 0.01, 0.5),
        "random_state" : trial.suggest_categorical('random_state', [42]),
        'objective': trial.suggest_categorical('objective', ['reg:squarederror']),
        "n_jobs" : trial.suggest_categorical('n_jobs', [-1]),
    }

    model_xgb = XGBRegressor(**params)
    model_xgb.fit(X_train, y_train)
    y_pred = model_xgb.predict(X_test)
    return mean_squared_error(y_test,y_pred, squared=False)

study_xgb = optuna.create_study(direction='minimize')
optuna.logging.set_verbosity(optuna.logging.WARNING)
study_xgb.optimize(objective_xg, n_trials=50,show_progress_bar=True)

# Print the best parameters
print('Best parameters', study_xgb.best_params)

xgb = XGBRegressor(**study_xgb.best_params)
xgb.fit(X_train, y_train)
xgb_pred = xgb.predict(X_test)

print('Error: ', mean_squared_error(y_test,y_pred, squared=False))

"""**Voting Regressor**"""

!pip install sklego

from sklego.linear_model import LADRegression
models = pd.DataFrame()
models["cat"] = cat.predict(X_test)
models["lgbm"] = lgb.predict(X_test)
models["xgb"] = xgb.predict(X_test)

weights = LADRegression().fit(models, y_test).coef_
pd.DataFrame(weights, index = models.columns, columns = ["weights"])

"""Based on the given weights, the best entry would be "xgb" with a weight of 0.7005926368790446."""

from sklearn.ensemble import VotingRegressor
voting = VotingRegressor(estimators=[ ('cat', cat),
                                      ('lgbm', lgb),
                                      ('xgb', xgb)],weights=weights)
voting.fit(X_train,y_train)
voting_pred = voting.predict(X_test)

print('Error: ', mean_squared_error(y_test,y_pred, squared=False))

import matplotlib.pyplot as plt

# Assuming you have the predictions of the VotingRegressor model stored in voting_pred

# Create a scatter plot to compare the predictions
plt.figure(figsize=(8, 6))
plt.scatter(y_test, voting_pred, color='purple', label='VotingRegressor')

# Add labels and title
plt.xlabel('True Values')
plt.ylabel('Predicted Values')
plt.title('Comparison of Model Predictions')

# Add a diagonal line for reference
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='black', linestyle='--')

# Add legend
plt.legend()

# Show the plot
plt.show()

import matplotlib.pyplot as plt

# Assuming you have the predictions of 'cat', 'lgbm', and 'xgb' models stored in separate variables
# For example, cat_pred, lgbm_pred, xgb_pred

# Create a scatter plot to compare the predictions
plt.figure(figsize=(8, 6))
plt.scatter(y_test, cat_pred, color='blue', label='CatBoost')
plt.scatter(y_test, lgb_pred, color='red', label='LGBM')
plt.scatter(y_test, xgb_pred, color='green', label='XGBoost')
plt.scatter(y_test, linear_pred, color='orange', label='linear regression')
plt.scatter(y_test, lasso_pred, color='pink', label='lasso regression')
plt.scatter(y_test, ridge_pred, color='yellow', label='ridge regression')

# Add labels and title
plt.xlabel('True Values')
plt.ylabel('Predicted Values')
plt.title('Comparison of Model Predictions')

# Add a diagonal line for reference
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='black', linestyle='--')

# Add legend
plt.legend()

# Show the plot
plt.show()

import matplotlib.pyplot as plt

# Assuming you have the predictions of 'cat', 'lgbm', and 'xgb' models stored in separate variables
# For example, cat_pred, lgb_pred, xgb_pred

# Create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

# Scatter plot 1 - Comparing CatBoost, LGBM, and XGBoost predictions
ax1.scatter(y_test, cat_pred, color='blue', label='CatBoost')
ax1.scatter(y_test, lgb_pred, color='red', label='LGBM')
ax1.scatter(y_test, xgb_pred, color='green', label='XGBoost')
ax1.scatter(y_test, linear_pred, color='orange', label='Linear Regression')
ax1.scatter(y_test, lasso_pred, color='pink', label='Lasso Regression')
ax1.scatter(y_test, ridge_pred, color='yellow', label='Ridge Regression')

# Add labels and title to subplot 1
ax1.set_xlabel('True Values')
ax1.set_ylabel('Predicted Values')
ax1.set_title('Comparison of Model Predictions')

# Add a diagonal line for reference in subplot 1
ax1.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='black', linestyle='--')

# Add legend to subplot 1
ax1.legend()

# Scatter plot 2 - Comparing CatBoost, LGBM, and XGBoost predictions (Zoomed-in view)
ax2.scatter(y_test, cat_pred, color='blue', label='CatBoost')
ax2.scatter(y_test, lgb_pred, color='red', label='LGBM')
ax2.scatter(y_test, xgb_pred, color='green', label='XGBoost')
ax2.scatter(y_test, linear_pred, color='orange', label='Linear Regression')
ax2.scatter(y_test, lasso_pred, color='pink', label='Lasso Regression')
ax2.scatter(y_test, ridge_pred, color='yellow', label='Ridge Regression')

# Add labels and title to subplot 2
ax2.set_xlabel('True Values')
ax2.set_ylabel('Predicted Values')
ax2.set_title('Comparison of Model Predictions (Zoomed-in view)')

# Set limits for the zoomed-in view in subplot 2
ax2.set_xlim([min(y_test), max(y_test)])
ax2.set_ylim([min(y_test), max(y_test)])

# Add a diagonal line for reference in subplot 2
ax2.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='black', linestyle='--')

# Add legend to subplot 2
ax2.legend()

# Adjust the spacing between the subplots
plt.tight_layout()

# Show the plot
plt.show()

import matplotlib.pyplot as plt

# Assuming you have the predictions of 'cat', 'lgbm', and 'xgb' models stored in separate variables
# For example, cat_pred, lgbm_pred, xgb_pred

# Create a scatter plot to compare the predictions
plt.figure(figsize=(8, 6))
plt.scatter(y_test, linear_pred, color='orange', label='linear regression')

plt.scatter(y_test, xgb_pred, color='green', label='XGBoost')

# Add labels and title
plt.xlabel('True Values')
plt.ylabel('Predicted Values')
plt.title('Comparison of Model Predictions')

# Add a diagonal line for reference
plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='black', linestyle='--')

# Add legend
plt.legend()

# Show the plot
plt.show()

"""## svr"""

from sklearn.svm import SVR
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error

# Train the SVM model
svm_model = SVR()
svm_model.fit(X_train, y_train)

# Make predictions using the SVM model
svm_preds = svm_model.predict(X_test)

# Calculate the mean squared error of the SVM model
svm_mse = mean_squared_error(y_test, svm_preds)
print("SVM Mean Squared Error:", svm_mse)

# Train the XGBoost model
xgb_model = XGBRegressor()
xgb_model.fit(X_train, y_train)

# Make predictions using the XGBoost model
xgb_svr_preds = xgb_model.predict(X_test)

# Calculate the mean squared error of the XGBoost model
xgb_mse = mean_squared_error(y_test, xgb_svr_preds)
print("XGBoost Mean Squared Error:", xgb_mse)

"""## svr_xgboosting"""

from sklearn.svm import SVR
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
import optuna
def objective_svr(trial):
    """Define the objective function for SVR"""

    params = {
        'kernel': trial.suggest_categorical('kernel', ['linear', 'poly', 'rbf']),
        'C': trial.suggest_loguniform('C', 0.01, 100),
        'epsilon': trial.suggest_loguniform('epsilon', 0.001, 1),
    }

    model_svr = SVR(**params)
    model_svr.fit(X_train, y_train)
    y_pred = model_svr.predict(X_test)
    return mean_squared_error(y_test, y_pred, squared=False)

def objective_xg(trial):
    """Define the objective function for XGBoost"""

    params = {
        'booster': trial.suggest_categorical('booster', ['gbtree']),
        'max_depth': trial.suggest_int('max_depth', 3, 12),
        'max_leaves': trial.suggest_int('max_leaves', 8, 1024),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
        'n_estimators': trial.suggest_int('n_estimators', 400, 1500),
        'min_child_weight': trial.suggest_int('min_child_weight', 10, 20),
        'subsample': trial.suggest_float('subsample', 0.3, 0.9),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.01, 0.5),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.5, 1.0),
        'colsample_bylevel': trial.suggest_float('colsample_bylevel', 0.3, 0.8),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1),
        'colsample_bynode': trial.suggest_float('colsample_bynode', 0.01, 0.5),
        'random_state': trial.suggest_categorical('random_state', [42]),
        'objective': trial.suggest_categorical('objective', ['reg:squarederror']),
        'n_jobs': trial.suggest_categorical('n_jobs', [-1]),
    }

    model_xgb = XGBRegressor(**params)
    model_xgb.fit(X_train, y_train)
    y_pred = model_xgb.predict(X_test)
    return mean_squared_error(y_test, y_pred, squared=False)

# Optimize SVR
study_svr = optuna.create_study(direction='minimize')
study_svr.optimize(objective_svr, n_trials=100)

# Optimize XGBoost
study_xg = optuna.create_study(direction='minimize')
study_xg.optimize(objective_xg, n_trials=100)

"""**🎲Prediction🎲:**"""

sub["SalePrice"]=np.exp(voting.predict(test))
sub.to_csv('submission.csv',index=False)
sub

