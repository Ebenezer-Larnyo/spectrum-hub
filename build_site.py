#!/usr/bin/env python3
"""Builds the static, search-friendly pages and refreshes SEO tags in index.html.

Writes: about.html, privacy.html, glossary.html, topics/, start/, regions/, 404.html,
sitemap.xml, robots.txt. Reads: index.html (resource data, styles), content.json, site_config.json.
Run after the crawler:  python build_site.py
"""
import datetime as dt
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
CFG = json.loads((ROOT / "site_config.json").read_text(encoding="utf-8"))
TEAM = None
CONTENT = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
TEAM = CFG.get("team", [])
SITE = CFG["site_url"].rstrip("/")
NAME = CFG["site_name"]
EMAIL = CFG["contact_email"]
TODAY = dt.date.today().isoformat()
e = html.escape

NEEDS = [("signs", "Understand signs and symptoms"), ("diagnosis", "Get a diagnosis"), ("care", "Find care and therapies"),
         ("caregivers", "Support for caregivers"), ("mental", "Mental health and sleep"), ("tech", "Tools and technology"),
         ("advocacy", "Self-advocacy and acceptance"), ("daily", "Everyday life and routines"), ("local", "Find local services")]
NEED_LABEL = dict(NEEDS)
TIER = {"gov": "Government", "academic": "University or journal", "nonprofit": "Nonprofit", "community": "Community-run"}
ORDER = {"gov": 0, "academic": 1, "nonprofit": 2, "community": 3}
REG = {"global": "Anywhere", "us": "United States", "uk": "United Kingdom", "ca": "Canada", "au": "Australia", "gh": "Ghana", "za": "South Africa"}
FOCUS = {"black": "Black communities", "latino": "Latino and Hispanic communities", "asian": "Asian communities",
         "indigenous": "Indigenous communities", "minority": "Racial and ethnic minority communities"}
HOME_DESC = ("Search links from selected public autism sources, including health agencies, universities and nonprofits, in one calm place. "
             "Topics, next steps, a plain-language glossary and an AI companion, for autistic people and caregivers.")

src = (ROOT / "index.html").read_text(encoding="utf-8")
DATA = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', src, re.S).group(1))
STYLE = re.search(r"<style>.*?</style>", src, re.S).group(0)
FONTS = "\n".join(re.findall(r'<link rel="(?:preconnect|stylesheet)"[^>]*>', src))
BRAND = re.search(r'<a class="brand".*?</a>', src, re.S).group(0)
COMFORT = re.search(r'<details class="comfort">.*?</details>', src, re.S).group(0)
ICON = '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 100 100%27%3E%3Ctext y=%27.9em%27 font-size=%2790%27%3E%F0%9F%8C%BF%3C/text%3E%3C/svg%3E">'

FOCUS_SET = sorted({f for r in DATA for f in r.get("focus", [])})
pages = []  # (path, priority)
TITLES = {}


def regions_of(r):
    return r.get("regions") or ["global"]


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def analytics_tag():
    a = CFG.get("analytics", {})
    p, code = a.get("provider", ""), a.get("code", "")
    if p == "goatcounter" and code:
        return f'<script data-goatcounter="https://{e(code)}.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'
    if p == "cloudflare" and code:
        return f"<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{\"token\": \"{e(code)}\"}}'></script>"
    return ""


def verification():
    out = ""
    if CFG.get("google_verification"):
        out += f'<meta name="google-site-verification" content="{e(CFG["google_verification"])}">'
    if CFG.get("bing_verification"):
        out += f'<meta name="msvalidate.01" content="{e(CFG["bing_verification"])}">'
    return out


