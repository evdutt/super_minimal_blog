import html
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote as url_quote

try:
    import markdown as md
except ImportError as exc:
    raise SystemExit("Missing dependency 'markdown'. Install it with: pip install markdown") from exc

# ---- config ----
POSTS_DIR        = Path("posts")
OUTPUT_DIR       = Path("output")
STATIC_DIR       = Path("static")
SITE_TITLE       = "Everett Dutton's Blog"
SITE_URL         = "https://www.everettdutton.com"
SITE_DESCRIPTION = "Writing on society, systems, and technology."
MARKDOWN_EXTENSIONS = ["extra", "sane_lists", "smarty"]
CONSULTING_PAGE_SLUG = "consulting"
CONSULTING_PAGE_TITLE = "Dutton Solutions LLC"
CONSULTING_PAGE_DESCRIPTION = "Operations research consulting focused on agentic analytics, machine learning, simulation, and optimization."
CONSULTING_PAGE_BODY_MD = """
Dutton Solutions LLC provides operations research consulting for teams that need better, faster decisions.

I design practical agentic analytics solutions that combine methods like:

- data collection and engineering
- statistics
- machine learning
- simulation
- optimization
- LLMs

I specialize in working with clients struggling with data quality and lack of clarity around their decision problems.

If you would like to chat about a project, please connect with me on [LinkedIn](https://www.linkedin.com/in/everett-dutton).
"""
# ----------------

def apply_template(template, vars):
    """Single-pass replacement so inserted content can't trigger further substitutions."""
    pattern = re.compile(r'\{\{(' + '|'.join(re.escape(k) for k in vars) + r')\}\}')
    result = pattern.sub(lambda m: vars[m.group(1)], template)
    for token in re.findall(r'\{\{[^}]+\}\}', result):
        print(f"  WARNING: unresolved template token {token}")
    return result

def markdown_to_html(text):
    return md.markdown(text, extensions=MARKDOWN_EXTENSIONS, output_format="html5")

def markdown_to_text(text):
    rendered = markdown_to_html(text)
    rendered = re.sub(r"<pre.*?</pre>", " ", rendered, flags=re.DOTALL)
    rendered = re.sub(r"<code.*?</code>", " ", rendered, flags=re.DOTALL)
    plain = re.sub(r"<[^>]+>", " ", rendered)
    plain = html.unescape(plain)
    return re.sub(r"\s+", " ", plain).strip()

def summarize(text, limit):
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit].rstrip() + "\u2026"

def parse_frontmatter_lines(lines):
    meta = {}
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        key, sep, value = line.partition(":")
        if not sep:
            return None
        meta[key.strip().lower()] = value.strip()
    return meta

def split_frontmatter(raw):
    # YAML-style frontmatter:
    # ---
    # title: ...
    # date: ...
    # ---
    if raw.startswith("---"):
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, flags=re.DOTALL)
        if match:
            meta = parse_frontmatter_lines(match.group(1).splitlines())
            if meta is not None:
                return meta, match.group(2)

    # Backward-compatible legacy frontmatter:
    # title: ...
    # date: ...
    # ---
    # body
    header, sep, body = raw.partition("\n---\n")
    if sep:
        meta = parse_frontmatter_lines(header.splitlines())
        if meta is not None:
            return meta, body

    return {}, raw

def derive_title_and_body(raw_title, body, slug):
    title = raw_title.strip()
    trimmed_body = body.strip()
    if title:
        return title, trimmed_body

    lines = body.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("# "):
            heading_md = stripped[2:].strip()
            heading_text = markdown_to_text(heading_md)
            next_body = "\n".join(lines[i + 1:]).lstrip()
            if heading_text:
                return heading_text, next_body
        break

    fallback = slug.replace("-", " ").replace("_", " ").title()
    return fallback, trimmed_body

def parse_post(filepath):
    raw = filepath.read_text(encoding="utf-8")
    meta, body = split_frontmatter(raw)

    title, body = derive_title_and_body(meta.get("title", ""), body, filepath.stem)
    date = meta.get("date", "").strip()
    if date:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"{filepath}: 'date' must be YYYY-MM-DD, got {date!r}")
    else:
        parsed_date = datetime.fromtimestamp(filepath.stat().st_mtime)
        date = parsed_date.strftime("%Y-%m-%d")

    body_markdown = body.strip()
    body_html = markdown_to_html(body_markdown)
    body_text = markdown_to_text(body_markdown) or title

    return {
        "title":       title,
        "date":        date,
        "parsed_date": parsed_date,
        "draft":       meta.get("draft", "false").strip().lower() in {"true", "1", "yes"},
        "body":        body_markdown,
        "body_html":   body_html,
        "body_text":   body_text,
        "slug":        filepath.stem,
    }

