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

**Photos:** see [`assets/PUT-PHOTOS-HERE.txt`](assets/PUT-PHOTOS-HERE.txt).
Short version — main portrait at `assets/photo.jpg`, gallery shots at
`assets/memory-1.jpg` and up. Missing files degrade gracefully: the portrait
falls back to her initial, and the gallery hides itself entirely.

**Bonus:** the name can be overridden in the URL — `?to=Sophie` — so one deploy
works for more than one person.

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
- The melody and sound effects are generated with WebAudio, so there's no audio
  file to host. *Happy Birthday to You* has been public domain in the US
  since 2016.
- **The microphone is never recorded or sent anywhere.** The audio stream is
  connected to an analyser and nothing else — not even the speakers — and the
  track is stopped the moment the last candle goes out.
