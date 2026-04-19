# Super Minimal Blog

A tiny static blog generator built with Python and Markdown.

This project is intentionally simple: write posts in Markdown, run one script, and publish the generated HTML from `output/`.

## Reusable Materials

You can reuse the **Reusable Materials** listed in [LICENSE](LICENSE) to kick start your own blog.

At the time of writing, that includes:

- `build.py`
- `templates/`
- `style.css` (located at `static/style.css` in this repo)

Post content is not reusable. See [LICENSE](LICENSE) for the exact terms.

## Quick Start

1. Copy the Reusable Materials into a new project.
2. Create a `posts/` folder with your own `.md` posts.
3. Create a `static/` folder and place your stylesheet/assets there.
4. Install the Markdown dependency:

   ```bash
   python -m pip install markdown
   ```

5. Build the site:

   ```bash
   python build.py
   ```

Generated files are written to `output/`.

## Post Format

Use Markdown files in `posts/`.

Optional frontmatter:

```md
---
title: My First Post
date: 2026-04-19
draft: false
---

Your post content here.
```

If `title` is missing, the first `# Heading` is used.
If `date` is missing, file modification time is used.

## Customize

- Edit site constants near the top of `build.py` (`SITE_TITLE`, `SITE_URL`, `SITE_DESCRIPTION`).
- Edit HTML in `templates/`.
- Style your blog in `static/style.css`.

## Build In This Repository

If you are working in this repository, use the local virtual environment:

```bash
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python build.py
```

## Publish to GitHub Pages

This repository already includes an automated GitHub Pages workflow at `.github/workflows/deploy.yml`.

1. In your GitHub repository, go to **Settings -> Pages**.
2. Set **Source** to **GitHub Actions**.
3. Push to `main`.

Each push to `main` runs the deploy workflow, which installs dependencies, builds the site, and publishes `output/` to GitHub Pages.

If you are starting a new repo from the Reusable Materials, copy `.github/workflows/deploy.yml` into your new repo so deployment works the same way.