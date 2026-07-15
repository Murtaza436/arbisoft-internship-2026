from src.data_prep import load_data, split_data


def test_load_data_shape():
    """Iris has 150 rows and 6 columns (4 features + target + target_name)."""
    df = load_data()
    assert df.shape == (150, 6)


def test_load_data_columns():
    """Check expected columns exist."""
    df = load_data()
    assert "target" in df.columns
    assert "target_name" in df.columns


def test_split_data_sizes():
    """Default 80/20 split should give 120 train and 30 test rows."""
    df = load_data()
    X_train, X_test, y_train, y_test = split_data(df)
    assert len(X_train) == 120
    assert len(X_test) == 30


def test_split_no_overlap():
    """Train and test indices must not overlap."""
    df = load_data()
    X_train, X_test, _, _ = split_data(df)
    train_idx = set(X_train.index)
    test_idx = set(X_test.index)
    assert train_idx.isdisjoint(test_idx)
