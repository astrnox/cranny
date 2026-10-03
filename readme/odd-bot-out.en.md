# Odd Bot Out

A browser puzzle-observation game. A grid of identical robots is on screen — **only one of them is different.** Find it, click it, and move to the next round. The grid grows and the differences get subtler as you go.

- **Live demo:** [astrnox.github.io/odd-bot-out](https://astrnox.github.io/odd-bot-out/)
- **Source:** [github.com/astrnox/odd-bot-out](https://github.com/astrnox/odd-bot-out)
- **Official site:** [oddbotout.com](https://www.oddbotout.com/)

## How to play

Every round shows a grid of robots that all look alike, except one. Your job is to spot the one that doesn't belong.

1. **Scan** the grid — the odd one usually differs by a single detail: a color, an antenna, an eye, a marking.
2. **Click** the robot you think is different.
3. A correct pick advances you; a wrong one costs a life (or a retry, depending on difficulty).
4. As the levels progress the grid gets larger and the difference becomes easier to miss.

It's a pure eye-training / pattern-spotting game — no timers, no reading, just careful looking.

## How it runs

The game is **native code compiled to WebAssembly with Emscripten**, rendered into an HTML5 `<canvas>`.

```
index.html            # canvas host + loading splash
webapp/index.js       # Emscripten runtime loader
webapp/source_min.js  # compiled game module
webapp/obo.css        # canvas / layout styles
webapp/splash.png     # loading splash
```

A `<progress>` bar shows download/compile progress on first load, then the game fades in.

## Run it locally

Serve over HTTP (the Emscripten module won't load from `file://`):

```bash
git clone https://github.com/astrnox/odd-bot-out.git
cd odd-bot-out
python3 -m http.server 8000
# open http://localhost:8000
```

## Tech stack

- **Game:** native (C/C++) compiled with **Emscripten** to WebAssembly
- **Renderer:** HTML5 `<canvas>`
- **Hosting:** GitHub Pages

## Credits

- Original game: *Odd Bot Out* — [oddbotout.com](https://www.oddbotout.com/)
- This repository is an unblocked web build for play in modern browsers.
