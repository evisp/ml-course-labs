# Block 2 · the data, settled

A worked notebook, not a fill-in-the-blanks lab. It shows every decision that
`hotels.py` makes on your behalf, including the leak that would have given us a
perfect score, and leaves four questions open at the end.

Run it once before Week 5.

```
python data/download.py --hotels     # from the repository root
jupyter lab block-2-data/notebook.ipynb
```

From Week 5 onwards, every lab starts with:

```python
import sys; sys.path.insert(0, "..")
import hotels

df = hotels.block_2()               # or block_2(sample=20_000) while developing
cancel = hotels.cancellation(df)    # track B, target is 0 or 1
rate = hotels.daily_rate(df)        # track A, target is euros per night
```

The page that goes with this notebook:
https://evisp.github.io/ml-course-umt/03-models-optimization/dataset/
