"""Renders data/manual/<id>.json as docs/review/<id>.md: one line per fact with a link to the source page and the quote.

python -m psi_fire.interface.review_sheet [INVESTIGATION_ID ...]
Generated output, never edited by hand: to approve, set review_status/reviewed_by/reviewed_on in the JSON.
"""

import re
import sys
from pathlib import Path
from urllib.parse import quote

from psi_fire.domain.manual import Claim, Evidence, ManualMetadata

REPO_ROOT = Path(__file__).resolve().parents[3]
MANUAL_DIR = REPO_ROOT / "data" / "manual"
REVIEW_DIR = REPO_ROOT / "docs" / "review"
_PAGE = re.compile(r"^p\.\s*(\d+)$")


def _link(evidence: Evidence) -> str:
    target = "../../" + quote(evidence.source_file)
    if match := _PAGE.match(evidence.locator.strip()):
        target += f"#page={match[1]}"  # opens the PDF on the cited page
    return f"[{evidence.source_file.rsplit('/', 1)[-1]} · {evidence.locator}]({target})"


def _fact(label: str, claim: Claim) -> list[str]:  # type: ignore[type-arg]
    value = claim.model_dump(mode="json", exclude_none=True).get("value")  # plain JSON types: no enum reprs
    lines = [f"- [ ] **{label}**: `{value}` · _{claim.status.value}_"]
    if claim.note:
        lines.append(f"  - note: {claim.note}")
    lines += [f"  - {_link(e)}: `{e.quote}`" for e in claim.evidence]  # code span: copy-paste into Ctrl+F
    return lines


def render(manual: ManualMetadata) -> str:
    instructions = (
        f"Edit `data/manual/{manual.investigation_id}.json` to approve: set `review_status` to `reviewed`, "
        "`reviewed_by` and `reviewed_on`. Check each box after comparing the quote with the linked page."
    )
    out = [f"# {manual.investigation_id}: review sheet ({manual.review_status.value})", "", instructions, ""]
    out += _fact("Pillars", manual.pillars) + _fact("Gravity regime", manual.gravity_regime)
    out += _fact("Hardware", manual.hardware)
    if manual.nominal_atmosphere:
        out += _fact("Nominal atmosphere", manual.nominal_atmosphere)
    for sensor in manual.sensors:
        out += _fact("Sensor", sensor)
    for application in manual.earth_applications:
        out += _fact("Earth application", application)
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    paths = [MANUAL_DIR / f"{i}.json" for i in argv] if argv else sorted(MANUAL_DIR.glob("*.json"))
    for path in paths:
        manual = ManualMetadata.model_validate_json(path.read_text(encoding="utf-8"))
        (REVIEW_DIR / f"{manual.investigation_id}.md").write_text(render(manual), encoding="utf-8")
        print(f"docs/review/{manual.investigation_id}.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
