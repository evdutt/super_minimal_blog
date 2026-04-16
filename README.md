# Super Minimal Blog

A static blog generator built with Python. Zero dependencies, just drop .txt files and deploy to GitHub Pages.

## Features

- Write posts in plain .txt files
- Draft support
- RSS feed
- 90s Windows 95 style CSS
- Free hosting on GitHub Pages
- DDoS protection via Cloudflare

## Setup

1. Clone or create this repo on GitHub.

2. Edit `build.py` to set your `SITE_TITLE` and `SITE_URL`.

3. For custom domain:
   - Edit `CNAME` with your domain.
   - Point your domain's DNS to GitHub Pages IPs.
   - Sign up for Cloudflare (free) and move your nameservers there for protection and analytics.

4. Push to GitHub. The GitHub Action will build and deploy automatically.

## Writing Posts

Create files in `posts/` with format:

```
title: My Post Title
date: 2026-04-16
draft: false  # optional, defaults to false
---
Post content here.

Paragraphs separated by blank lines.
```

## Building Locally

Run `python build.py` to generate the site in `output/`.

## Deployment

On push to `main`, GitHub Actions runs the build and deploys to `gh-pages` branch.