def render_post(post, template, prev_post=None, next_post=None):
    date_fmt = post["parsed_date"].strftime("%B %d, %Y")
    date_month_year = post["parsed_date"].strftime("%B %Y")
    description = summarize(post["body_text"], 160)

    if prev_post or next_post:
        prev_part = (
            f'<a href="/{prev_post["slug"]}.html" class="prev">'
            f'<span class="label">← Previous</span>'
            f'<span class="title">{html.escape(prev_post["title"])}</span>'
            f'</a>'
            if prev_post else '<span></span>'
        )
        next_part = (
            f'<a href="/{next_post["slug"]}.html" class="next">'
            f'<span class="label">Next →</span>'
            f'<span class="title">{html.escape(next_post["title"])}</span>'
            f'</a>'
            if next_post else ''
        )
        pager = f'<div class="pager">{prev_part}{next_part}</div><div class="return-index"><a href="/">← ALL POSTS</a></div>'
    else:
        pager = '<div class="return-index"><a href="/">← ALL POSTS</a></div>'

    return apply_template(template, {
        "SITE_TITLE":      html.escape(SITE_TITLE),
        "TITLE":           html.escape(post["title"]),
        "DATE":            html.escape(date_fmt),
        "DATE_MONTH_YEAR": html.escape(date_month_year),
        "BODY":            post["body_html"],
        "DESCRIPTION":     html.escape(description),
        "PAGER":           pager,
    })

def render_index(posts, template):
    items = ""
    for p in posts:
        short_date = p["parsed_date"].strftime("%b %d, %Y")
        excerpt = summarize(p["body_text"], 200)
        items += (
            f'<li>'
            f'<div class="date">{html.escape(short_date)}</div>'
            f'<div class="main">'
            f'<div class="title-line"><a href="{html.escape(p["slug"])}.html">{html.escape(p["title"])}</a></div>'
            f'<div class="excerpt"><a href="{html.escape(p["slug"])}.html">{html.escape(excerpt)}</a></div>'
            f'</div>'
            f'</li>\n'
        )
    return apply_template(template, {
        "SITE_TITLE":   html.escape(SITE_TITLE),
        "DESCRIPTION":  html.escape(SITE_DESCRIPTION),
        "POST_COUNT":   str(len(posts)),
        "POST_LIST":    items,
    })

def render_page(title, description, body_markdown, template):
    return apply_template(template, {
        "SITE_TITLE":   html.escape(SITE_TITLE),
        "TITLE":        html.escape(title),
        "DESCRIPTION":  html.escape(description),
        "BODY":         markdown_to_html(body_markdown.strip()),
    })

def render_rss(posts):
    def rss_date(dt):
        return dt.replace(tzinfo=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    items = ""
    for post in posts:
        url = f"{SITE_URL}/{url_quote(post['slug'])}.html"
        items += f"""
  <item>
    <title>{html.escape(post['title'])}</title>
    <link>{url}</link>
    <guid>{url}</guid>
    <pubDate>{rss_date(post['parsed_date'])}</pubDate>
        <description><![CDATA[{post['body_html']}]]></description>
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

def render_sitemap(posts, extra_paths=None):
    newest_date = posts[0]["date"] if posts else ""
    default_lastmod = newest_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    root_lastmod = f"<lastmod>{newest_date}</lastmod>" if newest_date else ""
    urls = f"  <url><loc>{SITE_URL}/</loc>{root_lastmod}</url>\n"
    for post in posts:
        urls += f"  <url><loc>{SITE_URL}/{url_quote(post['slug'])}.html</loc><lastmod>{post['date']}</lastmod></url>\n"
    for path in extra_paths or []:
        urls += f"  <url><loc>{SITE_URL}/{path}</loc><lastmod>{default_lastmod}</lastmod></url>\n"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}</urlset>"""

def build():
    if not POSTS_DIR.exists():
        raise FileNotFoundError(f"Posts directory '{POSTS_DIR}' not found")
    post_template_path  = Path("templates/post.html")
    index_template_path = Path("templates/index.html")
    page_template_path = Path("templates/page.html")
    for p in (post_template_path, index_template_path, page_template_path):
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
    page_template = page_template_path.read_text(encoding="utf-8")

    all_posts = []
    errors = []
    for f in POSTS_DIR.glob("*.md"):
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

    for i, post in enumerate(posts):
        prev_post = posts[i + 1] if i + 1 < len(posts) else None  # older
        next_post = posts[i - 1] if i > 0 else None               # newer
        html_out = render_post(post, post_template, prev_post, next_post)
        (OUTPUT_DIR / f"{post['slug']}.html").write_text(html_out, encoding="utf-8")
        print(f"  built:   {post['slug']}.html")

    for post in drafts:
        print(f"  skipped: {post['slug']}.md (draft)")

    index_html = render_index(posts, index_template)
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"  built:   index.html")

    consulting_html = render_page(
        CONSULTING_PAGE_TITLE,
        CONSULTING_PAGE_DESCRIPTION,
        CONSULTING_PAGE_BODY_MD,
        page_template,
    )
    consulting_filename = f"{CONSULTING_PAGE_SLUG}.html"
    (OUTPUT_DIR / consulting_filename).write_text(consulting_html, encoding="utf-8")
    print(f"  built:   {consulting_filename}")

    rss_xml = render_rss(posts)
    (OUTPUT_DIR / "feed.xml").write_text(rss_xml, encoding="utf-8")
    print(f"  built:   feed.xml")

    sitemap_xml = render_sitemap(posts, extra_paths=[consulting_filename])
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
    print(f"  built:   sitemap.xml")

    (OUTPUT_DIR / "robots.txt").write_text(render_robots(), encoding="utf-8")
    print(f"  built:   robots.txt")

    print(f"\nDone. {len(posts)} posts, {len(drafts)} drafts skipped.")

if __name__ == "__main__":
    build()