def seo_head(title, desc, path, ld=None):
    url = SITE + "/" + path if path else SITE + "/"
    t = [f'<meta name="description" content="{e(desc)}">', f'<link rel="canonical" href="{e(url)}">',
         '<meta property="og:type" content="website">', f'<meta property="og:site_name" content="{e(NAME)}">',
         f'<meta property="og:title" content="{e(title)}">', f'<meta property="og:description" content="{e(desc)}">',
         f'<meta property="og:url" content="{e(url)}">', f'<meta property="og:image" content="{e(SITE)}/og.png">',
         '<meta name="twitter:card" content="summary_large_image">', ICON, verification()]
    if ld:
        t.append(jsonld(ld))
    return "\n".join(x for x in t if x)


MINI_JS = """<script>
(function(){var b=document.getElementById('totop');if(!b)return;function vis(){b.hidden=(window.pageYOffset||document.documentElement.scrollTop||0)<500}window.addEventListener('scroll',vis,{passive:true});vis();b.onclick=function(){var calm=document.documentElement.hasAttribute('data-calm')||(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches);window.scrollTo({top:0,behavior:calm?'auto':'smooth'});var h=document.querySelector('.brand');if(h&&h.focus)h.focus({preventScroll:true})}})();
(function(){var r=document.documentElement,$=function(i){return document.getElementById(i)},K='sh-mem',m=null;
try{m=JSON.parse(localStorage.getItem(K)||'null')}catch(e){}if(!(m&&m.on))m=null;
var P={size:100,contrast:false,calm:false,motion:false,font:'',space:false,theme:(window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dusk':'sage')};
if(m)['size','contrast','calm','motion','font','space','theme'].forEach(function(k){if(k in m)P[k]=m[k]});
function fl(n,on,v){on?r.setAttribute(n,v||''):r.removeAttribute(n)}
function ap(){r.style.fontSize=P.size+'%';fl('data-theme',true,P.theme);fl('data-contrast',P.contrast);fl('data-calm',P.calm);fl('data-motion',P.motion);fl('data-font',P.font==='plain','plain');fl('data-space',P.space);
['contrast','calm','motion','space'].forEach(function(k){$(k).setAttribute('aria-pressed',String(P[k]))});$('font').setAttribute('aria-pressed',String(P.font==='plain'));
['sage','paper','dusk'].forEach(function(t){$('th-'+t).setAttribute('aria-pressed',String(P.theme===t))})}
function set(k,v){P[k]=v;ap();if(m){m[k]=v;try{localStorage.setItem(K,JSON.stringify(m))}catch(e){}}}
$('smaller').onclick=function(){set('size',Math.max(85,P.size-15))};$('larger').onclick=function(){set('size',Math.min(160,P.size+15))};
['contrast','calm','motion','space'].forEach(function(k){$(k).onclick=function(){set(k,!P[k])}});
$('font').onclick=function(){set('font',P.font==='plain'?'':'plain')};
['sage','paper','dusk'].forEach(function(t){$('th-'+t).onclick=function(){set('theme',t)}});ap()})();
</script>"""


TOTOP = '<button type="button" id="totop" class="totop" hidden aria-label="Back to top"><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg><span>Top</span></button>'


