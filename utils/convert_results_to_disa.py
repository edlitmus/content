#!/usr/bin/env python3

"""Convert SSG XCCDF result XML IDs to match a DISA XCCDF benchmark.

This utility rewrites benchmark/profile/rule identifiers in an OpenSCAP XCCDF
results file generated from SSG content so the result can be imported into
systems that key off DISA benchmark IDs (e.g. STIG Manager).

Usage example:
  python3 utils/convert_results_to_disa.py \
    --results-in mongodb-results.xml \
    --disa-xccdf U_MongoDB_Enterprise_Advanced_7-x_STIG_V1R1_Manual-xccdf.xml \
    --results-out mongodb-results-disa.xml
"""

from __future__ import annotations

import argparse
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

STIG_ID_RE = re.compile(r"MD7X-\d{2}-\d{6}")


@dataclass
class BenchmarkData:
    benchmark_id: str
    profiles_by_title: Dict[str, str]
    rules_by_stig_id: Dict[str, str]


def _iter_text_chunks(elem: ET.Element) -> Iterable[str]:
    if elem.text:
        yield elem.text
    for child in list(elem):
        yield from _iter_text_chunks(child)
        if child.tail:
            yield child.tail


def _extract_stig_id_from_rule(rule: ET.Element) -> Optional[str]:
    rule_id = rule.get("id", "")
    match = STIG_ID_RE.search(rule_id)
    if match:
        return match.group(0)

    for text in _iter_text_chunks(rule):
        match = STIG_ID_RE.search(text)
        if match:
            return match.group(0)

    return None


def _normalize_profile_title(title: str) -> str:
    return " ".join(title.split()).strip()


def _parse_benchmark_data(path: str) -> BenchmarkData:
    tree = ET.parse(path)
    root = tree.getroot()

    benchmark = root if root.tag.endswith("Benchmark") else root.find(".//{*}Benchmark")
    if benchmark is None:
        raise RuntimeError(f"No Benchmark element found in {path}")

    benchmark_id = benchmark.get("id", "")
    if not benchmark_id:
        raise RuntimeError(f"Benchmark id is missing in {path}")

    profiles_by_title: Dict[str, str] = {}
    for profile in benchmark.findall(".//{*}Profile"):
        profile_id = profile.get("id")
        title = profile.find("{*}title")
        if not profile_id or title is None or title.text is None:
            continue
        profiles_by_title[_normalize_profile_title(title.text)] = profile_id

    rules_by_stig_id: Dict[str, str] = {}
    for rule in benchmark.findall(".//{*}Rule"):
        rule_id = rule.get("id")
        if not rule_id:
            continue
        stig_id = _extract_stig_id_from_rule(rule)
        if stig_id:
            rules_by_stig_id[stig_id] = rule_id

    return BenchmarkData(
        benchmark_id=benchmark_id,
        profiles_by_title=profiles_by_title,
        rules_by_stig_id=rules_by_stig_id,
    )


def _build_ssg_rule_stig_map(results_root: ET.Element) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for rule in results_root.findall(".//{*}Rule"):
        rule_id = rule.get("id")
        if not rule_id:
            continue
        stig_id = _extract_stig_id_from_rule(rule)
        if stig_id:
            mapping[rule_id] = stig_id
    return mapping


def _build_profile_map(results_root: ET.Element, disa: BenchmarkData) -> Dict[str, str]:
    profile_map: Dict[str, str] = {}

    for profile in results_root.findall(".//{*}Profile"):
        src_id = profile.get("id")
        title_elem = profile.find("{*}title")
        if not src_id or title_elem is None or not title_elem.text:
            continue

        title = _normalize_profile_title(title_elem.text)
        dst_id = disa.profiles_by_title.get(title)
        if dst_id:
            profile_map[src_id] = dst_id

    return profile_map


def _parse_profile_map_entries(entries: Optional[Iterable[str]]) -> Dict[str, str]:
    profile_map: Dict[str, str] = {}
    if not entries:
        return profile_map

    for entry in entries:
        if "=" not in entry:
            raise RuntimeError(
                f"Invalid --profile-map entry '{entry}'. Expected format: <src_profile_id>=<disa_profile_id>"
            )
        src, dst = entry.split("=", 1)
        src = src.strip()
        dst = dst.strip()
        if not src or not dst:
            raise RuntimeError(
                f"Invalid --profile-map entry '{entry}'. Expected non-empty source and destination ids."
            )
        profile_map[src] = dst

    return profile_map


