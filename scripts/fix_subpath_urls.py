#!/usr/bin/env python3
"""
Post-build URL fixup for Hugo sub-path deployment.

When content is at content/learn/ and baseURL is /learn/, Hugo's relURL
behavior is inconsistent for markdown links. This script normalizes all
internal hrefs to use /learn/ prefix.

Run after: hugo --gc --minify

Usage:
  python3 scripts/fix_subpath_urls.py public/
"""
import os
import re
import sys

BASE_PREFIX = "/learn/"

# Patterns that should keep their original form (external, anchors, etc.)
EXTERNAL_PROTOCOLS = ("http://", "https://", "mailto:", "tel:", "javascript:", "#", "data:")

# Internal sections that should be prefixed with /learn/
INTERNAL_SECTIONS = [
    "concepts/", "lessons/", "culture/", "posts/",
    "russian/", "japanese/", "chinese/", "ko/",
    "about/",
]


def should_skip_href(href):
    """Skip URLs that should not be modified."""
    return any(href.startswith(p) for p in EXTERNAL_PROTOCOLS)


def needs_prefix(href):
    """Check if href is a section URL that needs /learn/ prefix."""
    # Fix doubled /learn/learn/ (artifact of baseURL + page URL combination)
    if href.startswith("/learn/learn/"):
        return "fix-double"
    if href.startswith(BASE_PREFIX):
        return False
    # Match both /section/ and section/ (no leading slash)
    for section in INTERNAL_SECTIONS:
        if href == "/" + section or href.startswith("/" + section):
            return True
        if href == section or href.startswith(section):
            return True
    return False


def add_prefix(href):
    """Add /learn/ prefix to a section URL."""
    # If it's /learn/learn/, just remove one
    if href.startswith("/learn/learn/"):
        return "/learn/" + href[len("/learn/learn/"):]
    # Add /learn/ prefix
    if href.startswith("/"):
        return BASE_PREFIX + href.lstrip("/")
    # No leading slash - add /learn/ prefix
    return BASE_PREFIX + href


def fix_html_urls(html_path):
    """Fix href URLs in an HTML file."""
    with open(html_path) as f:
        html = f.read()
    original = html

    # Pattern 1: href="..." (double or single quoted)
    def fix_quoted(match):
        attr = match.group(1)
        quote = match.group(2)
        href = match.group(3)
        if should_skip_href(href):
            return match.group(0)
        if needs_prefix(href):
            return f'{attr}{quote}{add_prefix(href)}{quote}'
        return match.group(0)

    new_html = re.sub(r'(href=)(["\'])([^"\']+)\2', fix_quoted, html)

    # Pattern 2: href=... (unquoted - Hugo's minified output)
    def fix_unquoted(match):
        attr = match.group(1)
        href = match.group(2)
        if should_skip_href(href):
            return match.group(0)
        if needs_prefix(href):
            return f'{attr}{add_prefix(href)}'
        return match.group(0)

    new_html = re.sub(r'(href=)([^\s"\'>]+)', fix_unquoted, new_html)

    # Fix canonical hrefs that got doubled (/learn/learn/)
    new_html = re.sub(
        r'href=(["\'])https://seoca1\.github\.io/learn/learn/',
        r'href=\1https://seoca1.github.io/learn/',
        new_html
    )
    # Also fix unquoted canonical hrefs
    new_html = re.sub(
        r'href=(https://seoca1\.github\.io/learn/)learn/',
        r'href=\1',
        new_html
    )
    # Fix og:url and similar
    new_html = re.sub(
        r'property=(["\'])og:url(["\']) content=(["\'])https://seoca1\.github\.io/learn/learn/',
        r'property=\1og:url\2 content=\3https://seoca1.github.io/learn/',
        new_html
    )
    new_html = re.sub(
        r'property=og:url content=(["\'])https://seoca1\.github\.io/learn/learn/',
        r'property=og:url content=\1https://seoca1.github.io/learn/',
        new_html
    )
    # Fix redirect page titles and meta refresh URLs (page/1/ pagination)
    new_html = re.sub(
        r'<title>(https://seoca1\.github\.io/learn/learn/[^<]+)</title>',
        lambda m: f'<title>{m.group(1).replace("/learn/learn/", "/learn/")}</title>',
        new_html
    )
    # Specifically handle the trailing /learn/learn/ (page/1/ → /learn/)
    new_html = re.sub(
        r'<title>(https://seoca1\.github\.io/learn)/learn/</title>',
        r'<title>\1/</title>',
        new_html
    )
    new_html = re.sub(
        r'content="0; url=https://seoca1\.github\.io/learn/learn/',
        r'content="0; url=https://seoca1.github.io/learn/',
        new_html
    )

    if new_html != original:
        with open(html_path, 'w') as f:
            f.write(new_html)
        return True
    return False


def fix_xml_urls(xml_path):
    """Fix URLs in XML files (RSS, sitemap)."""
    with open(xml_path) as f:
        xml = f.read()
    original = xml

    # Fix /learn/learn/ → /learn/
    new_xml = xml.replace("/learn/learn/", "/learn/")

    if new_xml != original:
        with open(xml_path, 'w') as f:
            f.write(new_xml)
        return True
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/fix_subpath_urls.py public/")
        sys.exit(1)

    public_dir = sys.argv[1]
    if not os.path.isdir(public_dir):
        print(f"Error: {public_dir} not a directory")
        sys.exit(1)

    fixed = 0
    total = 0
    for root, dirs, files in os.walk(public_dir):
        for fn in files:
            if not (fn.endswith('.html') or fn.endswith('.xml')):
                continue
            total += 1
            fp = os.path.join(root, fn)
            if fn.endswith('.html'):
                if fix_html_urls(fp):
                    fixed += 1
            elif fn.endswith('.xml'):
                if fix_xml_urls(fp):
                    fixed += 1

    print(f"Processed {total} files, fixed {fixed}")


if __name__ == "__main__":
    main()
