#!/usr/bin/env python3
"""Prepare the PDK 3.0.4 full stem recipe for an HD2/Linux ROMBUILD."""

from __future__ import annotations

import pathlib
import re
import sys


LINE = re.compile(
    r'^(?P<prefix>\s*(?:primary|secondary|variant|extension|device|file|data|bootbinary)'
    r'(?:\[[^]]+\])?\s*=\s*)(?P<quote>"?)(?P<source>(?:[A-Za-z]:)?[\\/][^\s"]+)'
    r'(?P=quote)(?P<suffix>.*)$',
    re.IGNORECASE,
)


def resolve_case(path: pathlib.Path) -> pathlib.Path | None:
    if path.exists():
        return path.resolve()
    parts = path.parts[1:]

    def descend(current: pathlib.Path, index: int) -> pathlib.Path | None:
        if index == len(parts):
            return current.resolve() if current.exists() else None
        part = parts[index]
        if part == "..":
            return descend(current.parent, index + 1)
        if part == ".":
            return descend(current, index + 1)
        if not current.is_dir():
            return None
        exact = current / part
        wanted = part.casefold()
        matches = [entry for entry in current.iterdir()
                   if entry.name.casefold() == wanted]
        # A Linux PDK build may contain both data/Z and data/z.  Try the exact
        # spelling first, but backtrack into its case sibling when a child is
        # present only there.
        matches.sort(key=lambda entry: entry != exact)
        for match in matches:
            found = descend(match, index + 1)
            if found is not None:
                return found
        return None

    return descend(pathlib.Path(path.anchor), 0)


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit(f"usage: {sys.argv[0]} INPUT EPOCROOT OUTPUT")
    source = pathlib.Path(sys.argv[1])
    epocroot = pathlib.Path(sys.argv[2]).resolve()
    output = pathlib.Path(sys.argv[3])
    fallbacks: list[str] = []
    omitted: list[str] = []
    skipped_patchdata: list[str] = []
    result: list[str] = []

    text = source.read_text(errors="strict").replace("\r", "")

    for raw in text.splitlines():
        if re.match(r"^romname=", raw, re.IGNORECASE):
            raw = "romname=hd2_symbian3_full_raw.img"
        elif re.match(r"^romlinearbase=", raw, re.IGNORECASE):
            raw = "romlinearbase=0x12200000"
        elif re.match(r"^demandpagingconfig\b", raw, re.IGNORECASE):
            raw = "REM HD2 first-UI baseline: demand paging disabled " + raw
        elif re.match(r"^pagingpolicy\b", raw, re.IGNORECASE):
            raw = "pagingpolicy defaultunpaged"
        elif re.match(r"^codepagingoverride\b", raw, re.IGNORECASE):
            raw = "codepagingoverride defaultunpaged"

        # The original recipe was generated on a case-insensitive Windows
        # host.  Linux ROMBUILD compares internal destination names literally
        # for alias/patchdata lookups, so use one canonical spelling.
        if re.match(r"^\s*patchdata\b", raw, re.IGNORECASE):
            # These offsets were generated for Nokia's exact 2010 release
            # binaries.  Some open components have just been rebuilt, so
            # blindly applying the stale file offsets could corrupt code.
            # None is required for the first UI milestone; retain an audit
            # list and restore individual settings only after symbol review.
            skipped_patchdata.append(raw)
            result.append("REM HD2 skipped stale PDK patchdata: " + raw)
            continue
        if re.match(r"^\s*alias\b", raw, re.IGNORECASE):
            raw = raw.lower()

        match = LINE.match(raw)
        if match is None:
            result.append(raw)
            continue
        # Only normalize the host-side source.  The suffix contains the ROM
        # destination (for example "sys\\bin\\euser.dll") and ROMBUILD 2.14
        # requires those Symbian separators to remain backslashes.
        source_name = match.group("source").replace("\\", "/")
        if re.match(r"^[A-Za-z]:/", source_name):
            # Three generated stem inputs retain their old W: checkout path
            # in the official recipe.  The PDK archive stores exact copies
            # beside the recipe.
            source_name = str(
                epocroot / "pdk304-stemkit" /
                pathlib.PurePosixPath(source_name).name
            )
        if source_name.casefold().startswith("/epoc32/"):
            source_name = f"{epocroot}/epoc32/{source_name[8:]}"
        # SBS can create both data/Z and data/z on a case-sensitive host.
        # The PDK release payload lives in the lowercase tree; selecting the
        # empty uppercase directory would make thousands of valid inputs look
        # missing and the simple case resolver cannot safely backtrack.
        data_prefix = f"{epocroot}/epoc32/data/z/"
        if source_name.casefold().startswith(data_prefix.casefold()):
            source_name = data_prefix + source_name[len(data_prefix):]
        candidate = pathlib.Path(source_name)
        actual = resolve_case(candidate)
        fallback: pathlib.Path | None = None
        if actual is None and candidate.name.casefold().endswith(".mbm_rom"):
            fallback = resolve_case(candidate.with_name(candidate.name[:-4]))
        if actual is None and candidate.suffix.casefold() == ".ttf":
            bold = "bold" if any(x in candidate.name.casefold()
                                     for x in ("ssb", "tsb")) else ""
            font = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
            fallback = resolve_case(
                epocroot / "epoc32/data/z/resource/fonts" / font
            )
        if actual is None:
            actual = fallback
            if actual is not None:
                fallbacks.append(f"{candidate}\t{actual}")
        if actual is None:
            omitted.append(str(candidate))
            result.append("REM HD2 omitted unavailable PDK input: " + raw)
            continue
        suffix = re.sub(
            r'"([^"]+)"',
            lambda quoted: f'"{quoted.group(1).lower()}"',
            match.group("suffix"),
        )
        result.append(
            f'{match.group("prefix")}{match.group("quote")}{actual}'
            f'{match.group("quote")}{suffix}'
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(result) + "\n")
    output.with_suffix(output.suffix + ".fallbacks.tsv").write_text(
        "\n".join(fallbacks) + "\n"
    )
    output.with_suffix(output.suffix + ".omitted").write_text(
        "\n".join(sorted(set(omitted))) + "\n"
    )
    output.with_suffix(output.suffix + ".patchdata-skipped").write_text(
        "\n".join(skipped_patchdata) + "\n"
    )
    print(
        f"full ROM recipe: fallbacks={len(fallbacks)} "
        f"omitted={len(set(omitted))} "
        f"patchdata_skipped={len(skipped_patchdata)} output={output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