def _replace_substring_attr(elem: ET.Element, attr: str, old: str, new: str) -> None:
    val = elem.get(attr)
    if val is None:
        return
    if old in val:
        elem.set(attr, val.replace(old, new))


def convert_results(
    results_in: str,
    disa_xccdf: str,
    results_out: str,
    profile_map_overrides: Optional[Iterable[str]] = None,
    force_profile_id: Optional[str] = None,
) -> Tuple[int, int, int, int]:
    ET.register_namespace("", "http://checklists.nist.gov/xccdf/1.2")

    disa = _parse_benchmark_data(disa_xccdf)
    results_tree = ET.parse(results_in)
    results_root = results_tree.getroot()

    # Rule mapping is derived via STIG IDs present in SSG rule metadata.
    ssg_rule_to_stigid = _build_ssg_rule_stig_map(results_root)
    rule_map: Dict[str, str] = {}
    for ssg_rule_id, stig_id in ssg_rule_to_stigid.items():
        disa_rule_id = disa.rules_by_stig_id.get(stig_id)
        if disa_rule_id:
            rule_map[ssg_rule_id] = disa_rule_id

    profile_map = _build_profile_map(results_root, disa)
    profile_map.update(_parse_profile_map_entries(profile_map_overrides))

    benchmark_changes = 0
    profile_changes = 0
    rule_changes = 0

    for elem in results_root.iter():
        for attr in ("id", "idref"):
            # Benchmark id rewrite
            if elem.get(attr) and elem.get(attr).startswith("xccdf_org.ssgproject.content_benchmark_"):
                if elem.get(attr) != disa.benchmark_id:
                    elem.set(attr, disa.benchmark_id)
                    benchmark_changes += 1

            # Profile id rewrites
            current = elem.get(attr)
            if current in profile_map and profile_map[current] != current:
                elem.set(attr, profile_map[current])
                profile_changes += 1

            # Rule id rewrites
            current = elem.get(attr)
            if current in rule_map and rule_map[current] != current:
                elem.set(attr, rule_map[current])
                rule_changes += 1

    # TestResult id often embeds profile id; replace these substrings too.
    for ssg_profile_id, disa_profile_id in profile_map.items():
        for elem in results_root.iter():
            _replace_substring_attr(elem, "id", ssg_profile_id, disa_profile_id)

    if force_profile_id:
        for profile in results_root.findall(".//{*}TestResult/{*}profile"):
            if profile.get("idref") != force_profile_id:
                profile.set("idref", force_profile_id)
                profile_changes += 1

    results_tree.write(results_out, encoding="utf-8", xml_declaration=True)

    return benchmark_changes, profile_changes, rule_changes, len(rule_map)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert SSG XCCDF result XML IDs to DISA IDs for STIG Manager import"
    )
    parser.add_argument("--results-in", required=True, help="Input XCCDF results XML generated from SSG content")
    parser.add_argument("--disa-xccdf", required=True, help="DISA XCCDF benchmark XML used by STIG Manager")
    parser.add_argument("--results-out", required=True, help="Output converted results XML")
    parser.add_argument(
        "--profile-map",
        action="append",
        help=(
            "Explicit profile-id mapping in the form <src_profile_id>=<disa_profile_id>. "
            "Can be specified multiple times."
        ),
    )
    parser.add_argument(
        "--force-profile-id",
        help="Force TestResult/profile@idref to this DISA profile id (useful when source profile has no DISA equivalent)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    benchmark_changes, profile_changes, rule_changes, mapped_rules = convert_results(
        args.results_in,
        args.disa_xccdf,
        args.results_out,
        profile_map_overrides=args.profile_map,
        force_profile_id=args.force_profile_id,
    )

    print(f"Converted results written to: {args.results_out}")
    print(f"Benchmark id changes: {benchmark_changes}")
    print(f"Profile id changes:   {profile_changes}")
    print(f"Rule id changes:      {rule_changes}")
    print(f"Mapped DISA rules:    {mapped_rules}")

    if mapped_rules == 0:
        print("WARNING: No rules were mapped. Verify that STIG IDs (e.g. MD7X-00-000200) exist in both files.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
