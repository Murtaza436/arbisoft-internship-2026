import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split


def load_data():
    """Load the Iris dataset and return as a DataFrame."""
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["target"] = iris.target
    df["target_name"] = df["target"].map(
        {i: name for i, name in enumerate(iris.target_names)}
    )
    return df


def split_data(df, target_col="target", test_size=0.2, random_state=42):
    """Split DataFrame into train and test sets."""
    X = df.drop(columns=[target_col, "target_name"])
    y = df[target_col]
    return train_test_split(X, y, test_size=test_size, random_state=random_state)
