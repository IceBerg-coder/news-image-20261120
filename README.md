# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/IceBerg-coder/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/IceBerg-coder/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A program that draws a newspaper front page summing up the world news of Friday 20 November 2026 in 35 stories — the Russian barrage that hit three Kyiv bridges, Cyclone Akvan's landfall in Odisha, Asia's AI sell-off, COP31 ending deadlocked, the UK-EU reset deal, missiles coming down in Poland, BepiColombo reaching Mercury, and 22 more — in pure-stdlib Python, with no network and no fonts on disk. Three drawn scenes, a six-number stat strip, a region bar, a numbered world map, and a date check that names the Thursday news left out on purpose.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024x1024, deterministic: two runs produce byte-identical output). The program draws every pixel itself — a 5x7 bitmap font, coloured panels and pictograms — and encodes the PNG with Python's standard library only.

---

<sub>Entered on [make.fun](https://make.fun/?ref=p372g7xd&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
