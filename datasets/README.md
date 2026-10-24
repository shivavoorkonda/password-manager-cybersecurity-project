# Dataset notes

The current Kaggle notebook reads the four attached Kaggle datasets directly. You do not need to download or copy them into this directory to run that notebook.

## Kaggle inputs used by the notebook

| Kaggle dataset | Role in the experiment |
|---|---|
| `bhavikbb/password-strength-classifier-dataset` | Password rows with the dataset's supplied strength labels |
| `wjburns/common-password-list-rockyoutxt` | Common/leaked password examples used as weak examples |
| `shivamb/10000-most-common-passwords` | Common-password examples used as weak examples |
| `joebeachcapital/top-10-million-passwords` | SecLists common-password list used as weak examples |

In Kaggle, attach all four with **Add Data**, then run the notebook at `proposed-improvement/ml-model/kaggle_password_model_training.ipynb`. The code searches under `/kaggle/input` and records its discovered files in the run metadata. Do not use any real personal or account password as training data or a demo input.

## Local-data policy

Raw password lists and evaluation CSV files are intentionally not versioned in this repository. They can contain exposed credentials, are large, and are not required to run the browser demo with the included active model. Obtain them only from the approved Kaggle sources above when retraining or reproducing the evaluation.

Keep password lists in a local, access-controlled workspace; follow each source's terms and provenance. Do not package raw lists or a password dictionary in a public release. The active model package should contain only its model artifacts, feature order, metadata, and documented evaluation summary.

## HIBP data

The Pwned Passwords lookup is a live API call; no HIBP corpus is downloaded by this project. The browser hashes an entered password locally, sends the first five SHA-1 hex characters to the range endpoint, and compares the returned suffixes locally. A lookup result concerns the HIBP corpus and is not a guarantee that an unmatched password has never been exposed.
