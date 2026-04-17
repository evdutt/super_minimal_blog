import html
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote as url_quote

# ---- config ----
POSTS_DIR        = Path("posts")
OUTPUT_DIR       = Path("output")
STATIC_DIR       = Path("static")
SITE_TITLE       = "Everett Dutton's Blog"
SITE_URL         = "https://www.everettdutton.com"
SITE_DESCRIPTION = "Writing on software, business, and whatever else I find interesting."
# ----------------

def apply_template(template, vars):
    """Single-pass replacement so inserted content can't trigger further substitutions."""
    pattern = re.compile(r'\{\{(' + '|'.join(re.escape(k) for k in vars) + r')\}\}')
    result = pattern.sub(lambda m: vars[m.group(1)], template)
    for token in re.findall(r'\{\{[^}]+\}\}', result):
        print(f"  WARNING: unresolved template token {token}")
    return result

def parse_post(filepath):
    raw = filepath.read_text(encoding="utf-8")
    header, sep, body = raw.partition("---")
    if not sep:
        raise ValueError(f"{filepath}: missing '---' separator between frontmatter and body")
    meta = {}
    for line in header.strip().splitlines():
        key, _, val = line.partition(":")
        meta[key.strip()] = val.strip()
    title = meta.get("title", "").strip()
    date  = meta.get("date", "").strip()
    if not title:
        raise ValueError(f"{filepath}: missing required frontmatter field 'title'")
    if not date:
        raise ValueError(f"{filepath}: missing required frontmatter field 'date'")
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"{filepath}: 'date' must be YYYY-MM-DD, got {date!r}")
    return {
        "title":       title,
        "date":        date,
        "parsed_date": parsed_date,
        "draft":       meta.get("draft", "false").lower() == "true",
        "body":        body.strip(),
        "slug":        filepath.stem,
    }

def render_post(post, template):
    date_fmt = post["parsed_date"].strftime("%B %d, %Y")
    paragraphs = "".join(
        f"<p>{html.escape(p.strip())}</p>\n"
        for p in post["body"].split("\n\n") if p.strip()
    )
    first_para = post["body"].split("\n\n")[0].strip().replace("\n", " ")
    description = first_para[:160] + ("\u2026" if len(first_para) > 160 else "")
    return apply_template(template, {
        "SITE_TITLE":   html.escape(SITE_TITLE),
        "TITLE":        html.escape(post["title"]),
        "DATE":         html.escape(date_fmt),
        "BODY":         paragraphs,
        "DESCRIPTION":  html.escape(description),
    })

def render_index(posts, template):
    items = "".join(
        f'<li><a href="{html.escape(p["slug"])}.html">{html.escape(p["title"])}</a>'
        f'<span>{html.escape(p["date"])}</span></li>\n'
        for p in posts
    )
    return apply_template(template, {
        "SITE_TITLE":   html.escape(SITE_TITLE),
        "DESCRIPTION":  html.escape(SITE_DESCRIPTION),
        "POST_LIST":    items,
    })

def render_rss(posts):
    def rss_date(dt):
        return dt.replace(tzinfo=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    items = ""
    for post in posts:
        url = f"{SITE_URL}/{url_quote(post['slug'])}.html"
        paragraphs = "".join(
            f"<p>{html.escape(p.strip())}</p>"
            for p in post["body"].split("\n\n") if p.strip()
        )
        items += f"""
  <item>
    <title>{html.escape(post['title'])}</title>
    <link>{url}</link>
    <guid>{url}</guid>
    <pubDate>{rss_date(post['parsed_date'])}</pubDate>
    <description><![CDATA[{paragraphs}]]></description>
  </item>"""

    newest = rss_date(posts[0]["parsed_date"]) if posts else ""
    last_build = f"\n    <lastBuildDate>{newest}</lastBuildDate>" if newest else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{html.escape(SITE_TITLE)}</title>
    <link>{SITE_URL}</link>
    <description>{html.escape(SITE_DESCRIPTION)}</description>{last_build}
    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
{items}
  </channel>
</rss>"""

def render_robots():
    return f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"

def render_sitemap(posts):
    newest_date = posts[0]["date"] if posts else ""
    root_lastmod = f"<lastmod>{newest_date}</lastmod>" if newest_date else ""
    urls = f"  <url><loc>{SITE_URL}/</loc>{root_lastmod}</url>\n"
    for post in posts:
        urls += f"  <url><loc>{SITE_URL}/{url_quote(post['slug'])}.html</loc><lastmod>{post['date']}</lastmod></url>\n"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}</urlset>"""

def build():
    if not POSTS_DIR.exists():
        raise FileNotFoundError(f"Posts directory '{POSTS_DIR}' not found")
    post_template_path  = Path("templates/post.html")
    index_template_path = Path("templates/index.html")
    for p in (post_template_path, index_template_path):
        if not p.exists():
            raise FileNotFoundError(f"Template '{p}' not found")

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()

    cname_src = Path("CNAME")
    if cname_src.exists():
        shutil.copy(cname_src, OUTPUT_DIR / "CNAME")

    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, OUTPUT_DIR / "static",
                        ignore=shutil.ignore_patterns(".DS_Store"))

    post_template  = post_template_path.read_text(encoding="utf-8")
    index_template = index_template_path.read_text(encoding="utf-8")

    all_posts = []
    errors = []
    for f in POSTS_DIR.glob("*.txt"):
        try:
            all_posts.append(parse_post(f))
        except ValueError as e:
            errors.append(str(e))

    if errors:
        for err in errors:
            print(f"  ERROR: {err}")
        raise SystemExit("Build aborted due to post errors.")

    drafts = [p for p in all_posts if p["draft"]]
    posts  = sorted(
        [p for p in all_posts if not p["draft"]],
        key=lambda p: p["parsed_date"],
        reverse=True,
    )

    for post in posts:
        html_out = render_post(post, post_template)
        (OUTPUT_DIR / f"{post['slug']}.html").write_text(html_out, encoding="utf-8")
        print(f"  built:   {post['slug']}.html")

    for post in drafts:
        print(f"  skipped: {post['slug']}.txt (draft)")

    index_html = render_index(posts, index_template)
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"  built:   index.html")

    rss_xml = render_rss(posts)
    (OUTPUT_DIR / "feed.xml").write_text(rss_xml, encoding="utf-8")
    print(f"  built:   feed.xml")

    sitemap_xml = render_sitemap(posts)
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
    print(f"  built:   sitemap.xml")

    (OUTPUT_DIR / "robots.txt").write_text(render_robots(), encoding="utf-8")
    print(f"  built:   robots.txt")

    print(f"\nDone. {len(posts)} posts, {len(drafts)} drafts skipped.")

if __name__ == "__main__":
    build()
