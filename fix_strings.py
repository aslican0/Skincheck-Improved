import re

path = "js/products.js"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    if line.strip() == "":
        continue
    match = re.match(r'^\s*("|\'|\[|\]|\{|\}|const|let|var|//|[a-zA-Z0-9_]+\s*:|category|imageUrl|ingredientNames)', line)
    if match or line.startswith("//") or line.startswith("\n"):
        fixed_lines.append(line)
    else:
        # It's a continuation line. Append to the previous line.
        if fixed_lines:
            fixed_lines[-1] = fixed_lines[-1].rstrip() + " " + line.lstrip()
        else:
            fixed_lines.append(line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(fixed_lines)
