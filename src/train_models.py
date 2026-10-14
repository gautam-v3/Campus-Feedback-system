"""
Trains the Category SVM and Priority SVM from data/complaints.csv,
saves models + vectorizers into models/, and prints evaluation reports.

Run from the project root:
    python -m src.train_models
"""
import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from config import (
    RAW_CSV_PATH, PROCESSED_CSV_PATH, MODELS_DIR,
    CATEGORY_MODEL_PATH, CATEGORY_VECTORIZER_PATH,
    PRIORITY_MODEL_PATH, PRIORITY_VECTORIZER_PATH,
)
from src.preprocessing import preprocess_text


def _train_one_classifier(df: pd.DataFrame, label_col: str, cmap: str, title: str):
    """Shared train/eval routine for both category and priority models."""
    subset = df.dropna(subset=["clean_text", label_col])
    X = subset["clean_text"]
    y = subset[label_col]

    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    except ValueError:
        # A class has too few samples to stratify — fall back to a plain split
        print(f"[warning] stratify failed for '{label_col}' (a class has <2 samples). "
              f"Falling back to unstratified split.")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 2))
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    model = SVC(kernel="linear", probability=True, random_state=42)
    model.fit(X_train_tfidf, y_train)

    y_pred = model.predict(X_test_tfidf)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n=== {title} ===")
    print(f"Accuracy: {acc:.3f}\n")
    print(classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
    plt.figure(figsize=(7, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap=cmap,
                xticklabels=model.classes_, yticklabels=model.classes_)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(title)
    plt.tight_layout()
    out_path = os.path.join(MODELS_DIR, f"{label_col}_confusion_matrix.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Confusion matrix saved to {out_path}")

    return model, vectorizer, acc


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)

    df = pd.read_csv(RAW_CSV_PATH)
    print(f"Loaded {len(df)} rows from {RAW_CSV_PATH}")

    df["clean_text"] = df["complaint_text"].apply(preprocess_text)
    df.to_csv(PROCESSED_CSV_PATH, index=False)
    print(f"Processed CSV saved to {PROCESSED_CSV_PATH}")

    category_model, category_vectorizer, cat_acc = _train_one_classifier(
        df, "category", "Blues", "Category Confusion Matrix"
    )
    priority_model, priority_vectorizer, pri_acc = _train_one_classifier(
        df, "priority", "Oranges", "Priority Confusion Matrix"
    )

    joblib.dump(category_model, CATEGORY_MODEL_PATH)
    joblib.dump(category_vectorizer, CATEGORY_VECTORIZER_PATH)
    joblib.dump(priority_model, PRIORITY_MODEL_PATH)
    joblib.dump(priority_vectorizer, PRIORITY_VECTORIZER_PATH)

    print("\nAll models and vectorizers saved to models/.")
    print(f"Category accuracy: {cat_acc:.3f} | Priority accuracy: {pri_acc:.3f}")
    print("Remember: priority accuracy alone is not the safety guarantee — "
          "the rule-based safety layer (src/safety_rules.py) sits on top of this model.")


if __name__ == "__main__":
    main()
