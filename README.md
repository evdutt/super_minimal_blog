# Super Minimal Blog

Liked my blog and want to copy it? Go ahead! There are no dependencies. It's a custom Python builder that runs on GitHub actions, and can be hosted for free on GitHub pages. You'll just need a domain name (actually you don't even *need* that).

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

## Deployment

On every push to `main`, GitHub Actions runs `python build.py` and deploys the `output/` directory to GitHub Pages via the official `actions/deploy-pages` action.
