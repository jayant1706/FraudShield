# FraudShield Dataset Directory

This directory holds the credit card fraud benchmark dataset.

### Kaggle Dataset Reference:
- **Dataset:** Credit Card Fraud Detection (284,807 transactions, European cardholders)
- **Kaggle URL:** [https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- **Path:** Place `creditcard.csv` in `ml/data/raw/creditcard.csv`

### Synthetic Benchmark Generation:
If the raw Kaggle dataset is not pre-downloaded, the data ingestion pipeline automatically falls back to generating a synthetic benchmark dataset with identical distribution (`0.172%` fraud class ratio, PCA components V1-V28, Time, and Amount) so the pipeline works seamlessly out of the box.

*Note: Raw `.csv` datasets and processed `.parquet` files are ignored by git via `.gitignore` to comply with version control best practices.*

