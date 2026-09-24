# NeoAccounting website

Source for the NeoAccounting marketing site.

## Live page

Published at: https://neoaccounting.app/

Deployed to AWS Amplify by `.github/workflows/deploy.yml` on every push to
`main`. The workflow runs `python3 build.py`, copies `full-doc-preview.html`
to `index.html`, zips it, and ships that zip to Amplify app `d2ifmhr1nmutri`
(eu-central-1) using an OIDC role. `index.html` is the deployed artifact and
is gitignored, so `full-doc-preview.html` is what actually goes live — not
`artifact-file.html`.

> **Note:** the "How signups are captured" and "Email backend" sections below
> predate the move to Amplify and the `Send signup form submissions to
> info@neoprop.ai via SES` commit. Treat them as historical until reviewed.

**Deploying assets:** the workflow zips `index.html` and nothing else, so any
additional static file (for example `og-image.png`, which the `og:image` meta
tag points at, or a future `robots.txt` / `sitemap.xml`) will 404 until it is
added to the `zip` line in the build step.

## Files

- `page.html` — the authored source. Has two build-time markers (`<!--HEAD-->`,
  `<!--BODY-->`) splitting head content (title/fonts/styles) from body
  content, and two placeholder tokens (`@@SIGNUPS_JSON@@`, `@@TEMPLATE_TEXT@@`)
  resolved by `build.py`. Edit this file, not the generated ones.
- `build.py` — run with `python3 build.py` (from this folder) after editing
  `page.html`. Produces `artifact-file.html` and `full-doc-preview.html`.
  Pushing to `main` is what updates the live site; see Live page above.
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

The palette matches neoprop.ai:

| Role              | Hex       |
|-------------------|-----------|
| Primary navy      | `#071A2B` |
| Primary teal      | `#16C7C8` |
| Bright cyan       | `#20D9D9` |
| White             | `#FFFFFF` |
| Light background  | `#F5F8FA` |
| Dark text         | `#102333` |
| Muted text        | `#6B7C8C` |
| Light border      | `#DCE5EA` |

Three values are derived rather than taken from that list, each for a
contrast reason:

- `--accent-text` (`#0F7F80`) — the brand teal measures 2.1:1 as text on
  white, so it is used only as a fill. This is the same hue darkened to
  4.5:1 for type, 1px borders and focus rings.
- `--accent-on-tint` (`#0D7576`) — the numbered chips tint their own
  background with teal, which costs enough contrast that `--accent-text`
  drops to 4.28:1. Darker again so chip labels clear AA at 12.5px.
- `--muted` (`#5D6E7E`) — brand muted is 4.3:1 on the light background and
  is used at 0.78–0.82rem. Darkened to 5.0:1.

Primary buttons use navy text on teal (8.4:1), never white (2.1:1).

The palette is applied through the token blocks at the top of `page.html`
(light, `prefers-color-scheme: dark`, and explicit `[data-theme="dark"]`),
plus a "Brand expression layer" at the end of the stylesheet that gives the
header, hero and footer a navy field where the vivid teal is legible at full
strength. Every text pair passes WCAG AA in both themes.

## Verification

Run from this folder after editing `page.html`:

- `python3 build.py` — regenerates `artifact-file.html` and
  `full-doc-preview.html`.
- `node quine-test.js` — checks the self-publish logic round-trips across
  three generations, including adversarial `</script>` input.
- `node browser-check.js` — parses the published page in a real browser.
  Needs Playwright + Chromium. A blocked Google Fonts request is expected
  offline and is not a failure.

`build.py` resets the embedded signup store to `[]`. Once real signups have
accumulated on the live page, reconcile them before republishing from a
fresh build or they will be overwritten.
