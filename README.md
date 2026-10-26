# Avi Sahni — portfolio

A static site (plain HTML, CSS and a little JS). No framework and no server.

```
public/            the site, which is the only folder that gets hosted
  index.html       home (project sections 01–06)
  about.html       about + résumé
  stfc.html rah.html hyperyouth.html right-to-resist.html dekho.html playground.html
  css/style.css    all styling (Satoshi only, #ffdd00 logo via exclusion blend)
  js/main.js       video autoplay-on-scroll, "Top ↑"
  fonts/           self-hosted Satoshi (Fontshare free licence included)
  img/             wordmark + favicon
  media/           optimised images (.webp) and videos (.mp4), grouped by source
tools/
  build.py         regenerates the .html pages from the content inside it
  media-index.json name -> file/size lookup used by build.py
reference/         the Cargo screenshots + saved page used as the design reference (not hosted)
```

## Editing

Page copy, captions, thumbnail order and gallery order all live in `tools/build.py`.
After changing it, run:

```
python3 tools/build.py
```

and preview with `cd public && python3 -m http.server`.

To add a new image, drop it in `public/media/<project>/`, add an entry to
`tools/media-index.json` (`src`, `w`, `h`; videos also need a `poster`) and reference its key in `build.py`.

## Hosting for free (Cloudflare Pages)

1. Push this repo to GitHub.
2. Cloudflare dashboard → **Workers & Pages → Create → Pages → Connect to Git** → pick this repo.
3. Build command: *(leave empty)*. **Build output directory: `public`**.
4. Deploy. Every push to the production branch redeploys. You get a free `*.pages.dev` address.
5. Optional custom domain: **Custom domains → Set up a domain**. Registering one at Cloudflare costs about $10–12 a year at cost price.

GitHub Pages, Netlify and Vercel also work with the same settings (publish directory `public`).