def shell(title, desc, path, body, ld=None, depth=0, noindex=False):
    TITLES[path] = title.replace(" | " + NAME, "")
    root = "../" * depth
    foot = (f'<nav aria-label="About" style="margin-bottom:8px"><a href="{root}about.html">About and contact</a> · '
            f'<a href="{root}privacy.html">Privacy and safety</a> · <a href="{root}glossary.html">Glossary</a> · '
            f'<a href="{root}topics/index.html">Topics</a> · <a href="{root}start/index.html">Start here</a> · '
            f'<a href="{root}community/index.html">Communities</a> · <a href="{root}sitemap.html">Site map</a> · '
            f'<a href="{root}index.html">Search all resources</a></nav>')
    brand = BRAND.replace('href="#hub"', f'href="{root}index.html"')
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
{seo_head(title, desc, path, ld)}{'<meta name="robots" content="noindex">' if noindex else ''}
{FONTS}
{STYLE}
{analytics_tag()}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap bar">{brand}
<nav class="sec" aria-label="Sections"><a href="{root}index.html">Resources</a><a href="{root}topics/index.html">Topics</a><a href="{root}start/index.html">Start here</a><a href="{root}community/index.html">Communities</a><a href="{root}glossary.html">Glossary</a><a href="{root}index.html#companion">Companion</a><a href="{root}about.html">About</a></nav>
<div class="tools">{COMFORT}</div></div><div class="ribbon" aria-hidden="true"></div></header>
<main class="wrap" id="main">
{body}
</main>
<footer><div class="wrap">{foot}{NAME} collects and sorts links from selected public autism sources. It does not independently verify or endorse them, and it does not give medical advice. Design based on the recommendations of Larnyo, Nutakor, Addai-Dansoh and Nkrumah (2024), <a href="https://doi.org/10.3389/fpsyt.2024.1441349" target="_blank" rel="noopener noreferrer">Frontiers in Psychiatry 15:1441349<span class="vh"> (opens in a new tab)</span></a>.</div></footer>
{TOTOP}
{MINI_JS}
</body>
</html>
"""
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return page


def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + "/" + p} for i, (n, p) in enumerate(items)]}


depth_hint = [1]


def focus_txt(r):
    f = r.get("focus", [])
    return ("Focus: " + e(", ".join(FOCUS.get(x, x) for x in f)) + ". ") if f else ""


def resource_list(rs):
    rs = sorted(rs, key=lambda r: (ORDER.get(r["tier"], 9), r["title"].lower()))
    if not rs:
        return '<p class="empty">We have not collected resources for this yet. Check back soon, or <a href="' + ('../' * depth_hint[0]) + 'index.html">search all resources</a>.</p>'
    li = []
    for r in rs:
        chk = "Starter entry, not yet crawled." if r.get("checked") == "seed" else "Checked " + e(str(r.get("checked", "")))
        li.append(f'<li class="item" style="--tc:var(--{e(r["tier"])})"><h3><a href="{e(r["url"])}" target="_blank" rel="noopener noreferrer">{e(r["title"])}'
                  f'<span class="vh"> (opens in a new tab)</span></a><span class="nt" aria-hidden="true">opens in a new tab</span></h3>'
                  f'<p class="meta"><b>{TIER.get(r["tier"], "Other")}</b> from {e(r["source"])} ({e(", ".join(REG.get(x, x) for x in regions_of(r)))}). {focus_txt(r)}{chk}</p>'
                  f'<p>{e(r["summary"])}</p></li>')
    return '<ul id="list">' + "".join(li) + "</ul>"


def add(path, prio="0.6"):
    pages.append((path, prio))


# ---------------------------------------------------------------- topics
topics = [(i, l, [r for r in DATA if i in r["cats"]]) for i, l in NEEDS]
topics = [t for t in topics if t[2]]
for i, label, rs in topics:
    intro = CONTENT["topic_intro"].get(i, "")
    goals = [g for g in CONTENT["goals"] if g["need"] == i]
    gl = "".join(f'<li><a href="../start/{g["id"]}.html">{e(g["label"])}</a></li>' for g in goals)
    body = (f'<section class="heroplain"><p><a href="index.html">All topics</a></p><h1>{e(label)}: autism resources</h1><p class="lede">{e(intro)}</p></section>'
            f'<h2 style="margin-top:28px">{len(rs)} {"resource" if len(rs) == 1 else "resources"}</h2>{resource_list(rs)}'
            + (f'<section class="card" style="margin-top:24px"><h2>Not sure where to start?</h2><ul>{gl}</ul></section>' if goals else "")
            + '<p style="margin-top:24px">These links lead to other websites and are not medical advice. <a href="../glossary.html">New to the words? See the glossary.</a></p>')
    shell(f"{label}: autism resources | {NAME}", f"{intro[:150].rstrip()} Links from selected public sources, collected in one place.".replace("  ", " ")[:300],
          f"topics/{i}.html", body, crumbs([("Home", ""), ("Topics", "topics/index.html"), (label, f"topics/{i}.html")]), 1)
    add(f"topics/{i}.html", "0.7")
cards = "".join(f'<li class="item"><h3><a href="{i}.html">{e(l)}</a></h3><p>{e(CONTENT["topic_intro"].get(i, ""))}</p><p class="meta">{len(rs)} {"resource" if len(rs) == 1 else "resources"}</p></li>' for i, l, rs in topics)
shell(f"Autism topics | {NAME}", "Browse autism resources by topic: signs, diagnosis, care, caregiver support, mental health and sleep, tools, self-advocacy, everyday life and local services.",
      "topics/index.html", f'<section class="heroplain"><h1>Browse by topic</h1><p class="lede">Choose a topic to see links collected from selected public sources.</p></section><ul id="list" style="margin-top:24px">{cards}</ul>',
      crumbs([("Home", ""), ("Topics", "topics/index.html")]), 1)
add("topics/index.html", "0.8")

# ---------------------------------------------------------------- start here (goals)
for g in CONTENT["goals"]:
    rs = [r for r in DATA if g["need"] in r["cats"] and (not g.get("aud") or g["aud"] in r["audience"])]
    steps = "".join(f"<li>{e(a)}</li>" for a in g["acts"])
    body = (f'<section class="heroplain"><p><a href="index.html">All starting points</a></p><h1>{e(g["label"])}</h1><p class="lede">Three small next steps. These are general ideas, not medical advice.</p></section>'
            f'<section class="card" style="margin-top:20px"><ol style="max-width:68ch">{steps}</ol></section>'
            f'<h2 style="margin-top:28px">Resources that may help</h2>{resource_list(rs)}'
            f'<p style="margin-top:24px">' + (f'<a href="../topics/{g["need"]}.html">More on this topic</a> · ' if any(t[0] == g["need"] for t in topics) else '') + f'<a href="../index.html#companion">Talk it through with the AI companion</a> · <a href="../glossary.html">Glossary</a></p>')
    shell(f"{g['label']}: three next steps | {NAME}", f"{g['label']}. Three small next steps and links to selected public autism resources, in plain language."[:300],
          f"start/{g['id']}.html", body, crumbs([("Home", ""), ("Start here", "start/index.html"), (g["label"], f"start/{g['id']}.html")]), 1)
    add(f"start/{g['id']}.html", "0.7")
cards = "".join(f'<li class="item"><h3><a href="{g["id"]}.html">{e(g["label"])}</a></h3><p>{e(g["acts"][0])}</p></li>' for g in CONTENT["goals"])
shell(f"Where to start with autism | {NAME}", "Tell us what you are trying to do and get three small next steps, plus links to selected public autism resources.",
      "start/index.html", f'<section class="heroplain"><h1>Where would you like to start?</h1><p class="lede">Choose what is closest to your situation. These are general ideas, not medical advice.</p></section><ul id="list" style="margin-top:24px">{cards}</ul>',
      crumbs([("Home", ""), ("Start here", "start/index.html")]), 1)
add("start/index.html", "0.8")

# ---------------------------------------------------------------- regions
for code, label in REG.items():
    if code == "global":
        continue
    spec = [r for r in DATA if code in regions_of(r)]
    if not spec:
        continue
    glob = [r for r in DATA if "global" in regions_of(r) and r not in spec]
    body = (f'<section class="heroplain"><h1>Autism resources for {e(label)}</h1><p class="lede">Resources for people in {e(label)}, plus resources that apply anywhere.</p></section>'
            f'<h2 style="margin-top:28px">Specific to {e(label)}</h2>{resource_list(spec)}'
            + (f'<h2 style="margin-top:28px">Useful anywhere</h2>{resource_list(glob)}' if glob else "") +
            '<p style="margin-top:24px">Services and rules differ by place, so check what applies where you live.</p>')
    shell(f"Autism resources for {label} | {NAME}", f"Links to selected public autism resources for {label}, collected from health agencies, universities and nonprofits.",
          f"regions/{code}.html", body, crumbs([("Home", ""), (label, f"regions/{code}.html")]), 1)
    add(f"regions/{code}.html", "0.6")

# ---------------------------------------------------------------- communities
COUNTS = {fx: len([r for r in DATA if fx in r.get("focus", [])]) for fx in FOCUS}
for fx, label in FOCUS.items():
    rs = [r for r in DATA if fx in r.get("focus", [])]
    if rs:
        listing = f'<h2 style="margin-top:28px">{len(rs)} {"resource" if len(rs) == 1 else "resources"}</h2>{resource_list(rs)}'
    else:
        listing = ('<section class="card" style="margin-top:20px"><h2>No resources yet</h2><p>We have not tagged any sources for this community yet, and we are adding them. '
                   'You can <a href="../index.html">search all resources</a> or tell us about a source at ' + f'<a href="mailto:{e(EMAIL)}">{e(EMAIL)}</a>.</p></section>')
    body = (f'<section class="heroplain"><p><a href="index.html">All communities</a></p><h1>Autism resources for {e(label)}</h1>'
            f'<p class="lede">Links to organizations and information made by or for {e(label.lower())}, from selected public sources.</p></section>{listing}'
            '<p style="margin-top:24px">The project team assigns community tags by hand, based on who runs or serves each source. They have not yet been reviewed by community advisors. '
            'Spectrum Hub does not independently verify or endorse these sources, and they are not clinically validated or medical advice.</p>')
    shell(f"Autism resources for {label} | {NAME}", f"Links to autism resources made by or for {label.lower()}, from selected public sources.", f"community/{fx}.html", body,
          crumbs([("Home", ""), ("Communities", "community/index.html"), (label, f"community/{fx}.html")]), 1, noindex=not rs)
    if rs:
        add(f"community/{fx}.html", "0.6")
rows_ = "".join(f'<li class="item"><h3><a href="{fx}.html">{e(lb)}</a></h3><p class="meta">{COUNTS[fx]} {"resource" if COUNTS[fx] == 1 else "resources"} tagged so far</p></li>' for fx, lb in FOCUS.items())
comm_body = (f'<section class="heroplain"><h1>Resources by community</h1><p class="lede">Find links to autism resources made by or for specific communities.</p></section>'
    '<section class="card" style="margin-top:20px"><h2>How this works</h2>'
    '<p>A community focus tag marks a source that is made by, or serves, a specific community. The project team assigns these tags by hand, based on who runs or serves each source. '
    'They are new and still being added, and they have not yet been reviewed by community advisors, so please treat the list as a starting point and not a complete directory.</p>'
    '<p>Spectrum Hub collects and sorts links from selected public sources. It does not independently verify, review or endorse them, and they are not clinically validated.</p>'
    '<h2>Places we are adding sources for</h2><p>Ghana and South Africa are available as place filters on the <a href="../index.html">main search</a>. Where no source is specific to a place yet, the search says so and shows resources that apply anywhere.</p>'
    '<h2>Finding resources and talking with people</h2><p>Finding community-focused resources is available now. A moderated peer community, where people talk with each other, is a future possibility and is not available. '
    'Ari, the AI companion, is a computer program and not a community of people.</p></section>'
    f'<h2 style="margin-top:28px">Communities</h2><ul id="list">{rows_}</ul>')
shell(f"Autism resources by community | {NAME}", "Find links to autism resources made by or for specific communities, from selected public sources.", "community/index.html", comm_body,
      crumbs([("Home", ""), ("Communities", "community/index.html")]), 1)
add("community/index.html", "0.7")

# ---------------------------------------------------------------- glossary
gl = "".join(f"<dt>{e(t)}</dt><dd>{e(d)}</dd>" for t, d in CONTENT["glossary"])
ld = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "Plain-language autism glossary",
      "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t, "description": d} for t, d in CONTENT["glossary"]]}
shell(f"Plain-language autism glossary | {NAME}", "Plain-language definitions of words you may meet when reading about autism, such as masking, meltdown, stimming, co-occurring conditions and school support plans.",
      "glossary.html", '<section class="heroplain"><h1>Plain-language glossary</h1><p class="lede">Words you may meet when reading about autism. Terms and systems differ between countries, so check what applies where you live.</p></section>'
      f'<dl class="card" id="gl" style="margin-top:20px">{gl}</dl>', ld, 0)
add("glossary.html", "0.7")

# ---------------------------------------------------------------- about

team_items = "".join(f'<li><h3>{e(t["name"])}</h3><p class="aff">{e(t["affiliation"])}</p><p>{e(t["blurb"])}</p></li>' for t in TEAM)
team_block = (f'<h2>The research team</h2><p>{e(NAME)} is based on the 2024 study by this team. Affiliations and roles are as listed in the article and may have changed since. '
              f'Questions about this site can go to the contact address below.</p><ul class="team">{team_items}</ul>') if TEAM else ""
about = f"""<section class="heroplain"><h1>About {e(NAME)}</h1>
<p class="lede">{e(NAME)} collects and sorts links from selected public autism sources into one calm, searchable place, for autistic people, caregivers and professionals.</p></section>
<section class="card" style="margin-top:20px">
<h2>Why it exists</h2>
<p>A 2024 study of autism discussions on Reddit (Larnyo, Nutakor, Addai-Dansoh and Nkrumah, <em>Frontiers in Psychiatry</em> 15:1441349) found that people want reliable health information, support for diagnosis and caregiving, and a community that helps them feel understood. It recommended accessible digital platforms that bring this together. This site is a prototype of that idea. <a href="https://doi.org/10.3389/fpsyt.2024.1441349" target="_blank" rel="noopener noreferrer">Read the article<span class="vh"> (opens in a new tab)</span></a>.</p>
{team_block}
<h2>How the list is made</h2>
<p>A program called SpectrumHubBot visits a short list of public pages from government health agencies, universities and nonprofits. It reads each page’s title and summary, sorts it into topics, removes duplicates and records the date it was checked. A person chooses which sources it may visit, and the project team sorts and tags them. Labels such as “Government” or “Nonprofit” say who runs a source. They are not a guarantee that the information is accurate or right for you.</p>
<h2>Finding resources and talking with people</h2>
<p>Finding resources, including by region and community focus, is available now. A moderated peer community, where people talk with each other, is a future possibility and is not available. Ari, the AI companion, is a computer program and not a community of people.</p>
<h2>What it is not</h2>
<p>It does not give medical advice, diagnose anyone or replace a health professional. It does not independently verify, review or endorse the sites it links to, and their content is not clinically validated. The AI companion, Ari, is a computer program, not a person, therapist or doctor.</p>
<h2>Get in touch</h2>
<p>Questions, corrections, suggestions for sources, or a request to stop SpectrumHubBot visiting your site: <a href="mailto:{e(EMAIL)}">{e(EMAIL)}</a>. Autistic people and caregivers who can tell us what would make this easier to use are especially welcome.</p>
</section>"""
shell(f"About and contact | {NAME}", f"What {NAME} is, why it exists, how the list of autism resources is made, and how to contact the project.", "about.html", about, None, 0)
add("about.html", "0.5")

# ---------------------------------------------------------------- privacy
a = CFG.get("analytics", {})
prov = {"goatcounter": "GoatCounter", "cloudflare": "Cloudflare Web Analytics"}.get(a.get("provider", ""), "")
if prov and a.get("code"):
    count_block = (f"<h2>Counting visits</h2><p>This site counts visits with {prov}, a tool that does not use cookies and does not follow people across websites. "
                   "We can see totals such as how many times each page was opened, which countries visits come from, which websites sent them, and similar basic details such as browser type and screen size. "
                   "Because topic, starting-point and region pages have their own addresses, we can see roughly how often each is opened. We do not record what you choose or type in the resource finder or the Companion, and we do not try to identify anyone.</p>")
    top_line = "It has no accounts and no advertising, it does not use cookies, and it does not sell data. The only visit counting is described under “Counting visits.”"
else:
    count_block = ""
    top_line = "It has no accounts and no advertising, and it does not add analytics or tracking tools. It does not sell data."
priv = f"""<section class="heroplain"><h1>Privacy and safety</h1>
<p class="lede">Last updated {e(CFG["privacy_updated"])}. Short version: no accounts, nothing saved about you unless you choose it.</p></section>
<section class="card" style="margin-top:20px">
<h2>If you need urgent help</h2>
<p>This site is not an emergency service. In the US, call or text 988 (Suicide &amp; Crisis Lifeline), or call 911. Elsewhere, contact your local emergency number.</p>
<h2>What this site does not do</h2>
<p>{top_line}</p>
{count_block}
<h2>What is stored on your device</h2>
<p>Nothing, unless you turn on “Remember my preferences” in the Companion page. Then only your preferences are kept in your browser, such as text size, colors and your preferred name. Conversations are never saved. You can see each item, forget one, forget all, or turn Memory off at any time.</p>
<h2>Other companies involved</h2>
<ul>
<li><b>Hosting.</b> The page is served by GitHub Pages, which may log visitors’ addresses under GitHub’s own privacy statement.</li>
<li><b>Fonts.</b> The page loads its fonts from Google Fonts, so Google receives your address when the page loads.</li>
<li><b>Linked sites.</b> Resources open on other websites that have their own privacy practices.</li>
</ul>
<h2>The AI companion (Ari)</h2>
<p>When you send a message to Ari, the text is sent to a server run for this project and then to Claude, an AI model from Anthropic, to write a reply. This page does not store your messages, and the project’s server is set up not to log them. Anthropic processes them under its own privacy policy. Please do not share anything you would not want an AI service to process, such as full names, addresses or medical record details. If you use voice input, your browser’s speech service may send your audio to its provider. Messages that mention self-harm, abuse or immediate danger get a fixed safety message and are not sent to the AI.</p>
<p>The companion is meant for adults. If you are under 18, please do not use it without a trusted adult. It can make mistakes, so check anything important with a qualified professional.</p>
<h2>The crawler</h2>
<p>SpectrumHubBot reads only public pages, follows each site’s robots.txt rules, waits between requests, does not visit forums or social media, and collects no personal data. Site owners can ask us to stop at the email below.</p>
<h2>Contact</h2>
<p><a href="mailto:{e(EMAIL)}">{e(EMAIL)}</a></p>
</section>"""
shell(f"Privacy and safety | {NAME}", f"How {NAME} handles your information, what is stored on your device, how the AI companion works, and where to find urgent help.", "privacy.html", priv, None, 0)
add("privacy.html", "0.4")

# ---------------------------------------------------------------- 404
shell(f"Page not found | {NAME}", "This page could not be found.", "404.html",
      '<section class="heroplain"><h1>We could not find that page</h1><p class="lede">It may have moved. You can <a href="index.html">search all resources</a>, <a href="topics/index.html">browse topics</a> or <a href="start/index.html">choose where to start</a>.</p></section>')

# ---------------------------------------------------------------- site map page (for people)
def group(prefix, title):
    items = [(p, TITLES[p]) for p in sorted(TITLES) if p.startswith(prefix) and p != prefix + "index.html"]
    head = f'<li><a href="{prefix}index.html">{e(title)}</a></li>' if (prefix + "index.html") in TITLES else ""
    return f'<section class="card" style="margin-top:16px"><h2>{e(title)}</h2><ul>{head}' + "".join(f'<li><a href="{p}">{e(t)}</a></li>' for p, t in items) + "</ul></section>"
main_links = '<section class="card" style="margin-top:16px"><h2>Main pages</h2><ul><li><a href="index.html">Search all resources</a></li><li><a href="index.html#companion">Talk it through with Ari</a></li><li><a href="glossary.html">Plain-language glossary</a></li><li><a href="about.html">About and contact</a></li><li><a href="privacy.html">Privacy and safety</a></li></ul></section>'
sm_body = ('<section class="heroplain"><h1>Site map</h1><p class="lede">Every page on the site, in one place.</p></section>' + main_links
           + group("topics/", "Topics") + group("start/", "Where to start") + group("community/", "Communities") + group("regions/", "Places")
           + '<p style="margin-top:20px">Search engines can read the <a href="sitemap.xml">XML site map</a>.</p>')
shell(f"Site map | {NAME}", "A list of every page on the site.", "sitemap.html", sm_body)
add("sitemap.html", "0.3")

# ---------------------------------------------------------------- index.html: SEO tags, analytics, noscript, footer
def block(text, name, content, anchor, before=False):
    pat = re.compile(rf"<!--{name}-start-->.*?<!--{name}-end-->", re.S)
    new = f"<!--{name}-start-->{content}<!--{name}-end-->"
    if pat.search(text):
        return pat.sub(lambda m: new, text, count=1)
    i = text.index(anchor)
    j = i if before else i + len(anchor)
    return text[:j] + new + text[j:]


home_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE + "/", "description": HOME_DESC, "inLanguage": "en"}
src = block(src, "seo", seo_head(f"{NAME}: autism resources in one place", HOME_DESC, "", home_ld), "</title>")
src = block(src, "analytics", analytics_tag(), "</head>", before=True)
nos = ('<noscript><section class="card"><h2>Browse without JavaScript</h2><p>The search and companion need JavaScript. You can still browse by topic, <a href="community/index.html">by community</a> or on the <a href="sitemap.html">site map</a>:</p><ul>'
       + "".join(f'<li><a href="topics/{i}.html">{e(l)}</a></li>' for i, l, rs in topics) + '</ul><p><a href="start/index.html">Where to start</a> · <a href="glossary.html">Glossary</a></p></section></noscript>')
src = block(src, "noscript", nos, '<main class="wrap" id="main">')
links = ('<nav aria-label="About" style="margin-bottom:8px"><a href="about.html">About and contact</a> · <a href="privacy.html">Privacy and safety</a> · '
         '<a href="glossary.html">Glossary</a> · <a href="topics/index.html">Topics</a> · <a href="start/index.html">Start here</a> · '
         '<a href="community/index.html">Communities</a> · <a href="sitemap.html">Site map</a></nav>')
if "<!--footerlinks-start-->" in src:
    src = block(src, "footerlinks", links, "")
else:
    src = re.sub(r'<nav aria-label="About" style="margin-bottom:8px">.*?</nav>', lambda m: "<!--footerlinks-start-->" + links + "<!--footerlinks-end-->", src, count=1, flags=re.S)
# keep the in-page goals and glossary in sync with content.json
src = re.sub(r"var GOALS=\[.*?\n\];", lambda m: "var GOALS=" + json.dumps(CONTENT["goals"], ensure_ascii=False, indent=0) + ";", src, count=1, flags=re.S)
src = re.sub(r"var GL=\[.*?\n\];", lambda m: "var GL=" + json.dumps(CONTENT["glossary"], ensure_ascii=False, indent=0) + ";", src, count=1, flags=re.S)
(ROOT / "index.html").write_text(src, encoding="utf-8")
add("", "1.0")

# ---------------------------------------------------------------- sitemap and robots
urls = "".join(f"<url><loc>{e(SITE + '/' + p)}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>" for p, pr in sorted(pages, key=lambda x: x[0]))
(ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8")
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
print(f"Built {len(pages)} pages, sitemap.xml and robots.txt for {SITE}")
