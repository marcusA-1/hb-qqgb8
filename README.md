# 🎂 Birthday Card

A single-page, self-contained digital birthday card. No build step, no
dependencies, no tracking, no external requests — one HTML file plus your photos.

**How it plays:**

1. **A wrapped present** sits there rattling until she taps it. It bursts open.
2. **The cake.** Tap the candles to blow them out — or hit **🎤 Blow them out for
   real** and actually blow at her phone. The flames lean over, then go out.
3. **The card.** Confetti cannons, a fireworks finale, her photo in a rainbow
   ring, your message, and a row of polaroid memories she can tap to enlarge.
   A button saves the whole thing as an image for her camera roll.

## Make it yours

Everything personal lives in one place. Open `index.html`, find the `CARD`
object at the top of the `<script>` block, and edit:

```js
const CARD = {
  name: "Birthday Girl",        // who it's for
  age: null,                    // a number shows a badge; null hides it
  candles: 5,                   // 1–12
  giftTag: "To you,\nopen me 💝",

  photo: "assets/photo.jpg",
  photoCaption: "the birthday girl ✨",

  greeting: "Happy birthday!",
  message: [ "…", "…" ],        // each string is its own paragraph
  signature: "— with love",

  galleryTitle: "a few favourites 📷",
  gallery: [
    { src: "assets/memory-1.jpg", caption: "Brighton, 2023" },
    { src: "assets/memory-2.jpg", caption: "" }
  ],

  footer: "made just for you 💛",
  music: true
};
```

**Photos:** main portrait at `assets/photo.jpg`, gallery shots at
`assets/memory-1.jpg` and up. Missing files degrade gracefully: the portrait
falls back to her initial, and the gallery hides itself entirely.

## Swapping the photos

Don't crop by hand — `tools/prepare-photos.py` does it, including stripping the
Instagram app furniture out of a screenshot.

```bash
# drop originals in tools/inbox/, then
bash tools/rebuild-photos.sh
```

It reads `tools/inbox/` in filename order, writes `assets/photo.jpg` from the
first file (or `--main NAME`) and `assets/memory-N.jpg` from the rest.

For a screenshot it locates the photo by scanning for the run of rows that
*aren't* Instagram's flat dark background — chrome rows measure a dead-flat
stddev of 0, a real photo never does, even a night shot — then trims the right
edge where iOS parks its scroll indicator.

Useful flags, all per-file:

| Flag | What it does |
| --- | --- |
| `--main NAME` | which file becomes the round portrait |
| `--zoom NAME=0.8` | tighten the square crop (1.0 = widest that fits) |
| `--focus NAME=0.0` | where the crop sits vertically; 0 keeps the very top |
| `--focus-x NAME=0.7` | where it sits horizontally; 0.5 is centred |
| `--rotate NAME=90` | for photos shot sideways; positive is anticlockwise |
| `--erase-badge NAME` | paints out Instagram's `1/2` carousel pill |
| `--no-crop NAME` | treat a tall image as a normal photo |
| `--debug` | writes `*_debug.png` showing the detected crop |

`--erase-badge` is deliberately opt-in rather than automatic. The pill is drawn
*onto* the photo so no rectangular crop removes it, but auto-detecting it is a
bad trade — a corner full of shelves and vases looks a lot like a pill to a
heuristic, and a wrong guess quietly smears a photo nobody thinks to re-check.

`tools/rebuild-photos.sh` records the settings the current photos needed, with a
note on why each one is there. Originals in `tools/inbox/` are gitignored, so
nothing unpublished rides along to GitHub.

**Bonus:** the name can be overridden in the URL — `?to=Sophie` — so one deploy
works for more than one person.

## Her song

The card embeds **Runaway — Kanye West** from Apple Music. Swap it by editing
the `song` block:

```js
song: {
  title: "Runaway",
  artist: "Kanye West",
  provider: "apple",                 // "apple" or "spotify"
  appleMusic: { album: "1445865909", track: "1445866473", country: "gb" },
  spotify: "3DK6m7It6Pw857FcQftMds",
  file: "",
  tease: true
}
```

To find the ids, open the song on the web and read the URL:

- Apple Music — `music.apple.com/gb/album/<album>?i=<track>`
- Spotify — `open.spotify.com/track/<id>`

**Why an embed and not an MP3.** "Runaway" is a commercial recording. Putting a
copy of it in `assets/` and pushing it to GitHub Pages is publishing it, which
isn't yours to do. The official embed costs nothing, needs no hosting, streams
from the label's own servers, and counts as a play for the artist.

**What she'll actually hear.** Signed in to Apple Music in that browser, the
full track. Otherwise a preview of roughly 30–90 seconds. Either way she gets
the artwork, the title, and a tap-through to the full song. No browser will
autoplay it — she taps play, which is also why the card doesn't try to.

`file:` is there if you have a track you *do* have the rights to (something you
made or bought a licence for). Point it at a file in `assets/` and it plays
inline on loop through the 🔊 toggle, and the embed is skipped.

`tease: true` plays a single soft piano note, repeating, over the candle scene —
a nod to the song's intro before the real thing starts. One pitch, nothing more.
Set it to `false` for silence.

## Preview it locally

Double-click `index.html` and most of it works. Two things need a real server:

- **Blowing into the mic** — browsers only grant microphone access over
  `https://` (or `localhost`).
- **Save as a keepsake** — once a photo is loaded, the browser refuses to export
  the canvas from a `file://` page.

Both work fine once it's on GitHub Pages. To test them beforehand:

```bash
python -m http.server 8000
# then open http://localhost:8000
```

The card detects both cases and shows a friendly note instead of failing.

## Publish it on GitHub Pages

The repo is already initialised and committed. Create an **empty** repo on
GitHub (no README, no .gitignore), then from this folder:

```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

Then on GitHub: **Settings → Pages → Source: Deploy from a branch →
Branch: `main`, folder: `/ (root)` → Save.**

A minute later it's live at:

```
https://<your-username>.github.io/<repo-name>/
```

> Naming the repo `<your-username>.github.io` instead puts it at the bare
> `https://<your-username>.github.io/` — nicer to text someone.

## Notes

- Works on any static host (Netlify, Vercel, a USB stick).
- Respects `prefers-reduced-motion` throughout.
- Keyboard accessible: `Space` blows out the next candle, `Esc` closes a photo.
- Phone haptics on each candle, each firework, and the unwrapping.
- Sound effects (candle puff, firework pops, the piano tease) are generated
  with WebAudio, so there's no audio file to host.
- **The microphone is never recorded or sent anywhere.** The audio stream is
  connected to an analyser and nothing else — not even the speakers — and the
  track is stopped the moment the last candle goes out.
