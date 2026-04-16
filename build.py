import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

# ---- config ----
POSTS_DIR   = Path("posts")
OUTPUT_DIR  = Path("output")
STATIC_DIR  = Path("static")
SITE_TITLE  = "Everett Dutton's Blog"
SITE_URL    = "https://www.everettdutton.com"
# ----------------

def parse_post(filepath):
    raw = filepath.read_text(encoding="utf-8")
    header, _, body = raw.partition("---")
    meta = {}
    for line in header.strip().splitlines():
        key, _, val = line.partition(":")
        meta[key.strip()] = val.strip()
    return {
        "title":  meta.get("title", filepath.stem),
        "date":   meta.get("date", ""),
        "draft":  meta.get("draft", "false").lower() == "true",
        "body":   body.strip(),
        "slug":   filepath.stem,
    }

def render_post(post, template):
    date_fmt = ""
    if post["date"]:
        date_fmt = datetime.strptime(post["date"], "%Y-%m-%d").strftime("%B %d, %Y")
    paragraphs = "".join(
        f"<p>{p.strip()}</p>\n"
        for p in post["body"].split("\n\n") if p.strip()
    )
    return (template
        .replace("{{SITE_TITLE}}", SITE_TITLE)
        .replace("{{TITLE}}", post["title"])
        .replace("{{DATE}}", date_fmt)
        .replace("{{BODY}}", paragraphs))

def render_index(posts, template):
    items = "".join(
        f'<li><a href="{p["slug"]}.html">{p["title"]}</a>'
        f'<span>{p["date"]}</span></li>\n'
        for p in posts
    )
    return (template
        .replace("{{SITE_TITLE}}", SITE_TITLE)
        .replace("{{POST_LIST}}", items))

def render_rss(posts):
    def rss_date(date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

    items = ""
    for post in posts:
        url = f"{SITE_URL}/{post['slug']}.html"
        paragraphs = "".join(
            f"<p>{p.strip()}</p>"
            for p in post["body"].split("\n\n") if p.strip()
        )
        pub_date = rss_date(post["date"]) if post["date"] else ""
        items += f"""
  <item>
    <title>{post['title']}</title>
    <link>{url}</link>
    <guid>{url}</guid>
    <pubDate>{pub_date}</pubDate>
    <description><![CDATA[{paragraphs}]]></description>
  </item>"""

    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{SITE_TITLE}</title>
    <link>{SITE_URL}</link>
    <description>{SITE_TITLE}</description>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="{SITE_URL}/feed.xml"
               rel="self" type="application/rss+xml"
               xmlns:atom="http://www.w3.org/2005/Atom"/>
{items}
  </channel>
</rss>"""

def build():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()

    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, OUTPUT_DIR / "static")

    post_template  = Path("templates/post.html").read_text()
    index_template = Path("templates/index.html").read_text()

    all_posts = [parse_post(f) for f in POSTS_DIR.glob("*.txt")]

    drafts = [p for p in all_posts if p["draft"]]
    posts  = sorted(
        [p for p in all_posts if not p["draft"]],
        key=lambda p: p["date"],
        reverse=True
    )

    for post in posts:
        html = render_post(post, post_template)
        (OUTPUT_DIR / f"{post['slug']}.html").write_text(html, encoding="utf-8")
        print(f"  built:   {post['slug']}.html")

    for post in drafts:
        print(f"  skipped: {post['slug']}.txt (draft)")

    index_html = render_index(posts, index_template)
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print(f"  built:   index.html")

    rss_xml = render_rss(posts)
    (OUTPUT_DIR / "feed.xml").write_text(rss_xml, encoding="utf-8")
    print(f"  built:   feed.xml")

    print(f"\nDone. {len(posts)} posts, {len(drafts)} drafts skipped.")

if __name__ == "__main__":
    build()