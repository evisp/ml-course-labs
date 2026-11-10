# Week 03 · Feature engineering

**The question this week:** which features help predict late delivery, and how do you build them so they cannot leak?

In this lab you:

- tell apart row-wise features, computed from one row, from learned features, computed from many
- build distance, same state, promised window and freight ratio, and test each one alone
- watch a seller's late rate leak when it is computed over all the data, and fix it
- write your own scikit-learn transformer, with `fit` and `transform`
- put preprocessing and model into one pipeline
- see why target encoding needs cross-fitting, and why logistic regression needs scaling
- let validation decide which features earn their place, then score the chosen model on test once

Open `lab.ipynb`, save your own copy as `my-lab.ipynb`, and work in that. The lab is longer than one session on purpose: finish at home.

Starts from `week_02()` in `checkpoints.py`. Needs the data from `python data/download.py`.
