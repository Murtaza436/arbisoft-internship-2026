from sklearn.datasets import load_iris
from src.data_prep import load_data, split_data
from src.train import train_model
from src.evaluate import evaluate_model


def main():
    iris = load_iris()
    class_names = list(iris.target_names)

    df = load_data()
    X_train, X_test, y_train, y_test = split_data(df)

    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test, class_names=class_names)


if __name__ == "__main__":
    main()
