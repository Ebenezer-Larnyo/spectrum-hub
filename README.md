# Spectrum Hub

One searchable place for autism resources, built by Dr Ebenezer Larnyo from the recommendations in his paper Larnyo et al. (2024), Frontiers in Psychiatry 15:1441349:
research-backed tools sorted by common issues, connected community institutions, and accessible design.

## Host it (GitHub Pages, free)
1. Before anything else, set a real contact URL or email in the `UA` line of `crawler.py` and check each source's terms of use.
2. Create a GitHub repository and upload this folder's contents, with `index.html` at the top level.
3. Settings > Pages > "Deploy from a branch" > `main` and `/ (root)`. The site appears at `https://YOUR-USERNAME.github.io/REPO-NAME/`.
4. `.github/workflows/refresh.yml` re-crawls every Monday at 06:00 UTC and commits the new data. You can also run it from the Actions tab. Public repositories pause scheduled runs after 60 days without activity.
5. Optional: add a custom domain in Settings > Pages and tick "Enforce HTTPS".
6. AI companion: on claude.ai it works on its own. On other hosts, deploy `companion-server/` (a small Cloudflare Worker that holds your API key; see its README) and set `ENDPOINT` in `index.html`. Or remove the Companion link and view.
7. Before real users: clinician review of the crisis wording, testing with autistic adults and caregivers, an accessibility check, a privacy notice (the Google Fonts links share visitors' addresses with Google, so self-host the fonts if you serve EU visitors), and an age policy.

## Run it locally
    pip install -r requirements.txt
    python crawler.py --sources sources.json --out resources.json --inject index.html
Open `index.html` in a browser, or host it on any static host. Re-run the crawler on a schedule (cron or GitHub Actions) to refresh.

## What the crawler does
- Reads only the sites listed in `sources.json` and stays inside each source's `allow` prefixes.
- Obeys robots.txt (skips a site if it cannot be read) and waits `--delay` seconds (default 1.5) between requests.
- Keeps only pages that are about autism, then sorts them into the nine topics in `CATS` using keyword scores on the title and text.
- Removes duplicates and records the date each page was checked.
- Does not crawl forums or social media, and stores no personal data. Set a contact URL in `UA` before real use.

## Add a source
Add an object to `sources.json` (name, tier: gov / academic / nonprofit / community, seeds, allow, audience, cats, max_pages). Check the site's terms of use first.

## Design for autistic people and caregivers
- Calm illustrated landscape, soft palettes (Sage, Paper, Dusk), one legible font family plus a plain-font option.
- Comfort settings: text size, colors, roomy spacing, high contrast, gentle motion (off by default), and hide pictures.
- Predictable layout, a three-step guide, no autoplay or sound, links that say when they open a new tab, and a "Take a pause" screen.
- The puzzle-piece symbol is deliberately not used, because many autistic people dislike it.

## AI companion (text-first prototype, `#companion` view)
- Audience modes: autistic person, caregiver, or both, changeable any time.
- Type/Talk toggle sharing one transcript; voice input and spoken replies use the browser's speech features (where supported), with captions always shown.
- Human-like avatar, labelled "AI companion", with hide, mute, look and reduced-motion controls.
- Memory is off by default and stores preferences only (never conversation text); users can view, forget one item, forget all, or download them.
- Crisis phrases skip the model and show a fixed message with 988/911. Replies can link only to entries in the Hub's own resource list.
- Replies come from Claude through the page's `sample` capability (declare `capabilities: {sample: {}, downloads: true}` when publishing on claude.ai). To host it elsewhere, replace `getSample()` with a call to your own server endpoint that holds the model key.
- Still needed before real users: clinician review of the crisis protocol, co-design testing with autistic adults and caregivers, an age policy, and a privacy review.

## Not included yet
A moderated community of people (needs accounts, moderation and safety policies) and a location-based provider search (needs a vetted directory or API).
Starter entries in `index.html` are marked "not yet crawled" until you run the crawler.
