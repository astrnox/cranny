# Wordle+

A word-guessing game. Find the hidden **6-letter** word in **6 tries**. Every guess gets color-coded feedback — and unlike classic Wordle, you can play in **daily, hourly, or infinite** mode.

- **Live demo:** [astrnox.github.io/wordle-plus](https://astrnox.github.io/wordle-plus/)
- **Source:** [github.com/astrnox/wordle-plus](https://github.com/astrnox/wordle-plus)

## How to play

Guess the six-letter word in six attempts. After each guess the tiles tell you how close you were:

| Tile | Meaning |
| --- | --- |
| 🟩 Green | Right letter, right position |
| 🟨 Yellow | Right letter, wrong position |
| ⬜ Gray | Letter not in the word |

Use the feedback to narrow it down, and **green tiles are locked in** for the next guess. Six tries, one word.

### Modes

- **Daily** — one puzzle per day, the same for everyone; come back tomorrow for a new one.
- **Hourly** — a fresh puzzle every hour.
- **Infinite** — endless puzzles, play as long as you like.

It's fully **offline-capable**: it's installable as a PWA and works after the first load.

## How it runs

A self-contained JavaScript bundle with a service worker, installable as a **Progressive Web App**.

```
index.html        # app shell, registers the service worker
build/bundle.js   # the game (compiled bundle)
build/bundle.css  # styles
global.css        # base styles
manifest.json     # PWA manifest
sw.js             # service worker (offline caching)
img/              # icons + social image
```

Keyboard: type letters, `Enter` to submit, `Backspace` to delete.

## Run it locally

```bash
git clone https://github.com/astrnox/wordle-plus.git
cd wordle-plus
python3 -m http.server 8000
# open http://localhost:8000
```

(Service workers need HTTP or HTTPS — `file://` won't register one.)

## Tech stack

- **Language:** JavaScript (bundled)
- **Type:** Progressive Web App (offline, installable)
- **Hosting:** GitHub Pages

## Credits

- Inspired by Josh Wardle's **Wordle** ([wordle.xyz](https://www.wordle.xyz/)); the `+` variant adds hourly & infinite modes.
- This repository is an unblocked web build.
