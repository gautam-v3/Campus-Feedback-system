"""
Entry point: train category + priority SVMs and build/save the NER pipeline.

Usage (from project root, in your activated venv):
    python main_train.py
"""
from src.train_models import main as train_classifiers
from src.ner_pipeline import build_ner_pipeline, save_ner_pipeline

if __name__ == "__main__":
    train_classifiers()

    print("\nBuilding NER pipeline...")
    nlp = build_ner_pipeline()
    save_ner_pipeline(nlp)
    print("NER pipeline saved to models/campus_ner_model")
    print("\nTraining complete. Run: python main_infer.py")
