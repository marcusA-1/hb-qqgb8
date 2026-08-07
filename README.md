# 🎂 Birthday Card

A single-page, self-contained digital birthday card. Blow out the candles, get
confetti, a photo, and a message. No build step, no dependencies, no tracking —
one HTML file plus a photo.

## Make it yours

Everything personal lives in one place. Open `index.html`, scroll to the
`<script>` block near the bottom, and edit the `CARD` object:

```js
const CARD = {
  name: "Birthday Girl",        // who it's for
  age: null,                    // a number shows a badge; null hides it
  candles: 5,                   // 1–12
  photo: "assets/photo.jpg",
  photoCaption: "the birthday girl ✨",
  greeting: "Happy birthday!",
  message: [ "…", "…" ],        // each string is its own paragraph
  signature: "— with love",
  footer: "made just for you 💛",
  music: true
};
```

**The photo:** save it as `assets/photo.jpg`. Square-ish crop, ~800×800, under
~500 KB. If it's missing the card falls back to her first initial, so it never
looks broken.

**Bonus:** you can override the name in the URL — `?to=Sophie` — so the same
deploy works for more than one person.

## Preview it locally

Just double-click `index.html`. (Or `python -m http.server` in this folder and
visit http://localhost:8000 if you want it served properly.)

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

- Works offline and on any static host (Netlify, Vercel, a USB stick).
- Respects `prefers-reduced-motion` for anyone sensitive to animation.
- Keyboard accessible: `Space` blows out the next candle.
- The melody is generated with WebAudio, so there's no audio file to host.
  *Happy Birthday to You* has been public domain in the US since 2016.
