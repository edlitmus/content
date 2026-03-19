import xml.etree.ElementTree as ET

import pytest

from utils.convert_results_to_disa import _parse_profile_map_entries
from utils.convert_results_to_disa import convert_results


XCCDF_NS = "http://checklists.nist.gov/xccdf/1.2"


def _write_xml(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(content)
    return path


def test_convert_results_rewrites_benchmark_profile_and_rule_ids(tmp_path):
    disa_path = _write_xml(
        tmp_path,
        "disa.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<Benchmark xmlns="{XCCDF_NS}" id="xccdf_mil.disa.benchmark_mongodb">
  <title>MongoDB Benchmark</title>
  <Profile id="xccdf_mil.disa_profile_MAC-1_Public">
    <title>MAC-1 Public</title>
  </Profile>
  <Group id="group">
    <Rule id="xccdf_mil.disa_rule_MD7X-00-000200">
      <title>MD7X-00-000200 External Identity Provider</title>
    </Rule>
  </Group>
</Benchmark>
""",
    )
    results_path = _write_xml(
        tmp_path,
        "results.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<Benchmark xmlns="{XCCDF_NS}" id="xccdf_org.ssgproject.content_benchmark_mongodb">
  <title>SSG MongoDB Benchmark</title>
  <Profile id="xccdf_org.ssgproject.content_profile_stig">
    <title>MAC-1 Public</title>
  </Profile>
  <Group id="group">
    <Rule id="xccdf_org.ssgproject.content_rule_external_auth">
      <title>External Identity Provider</title>
      <reference>MD7X-00-000200</reference>
    </Rule>
  </Group>
  <TestResult id="xccdf_org.ssgproject.content_testresult_xccdf_org.ssgproject.content_profile_stig">
    <benchmark idref="xccdf_org.ssgproject.content_benchmark_mongodb"/>
    <profile idref="xccdf_org.ssgproject.content_profile_stig"/>
    <rule-result idref="xccdf_org.ssgproject.content_rule_external_auth" result="pass"/>
  </TestResult>
</Benchmark>
""",
    )
    output_path = tmp_path / "converted.xml"

    benchmark_changes, profile_changes, rule_changes, mapped_rules = convert_results(
        str(results_path), str(disa_path), str(output_path)
    )

    assert benchmark_changes == 2
    assert profile_changes == 2
    assert rule_changes == 2
    assert mapped_rules == 1

    root = ET.parse(output_path).getroot()
    assert root.get("id") == "xccdf_mil.disa.benchmark_mongodb"

    profile = root.find(".//{*}Profile")
    assert profile is not None
    assert profile.get("id") == "xccdf_mil.disa_profile_MAC-1_Public"

    rule = root.find(".//{*}Rule")
    assert rule is not None
    assert rule.get("id") == "xccdf_mil.disa_rule_MD7X-00-000200"

    test_result = root.find(".//{*}TestResult")
    assert test_result is not None
    assert test_result.get("id") == "xccdf_org.ssgproject.content_testresult_xccdf_mil.disa_profile_MAC-1_Public"

    test_profile = root.find(".//{*}TestResult/{*}profile")
    assert test_profile is not None
    assert test_profile.get("idref") == "xccdf_mil.disa_profile_MAC-1_Public"

    rule_result = root.find(".//{*}rule-result")
    assert rule_result is not None
    assert rule_result.get("idref") == "xccdf_mil.disa_rule_MD7X-00-000200"


def test_convert_results_accepts_profile_map_override(tmp_path):
    disa_path = _write_xml(
        tmp_path,
        "disa.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<Benchmark xmlns="{XCCDF_NS}" id="xccdf_mil.disa.benchmark_mongodb">
  <title>MongoDB Benchmark</title>
  <Profile id="xccdf_mil.disa_profile_CUSTOM">
    <title>Custom Profile Title</title>
  </Profile>
</Benchmark>
""",
    )
    results_path = _write_xml(
        tmp_path,
        "results.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<Benchmark xmlns="{XCCDF_NS}" id="xccdf_org.ssgproject.content_benchmark_mongodb">
  <Profile id="xccdf_org.ssgproject.content_profile_stig">
    <title>Non Matching Title</title>
  </Profile>
  <TestResult id="xccdf_org.ssgproject.content_testresult_xccdf_org.ssgproject.content_profile_stig">
    <profile idref="xccdf_org.ssgproject.content_profile_stig"/>
  </TestResult>
</Benchmark>
""",
    )
    output_path = tmp_path / "converted.xml"

    _, profile_changes, _, _ = convert_results(
        str(results_path),
        str(disa_path),
        str(output_path),
        profile_map_overrides=[
            "xccdf_org.ssgproject.content_profile_stig=xccdf_mil.disa_profile_CUSTOM"
        ],
    )

    assert profile_changes == 2

    root = ET.parse(output_path).getroot()
    profile = root.find(".//{*}Profile")
    assert profile is not None
    assert profile.get("id") == "xccdf_mil.disa_profile_CUSTOM"

    test_result = root.find(".//{*}TestResult")
    assert test_result is not None
    assert test_result.get("id") == "xccdf_org.ssgproject.content_testresult_xccdf_mil.disa_profile_CUSTOM"

    test_profile = root.find(".//{*}TestResult/{*}profile")
    assert test_profile is not None
    assert test_profile.get("idref") == "xccdf_mil.disa_profile_CUSTOM"


def test_parse_profile_map_entries_rejects_invalid_value():
    with pytest.raises(RuntimeError, match="Invalid --profile-map entry"):
        _parse_profile_map_entries(["not-an-assignment"])
