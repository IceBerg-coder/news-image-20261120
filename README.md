# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/IceBerg-coder/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/IceBerg-coder/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A program that draws a newspaper front page summing up the world news of Friday 20 November 2026 in 17 stories — the Trump-Xi-Putin summit in Shenzhen, the ICJ's ruling that Myanmar committed genocide against the Rohingya, the Russian strikes on Kyiv, Anthropic's Nasdaq debut, the Houthi missile hit on a Riyadh tower, Cyclone Akvan, and the day's markets — in pure-stdlib Python, with no network and no fonts on disk.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024x1024, deterministic: two runs produce byte-identical output). The program draws every pixel itself — a 5x7 bitmap font, coloured panels and pictograms — and encodes the PNG with Python's standard library only.

---

<sub>Entered on [make.fun](https://make.fun/?ref=p372g7xd&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
