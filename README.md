# The World in One Day — Tuesday 17 November 2026

[![make.fun](https://img.shields.io/badge/make.fun-news--image--20261117-blue)](https://make.fun/bounty/news-image-20261117)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Size: 1024x1024](https://img.shields.io/badge/size-1024x1024-green.svg)](entry.png)

A newspaper front page that sums up the world news of Tuesday 17 November
2026 in one image: the Kerch Bridge struck again, tankers hit mines off
Hormuz, Trump lands in Manila with a Xi summit set for Thursday, the Chase
banking outage, Europe's Rwanda return hub plan, and Nvidia reporting after
Huang's exit.

## How it works

`gen_image.py` draws `entry.png` (1024x1024, stdlib-only Python: a hand-made
PNG encoder and a hand-made 5x7 bitmap font). `main.ts` (Node 22, stdlib
only) copies `entry.png` to the output directory as `entry.png`.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Competition: https://make.fun/bounty/news-image-20261117
