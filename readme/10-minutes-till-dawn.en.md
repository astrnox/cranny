# 10 Minutes Till Dawn

A top-down survival shooter. Monsters pour in from every side and your character **attacks automatically** — your only job is to keep moving, dodge the horde, and survive **ten minutes**. Upgrades trickle in between waves; how you spend them decides how far you get.

- **Live demo:** [astrnox.github.io/10-minutes-till-dawn](https://astrnox.github.io/10-minutes-till-dawn/)
- **Source:** [github.com/astrnox/10-minutes-till-dawn](https://github.com/astrnox/10-minutes-till-dawn)

## How to play

You start at the bottom of a dark field with a lantern. The clock is always running — **survive until the ten-minute mark.**

- Your weapon **fires on its own**, always at the nearest enemy. You never aim; you *position*.
- **Move** with the movement keys to kite the swarm, slip through gaps, and avoid getting surrounded.
- Enemies spawn faster and in nastier formations the longer you last.
- Kill enemies to earn XP. On level-up you **pick one upgrade** — extra damage, faster fire, more speed, more HP, and so on.
- Die and the run ends. Survive the full ten minutes and you win.

There's no aiming and no ammo — pure movement and build choice. The tension comes from managing crowd density: let enemies surround you and even auto-attack can't save you.

## Controls

| Action | Input |
| --- | --- |
| Move | `W` `A` `S` `D` or arrow keys |
| Attack | automatic (targets nearest enemy) |
| Pause | `Esc` / `P` |

## How it runs

The game is built in **Unity** and exported to **WebGL**, so the browser downloads a `.wasm` build and runs it on a `<canvas>`.

```
index.html                          # Unity bootstrap + scaling logic
Build/10MinutesTillDawnWebGL.json    # Unity build manifest
Build/*.wasm, *.data                # Unity WebGL payload
js/main.js                          # page script
icon.png                            # favicon
```

The game renders at a fixed **675×1200** portrait resolution and is letterboxed/scaled to fit your window (the `onResize` handler keeps the 9:16 aspect). Add `?pixelated` rendering for crisp pixel art.

## Run it locally

Unity WebGL builds must be served over HTTP with the correct MIME types (in particular `.wasm` and `.data`):

```bash
git clone https://github.com/astrnox/10-minutes-till-dawn.git
cd 10-minutes-till-dawn
python3 -m http.server 8000
# open http://localhost:8000
```

A plain `python3 -m http.server` is enough for local play; for a closer-to-production setup use `npx serve` or Nginx.

## Tech stack

- **Engine:** Unity (C#)
- **Export:** Unity WebGL (WebAssembly)
- **Hosting:** GitHub Pages

## Credits

- Original game: *10 Minutes Till Dawn* — a Unity WebGL survival shooter. All rights to the original creator.
- This repository is an unblocked web build for play in modern browsers.
