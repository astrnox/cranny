# Arkadium's Bubble Shooter

The classic **bubble shooter**, unblocked and playable in any modern browser. Aim, shoot, and match **three or more** bubbles of the same color to pop them. Clear every bubble on the board before they push down to the bottom line — or you lose.

- **Live demo:** [astrnox.github.io/arkadiumx27s-bubble-shooter](https://astrnox.github.io/arkadiumx27s-bubble-shooter/)
- **Source:** [github.com/astrnox/arkadiumx27s-bubble-shooter](https://github.com/astrnox/arkadiumx27s-bubble-shooter)

## How to play

Bubbles drift down from the top in a packed hexagonal arrangement. You control the shooter at the bottom.

- **Aim** with the mouse — the guide line shows where the next bubble will travel (it bounces off walls).
- **Click / tap** to fire the bubble from the cannon.
- Bubbles **stick** to the cluster on contact. Match **3+ of the same color** and they pop, everything above them drops.
- Every shot you don't land pushes the pack **down a row**. Let any bubble cross the bottom line and the game ends.
- Clear the entire board to advance — later levels add more colors and tighter layouts, so stray shots hurt more.

The tension is placement: the obvious shot isn't always the safe one, and a bad bounce can set up a cascade you didn't want.

## Controls

| Action | Input |
| --- | --- |
| Aim | Move mouse / drag finger |
| Shoot | Click / tap |

## How it runs

An **HTML5/JavaScript** build of Arkadium's Bubble Shooter (the version published on CrazyGames), loaded as a single compiled bundle.

```
index.html      # page shell, loads the game bundle
build/main.js   # the game engine + game code (content-hashed)
adSense.js      # ad script stub
```

The canvas fills the page and scales to any window size; it works with mouse and touch.

## Run it locally

Serve over HTTP (bundled scripts won't load from `file://`):

```bash
git clone https://github.com/astrnox/arkadiumx27s-bubble-shooter.git
cd arkadiumx27s-bubble-shooter
python3 -m http.server 8000
# open http://localhost:8000
```

## Tech stack

- **Language:** JavaScript (HTML5 build)
- **Renderer:** HTML5 `<canvas>`
- **Hosting:** GitHub Pages

## Credits

- Original game: *Arkadium's Bubble Shooter*, published on [CrazyGames](https://www.crazygames.com/). All rights to Arkadium / CrazyGames.
- This repository is an unblocked web build for play in modern browsers.
