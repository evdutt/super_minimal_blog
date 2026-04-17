# Super Minimal Blog

A static site generator in a single Python file. Zero dependencies — just the stdlib. Write posts as plain `.txt` files and deploy to GitHub Pages.

## What it generates

- Individual post pages (`posts/<slug>.html`)
- Index page listing all posts by date
- RSS feed (`feed.xml`)
- Sitemap (`sitemap.xml`)
- `robots.txt`

## Setup

1. Fork or clone this repo.

2. Edit the config block at the top of `build.py`:
   ```python
   SITE_TITLE = "Your Blog Name"
   SITE_URL = "https://yourdomain.com"
   ```

3. For a custom domain, edit `CNAME` with your domain and configure DNS to point to GitHub Pages.

4. Push to `main`. The GitHub Actions workflow builds the site and deploys it to GitHub Pages automatically.

## Writing posts

Create `.txt` files in `posts/`. The filename becomes the URL slug.

```
title: My Post Title
date: 2026-04-17
draft: false
---
First paragraph here.

Second paragraph here. Blank lines separate paragraphs.
```

- `title` and `date` (YYYY-MM-DD) are required.
- `draft: true` excludes a post from the build.
- No Markdown — body is plain text. Each blank-line-separated block becomes a `<p>` tag.

## Building locally

```
python build.py
```

Output goes to `output/`. Open `output/index.html` in a browser to preview.

## Deployment

On every push to `main`, GitHub Actions runs `python build.py` and deploys the `output/` directory to GitHub Pages via the official `actions/deploy-pages` action.
