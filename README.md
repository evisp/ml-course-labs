# ML Course Labs

Lab notebooks for the Machine Learning course at University Metropolitan Tirana.

Course site: https://evisp.github.io/ml-course-umt/

## Setup, once

```bash
git clone https://github.com/evisp/ml-course-labs.git
cd ml-course-labs

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

python data/download.py
```

The last command fetches the Olist dataset into `data/raw/olist/`. It takes a minute and only needs to run once.

## Every week

```bash
git pull
```

Then open `week-NN/lab.ipynb` and **save your own copy** as `my-lab.ipynb` before you start typing. If you edit `lab.ipynb` directly, a later `git pull` can clash with your changes.

The lab has gaps you fill in during class, and check cells that tell you whether you got each part right. The complete `solution.ipynb` appears the same evening.

## Missed a week?

Each lab from Week 2 onwards starts from the table the previous week built, rebuilt from the raw data by `checkpoints.py`. You can pick up at any week, even if you missed the one before.

```python
import sys
sys.path.insert(0, "..")
from checkpoints import week_01

orders = week_01()
```

## Project 1 data

Project 1 uses New York taxi trips from 2026. To download them here:

```bash
python data/download.py --taxi
```

The files land in `data/raw/taxi/`. Your team's own repository should download them itself: the [Project 1 brief](https://evisp.github.io/ml-course-umt/05-projects/project-1-pipeline/) has a short script for that.

## Structure

| Path | Contents |
|---|---|
| `data/download.py` | Fetches the datasets. The data itself is never committed. |
| `checkpoints.py` | Rebuilds each week's starting table from the raw data |
| `week-NN/lab.ipynb` | The in-class notebook, with gaps |
| `week-NN/solution.ipynb` | The complete, narrated version |

## Data

- [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), shared under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Used here for non-commercial teaching.
- [New York City taxi trip records](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page), published by the NYC Taxi and Limousine Commission through NYC Open Data.
