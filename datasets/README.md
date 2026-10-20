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

## Files already in this repository

This checkout currently tracks several password-list and strength-dataset files, including `password_strength.csv`, `rockyou.txt`, `top10k-common-passwords.csv`, and `xato-net-10-million-passwords.csv`. These files are not needed for the current Kaggle notebook. The older local `prepare_data.py` pipeline refers to this different set of files and should not be confused with the four-input Kaggle experiment.

Password lists can contain exposed credentials. Keep them only for the approved class research, follow each source's terms and provenance, and avoid copying them into public artifacts. The model ZIP should contain model files, feature order, metadata, and the training dictionary only; do not package the raw password lists. `dictionary.txt` is ignored by Git because it contains password strings.

## HIBP data

The Pwned Passwords lookup is a live API call; no HIBP corpus is downloaded by this project. The browser hashes an entered password locally, sends the first five SHA-1 hex characters to the range endpoint, and compares the returned suffixes locally. A lookup result concerns the HIBP corpus and is not a guarantee that an unmatched password has never been exposed.
