# Week 02 · Data quality and splitting

**The question this week:** how do you turn seven messy tables into one clean row per order, and how do you test a model the way it will really be used?

In this lab you:

- find what one row means in every table, and watch a join quietly add eighteen thousand rows
- audit the data with a checklist, and fix each problem in a way you can repeat
- build one clean row per order, checking the row count after every join
- split by time **before** exploring the target
- explore the training data with five charts, each pointing to a feature for next week
- rerun Week 1's baselines on a time-based split, and see what a random split was hiding

Open `lab.ipynb`, save your own copy as `my-lab.ipynb`, and work in that. The lab is longer than one session on purpose: finish at home.

Starts from `week_01()` in `checkpoints.py`. Needs the data from `python data/download.py`.
