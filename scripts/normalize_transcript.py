
import re

def normalize(text: str) -> str:
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        # Remove timestamps: 00:01:32, [00:01], (0:01)
        line = re.sub(r"\[?\(?\d{1,2}:\d{2}(?::\d{2})?\)?\]?", "", line).strip()
        # Remove pure-timestamp or blank lines
        if re.match(r"^[\d:,\s\-\[\]()]+$", line): continue
        # Remove [inaudible], [crosstalk] etc
        if re.match(r"^\[(?:inaudible|crosstalk|end of recording|end of transcript)\]$", line, re.I): continue
        # Collapse multiple spaces
        line = re.sub(r" {2,}", " ", line).strip()
        if line:
            lines.append(line)
    return "\n".join(lines)
