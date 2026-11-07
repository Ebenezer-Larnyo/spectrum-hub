# Spectrum Hub

One searchable place for autism resources, built from the recommendations in Larnyo et al. (2024), Frontiers in Psychiatry 15:1441349:
research-backed tools sorted by common issues, connected community institutions, and accessible design.

## Host it (GitHub Pages, free)
1. Before anything else, set a real contact (an email, plus your site's `#about` page) in the `UA` line of `crawler.py` and check each source's terms of use. Example: `UA = "SpectrumHubBot/0.1 (research project; contact: spectrumhub.project@protonmail.com; +https://ebenezer-larnyo.github.io/spectrum-hub/#about)"`.
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

## Search visibility and analytics
- `python build_site.py` writes static pages (about, privacy, glossary, topics, starting points, regions, 404), `sitemap.xml` and `robots.txt`, and refreshes the page title, description, social tags and structured data in `index.html`. The weekly workflow runs it after the crawl.
- Edit the goals, glossary and topic introductions in `content.json` (not in `index.html`) and re-run the script. Settings are in `site_config.json`.
- If you use a custom domain, change `site_url` in `site_config.json` and re-run the script. Note that search engines only read `robots.txt` at the root of a domain, so on a github.io project address it has no effect, which is fine because crawling is allowed by default.
- Register the site in Google Search Console and Bing Webmaster Tools, add the verification codes in `site_config.json`, and submit `sitemap.xml`.
- Analytics are off by default. To count visits without cookies, set `analytics` in `site_config.json` to `{"provider": "goatcounter", "code": "YOUR-CODE"}` or `{"provider": "cloudflare", "code": "YOUR-TOKEN"}`, then run the script. It adds the script tag to every page and updates the privacy page to describe the counting.

## Contact details, regions and community focus
- `site_config.json` holds the contact email and site address. The crawler builds its `UA` (the name it gives websites) from it, and the About and Privacy pages use it, so they always agree. Set `contact_email` to the address you actually read.
- Regions: `us`, `uk`, `ca`, `au`, `gh` (Ghana), `za` (South Africa) and `global`. To add one, add it to the region list and `REG` map in `index.html` and to `REG` in `build_site.py`, then use it in `sources.json`.
- Community focus: give a source `"focus": ["black"]` (or `latino`, `asian`, `indigenous`, `minority`). A "Community focus" filter appears on the page once any source has a focus, and `build_site.py` writes a page for each focus under `community/`.
- `sources.candidates.json` has unverified starting points and templates for Ghana, South Africa and community-focused sources. Look up and verify each official address, check the site's terms and robots.txt, then move the entry into `sources.json`.

## Avatar
The companion's avatar is generated from a handful of choices (skin tone, hair, eyes, glasses, clothing, colors, or a soft-shapes style). No photos are used or uploaded. The design is saved only if the user turns on Memory.

## Regions, starter steps and glossary
- Each resource has a `regions` list (`us`, `uk`, `ca`, `au` or `global`). The "Where are you?" filter shows the chosen region plus anything marked global. Set a source's region in `sources.json`.
- `sources.candidates.json` lists possible UK, Australian and Canadian sources. I have not checked their pages or terms: verify the web addresses and each site's terms and robots.txt, then move entries into `sources.json`.
- The "Not sure where to start?" goals (`GOALS`) and the glossary (`GL`) are plain lists in `index.html`. Have a clinician and autistic reviewers check the wording before wide release.

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
