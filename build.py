import re, sys

src = open("page.html", "r", encoding="utf-8").read()

head_marker = "<!--HEAD-->"
body_marker = "<!--BODY-->"
i_head = src.index(head_marker) + len(head_marker)
i_body = src.index(body_marker)
i_body_end = i_body + len(body_marker)

head_part = src[i_head:i_body].strip("\n")
body_part = src[i_body_end:].strip("\n")

assert head_part.count("@@SIGNUPS_JSON@@") == 0
# The bare tokens also appear as JS string-literal references inside the
# app logic further down the page (e.g. `.replace("@@SIGNUPS_JSON@@", ...)`),
# so more than one raw occurrence is expected. What must be unique is the
# actual tag-wrapped data SLOT that .replace(token, value, 1) will resolve
# (first-occurrence-only, and these slots come before the logic script in
# document order, so they are always the first match).
DATA_SLOT = '<script id="signups-data" type="application/json">@@SIGNUPS_JSON@@</script>'
TEMPLATE_SLOT = '<script id="page-template" type="text/plain">@@TEMPLATE_TEXT@@</script>'
assert body_part.count(DATA_SLOT) == 1, "expected exactly one signups-data slot"
assert body_part.count(TEMPLATE_SLOT) == 1, "expected exactly one page-template slot"

# What goes to the Artifact TOOL (it wraps doctype/html/head/body itself) --
# just title/style + body content, tokens left unresolved for now.
inner_content = head_part + "\n" + body_part

# The full, self-contained document used as the *runtime* capability-publish
# template (this is what claude.use("artifact").publish(html) sends -- it
# must be a complete document, unlike the file handed to the Artifact tool).
full_doc_template = (
    "<!doctype html>\n"
    '<html lang="en">\n'
    "<head>\n"
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    + head_part
    + "\n</head>\n<body>\n"
    + body_part
    + "\n</body>\n</html>\n"
)

# Escape real "</script" sequences (case-insensitive) so this whole document
# can be embedded as the text content of a <script type="text/plain"> tag.
def escape_script_close(text):
    return re.sub(r"</script", "<\\/script", text, flags=re.IGNORECASE)

escaped_skeleton = escape_script_close(full_doc_template)

# Resolve the INITIAL published version: data -> [], template slot -> the
# escaped (still token-bearing) skeleton, so the very first visitor's
# self-publish already has a working template to build from.
resolved = full_doc_template.replace("@@SIGNUPS_JSON@@", "[]", 1)
resolved = resolved.replace("@@TEMPLATE_TEXT@@", escaped_skeleton, 1)

# Sanity: the live #signups-data script should now hold exactly "[]", and
# the #page-template script should still contain the embedded (escaped) copy
# of the original DATA_SLOT / TEMPLATE_SLOT markers, unresolved.
assert '<script id="signups-data" type="application/json">[]</script>' in resolved
escaped_data_slot = escape_script_close(DATA_SLOT)
escaped_template_slot = escape_script_close(TEMPLATE_SLOT)
assert escaped_data_slot in resolved, "template copy missing embedded data slot"
assert escaped_template_slot in resolved, "template copy missing embedded template slot"

# Now build the actual file to hand to the Artifact TOOL: same as `resolved`
# but WITHOUT the doctype/html/head/body wrapper (the tool adds that itself).
artifact_file = inner_content.replace("@@SIGNUPS_JSON@@", "[]", 1)
artifact_file = artifact_file.replace("@@TEMPLATE_TEXT@@", escaped_skeleton, 1)

open("artifact-file.html", "w", encoding="utf-8").write(artifact_file)
open("full-doc-preview.html", "w", encoding="utf-8").write(resolved)

print("inner_content bytes:", len(inner_content))
print("full_doc_template bytes:", len(full_doc_template))
print("escaped_skeleton bytes:", len(escaped_skeleton))
print("artifact_file bytes:", len(artifact_file))
print("OK")
