# Temple of Boom

An unblocked, browser-playable build of the classic Flash action game **Temple of Boom**. Explore a crumbling temple, time your jumps between platforms, and fight your way through traps and guardians.

Play it instantly in your browser — no install, no Flash needed.

## Play

- **Live demo:** [astrnox.github.io/temple-of-boom](https://astrnox.github.io/temple-of-boom/)
- **Source:** [github.com/astrnox/temple-of-boom](https://github.com/astrnox/temple-of-boom)

## How to play

You are dropped into the depths of an ancient temple. The way out is at the top.

- **Move** with the keyboard and **jump** with the jump key.
- Land on platforms precisely — a mistimed jump sends you back to the ledge.
- Dodge traps and defeat the temple's guardians on the way up.
- The higher you climb, the faster the action gets. There is no checkpointing: a single mistake costs you a life.

Collect coins and power-ups along the route to extend your run. The game gets progressively harder as you ascend, so the run always ends somewhere — the goal is to beat your best.

## Controls

| Action | Input |
| --- | --- |
| Move left / right | `←` `→` or `A` / `D` |
| Jump | `↑` / `W` / `Space` |
| Interact | `E` / `Enter` |

> Controls follow the standard keyboard layout of the original Flash release; on-screen prompts appear in-game if you're unsure.

## How it runs

This is an **Adobe Flash (ActionScript) game** running through [Ruffle](https://ruffle.rs), the open-source Flash Player emulator written in Rust. The page boots the Ruffle runtime and embeds the compiled `TempleBoom` SWF.

```
index.html                              # boots Ruffle, embeds the SWF
TempleBoom_CustomPreloader_ForColin.js   # Ruffle (Lime) player bootstrap
*.swf                                    # the compiled game itself
adSense.js                              # ad script stub
```

The original game canvas runs at **624×400** and is scaled to fit your browser window.

## Run it locally

Because the page loads the Flash runtime and assets, serve it over HTTP (opening `index.html` via `file://` will be blocked by the browser):

```bash
git clone https://github.com/astrnox/temple-of-boom.git
cd temple-of-boom
python3 -m http.server 8000
# open http://localhost:8000
```

Any static file server works (`npx serve`, `php -S`, etc.).

## Tech stack

- **Game:** Adobe Flash / ActionScript (`.swf`)
- **Runtime:** [Ruffle](https://ruffle.rs) — open-source Flash Player emulator
- **Bootstrap:** plain HTML + a single embed script
- **Hosting:** GitHub Pages

## Credits

- Original game: *Temple of Boom* (Flash) — all rights to the original creator.
- This repository is an unblocked, Ruffle-powered web build for play in modern browsers.
