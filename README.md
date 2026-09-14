# NeoAccounting website

Source for the NeoAccounting marketing site, published as a Claude Artifact (a
hosted page on claude.ai, not a self-hosted deployment).

## Live page

Published at: https://claude.ai/code/artifact/67e89fbf-1826-424f-9a2c-15bd88f0c15b

It's currently private to the owning claude.ai account. To let the public
signup form work for outside visitors, it needs to be shared with edit/
interact access from the page's share menu (view-only sharing is not enough —
see "How signups are captured" below).

## Files

- `page.html` — the authored source. Has two build-time markers (`<!--HEAD-->`,
  `<!--BODY-->`) splitting head content (title/fonts/styles) from body
  content, and two placeholder tokens (`@@SIGNUPS_JSON@@`, `@@TEMPLATE_TEXT@@`)
  resolved by `build.py`. Edit this file, not the generated ones.
- `build.py` — run with `python3 build.py` (from this folder) after editing
  `page.html`. Produces `artifact-file.html` (and a couple of local preview/
  debug files that aren't included here). Publish `artifact-file.html` via
  Claude's Artifact tool to update the live page — republishing the same
  artifact URL keeps the link and its accumulated signups.
- `artifact-file.html` — the exact file that was last published live (kept
  here as a reference/backup).
- `quine-test.js` (run with `node`) / `browser-check.js` (run with
  `node`, needs Playwright + a local Chromium — see below) — verification
  scripts used while building this, useful again after any future edit to the
  self-publish logic in `page.html`.
- `screenshots/` — desktop light, desktop dark, and mobile renders taken
  during the build for a visual record.

## How signups are captured

There's no traditional backend — this is a single static page hosted as a
Claude Artifact. Submitting the form uses Claude's `artifact` runtime
capability to durably republish the whole page with the new signup appended
to a small embedded JSON store (`<script id="signups-data" type=
"application/json">`). This is a "quine": the page also carries an escaped
copy of its own template (`<script id="page-template" type="text/plain">`)
so it can rebuild and republish itself on every submission without any
server. If that capability call fails for a visitor (e.g. no write access),
the form falls back to a `mailto:info@neoprop.ai` link.

## Email backend

A Claude scheduled task ("NeoAccounting signup emailer", trigger id
`trig_0111H98tfimsn81mU9vFFEhq`) runs hourly, reads the live page's signup
data, and emails new signups to info@neoprop.ai via a transactional email
API. It currently holds placeholder credentials (no real API key yet), so it
detects pending signups but doesn't send. To activate it, give Claude a real
email API key/endpoint/from-address to swap into that scheduled task.

## Branding note

neoprop.ai's exact brand colors/fonts couldn't be extracted automatically, so
the palette (deep teal `#1f6f63` / brass `#b8873d` on an off-white ground,
Fraunces + IBM Plex Sans/Mono) is an approximation of a clean, modern,
professional look. Share neoprop.ai's real brand values to get an exact match.
