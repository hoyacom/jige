"""순수 함수(네트워크/파일시스템 없이 바로 판정 가능한 것) 회귀 테스트.

실행: python3 -m unittest discover -s tests -v
(설치/다운로드/uninstall처럼 실제 macOS 상태를 바꾸는 쪽은 여기서 다루지 않음 —
그쪽은 지금까지처럼 수동 검증 대상.)
"""
from __future__ import annotations

import unittest
from unittest import mock

from _load_jige import load_jige

jige = load_jige()
# jige 로딩 과정에서 sys.path에 REPO_ROOT를 넣고 jigelib를 이미 import해둠 — kind_icon/
# trust_badge 등은 이제 jigelib.display에 있고 자기 모듈의 _supports_unicode를 참조하므로,
# jige_cli.* 쪽을 patch해봐야 소용없고 실제 정의된 쪽(jigelib.display)을 patch해야 함.
from jigelib import display as jige_display  # noqa: E402


class PadVersionTuplesTest(unittest.TestCase):
    def test_pads_shorter_tuple_with_zeros(self):
        self.assertEqual(
            jige._pad_version_tuples((12,), (13, 0, 1)),
            [(12, 0, 0), (13, 0, 1)],
        )

    def test_equal_length_untouched(self):
        self.assertEqual(
            jige._pad_version_tuples((12, 7), (12, 6)),
            [(12, 7), (12, 6)],
        )


class MeetsMinMacosTest(unittest.TestCase):
    def test_exact_major_meets_requirement(self):
        with mock.patch.object(jige, "macos_version_tuple", return_value=(12, 7, 6)):
            self.assertTrue(jige.meets_min_macos("12"))

    def test_below_requirement_fails(self):
        with mock.patch.object(jige, "macos_version_tuple", return_value=(11, 7)):
            self.assertFalse(jige.meets_min_macos("12"))

    def test_minor_version_requirement(self):
        with mock.patch.object(jige, "macos_version_tuple", return_value=(13, 2)):
            self.assertTrue(jige.meets_min_macos("13.0"))
            self.assertFalse(jige.meets_min_macos("13.3"))


class DisplayWidthTest(unittest.TestCase):
    def test_ascii_is_one_per_char(self):
        self.assertEqual(jige._display_width("hop"), 3)

    def test_korean_is_two_per_char(self):
        self.assertEqual(jige._display_width("이름"), 4)

    def test_ambiguous_width_symbol_counts_as_two(self):
        # "…"/"★"/"▼" 등 — 한글 로케일 터미널에서 2칸으로 그려져서 2로 셈
        # (2026-11-11에 VirtualBox 행에서 줄바꿈이 깨지던 실제 버그 재발 방지용)
        self.assertEqual(jige._display_width("▼"), 2)

    def test_pad_fills_to_target_width(self):
        self.assertEqual(jige._pad("ab", 5), "ab   ")

    def test_pad_never_shrinks(self):
        self.assertEqual(jige._pad("가나다", 2), "가나다")


class TruncateToWidthTest(unittest.TestCase):
    def test_short_string_unchanged(self):
        self.assertEqual(jige._truncate_to_width("short", 20), "short")

    def test_long_string_gets_ellipsis_and_fits_width(self):
        out = jige._truncate_to_width("a very long description text", 10)
        self.assertLessEqual(jige._display_width(out), 10)
        self.assertTrue(out.endswith("…") or out.endswith("..."))


class SimplifyVersionForDisplayTest(unittest.TestCase):
    def test_strips_comma_suffix(self):
        self.assertEqual(jige.simplify_version_for_display("7.1.18,175245"), "7.1.18")

    def test_strips_numeric_dash_suffix(self):
        self.assertEqual(jige.simplify_version_for_display("1.2.3-174740"), "1.2.3")

    def test_keeps_dash_in_prerelease_word(self):
        # 숫자가 바로 뒤따르지 않는 하이픈(예: "-beta")은 버전의 일부로 보고 안 자름
        self.assertEqual(jige.simplify_version_for_display("1.2.3-beta"), "1.2.3-beta")

    def test_plain_version_unchanged(self):
        self.assertEqual(jige.simplify_version_for_display("1.2.3"), "1.2.3")


class RankTest(unittest.TestCase):
    def test_exact_match_ranks_best(self):
        self.assertLess(jige._rank("hop", "hop"), jige._rank("hop", "hopenpgp-tools"))

    def test_no_match_is_999(self):
        self.assertEqual(jige._rank("zzz-nope", "hop", "HWP viewer"), 999)

    def test_ignores_spaces_hyphens_as_fallback(self):
        # "InputSourcePro"가 토큰 "input-source-pro"를 찾아야 함(정확 매칭보단 낮은 순위)
        rank = jige._rank("InputSourcePro", "input-source-pro")
        self.assertLess(rank, 999)


class VersionSortKeyTest(unittest.TestCase):
    def test_numeric_parts_sort_numerically_not_lexically(self):
        # 문자열 정렬이면 "3.10" < "3.9" (틀림) — _version_sort_key는 숫자로 비교해야 함
        versions = ["3.9", "3.10", "3.2"]
        versions.sort(key=jige._version_sort_key)
        self.assertEqual(versions, ["3.2", "3.9", "3.10"])


class DependsOnMacosFloorTest(unittest.TestCase):
    def test_codename_symbol(self):
        self.assertEqual(jige.depends_on_macos_floor(">= :monterey"), "12")

    def test_bare_codename_symbol(self):
        self.assertEqual(jige.depends_on_macos_floor(":ventura"), "13")

    def test_numeric_expression(self):
        self.assertEqual(jige.depends_on_macos_floor(">= 13"), "13")

    def test_unrecognized_expression_is_none(self):
        self.assertIsNone(jige.depends_on_macos_floor(">= :nonexistent_codename"))


class ResolveCaskRbUrlTest(unittest.TestCase):
    def test_substitutes_known_placeholders(self):
        url = jige.resolve_cask_rb_url(
            "https://example.com/v#{version}/app-#{arch}.dmg", "1.2.3", "arm64"
        )
        self.assertEqual(url, "https://example.com/v1.2.3/app-arm64.dmg")

    def test_csv_version_placeholders(self):
        url = jige.resolve_cask_rb_url(
            "https://example.com/#{version.csv.first}/b#{version.csv.second}.dmg",
            "7.1.18,175245",
            "x86_64",
        )
        self.assertEqual(url, "https://example.com/7.1.18/b175245.dmg")

    def test_unknown_placeholder_gives_up(self):
        self.assertIsNone(
            jige.resolve_cask_rb_url("https://example.com/#{something_unknown}", "1.0", "arm64")
        )


class ParseCaskRbTest(unittest.TestCase):
    def setUp(self):
        self.hash_a = "a" * 64
        self.hash_b = "b" * 64
        self.text = (
            'cask "examplecask" do\n'
            '  arch arm: "arm64", intel: "x86_64"\n'
            '  version "7.1.18,175245"\n'
            f'  sha256 arm:   "{self.hash_a}",\n'
            f'         intel: "{self.hash_b}"\n'
            '  url "https://example.com/v#{version.csv.first}/Example-#{arch}.dmg"\n'
            '  name "Example"\n'
            '  desc "An example app"\n'
            '  homepage "https://example.com/"\n'
            '  depends_on macos: ">= :monterey"\n'
            '  app "Example.app"\n'
            "end\n"
        )

    def test_parses_all_fields(self):
        parsed = jige.parse_cask_rb(self.text)
        self.assertEqual(parsed["version"], "7.1.18,175245")
        self.assertEqual(parsed["arch_map"], {"arm": "arm64", "intel": "x86_64"})
        self.assertEqual(parsed["sha256"], {"arm": self.hash_a, "intel": self.hash_b})
        self.assertEqual(
            parsed["url_template"],
            "https://example.com/v#{version.csv.first}/Example-#{arch}.dmg",
        )
        self.assertEqual(parsed["app"], "Example.app")
        self.assertIsNone(parsed.get("pkg"))
        # 캡처는 따옴표 포함 원문 그대로(.rb 소스의 ">= :monterey" 리터럴) —
        # depends_on_macos_floor()가 따옴표를 무시하고 코드네임/숫자를 뽑아내는지는 별도 테스트로 확인
        self.assertEqual(parsed["depends_on_macos"], '">= :monterey"')
        self.assertEqual(jige.depends_on_macos_floor(parsed["depends_on_macos"]), "12")

    def test_single_sha256_applies_to_both_arches(self):
        text = (
            'cask "x" do\n'
            '  version "1.0"\n'
            f'  sha256 "{self.hash_a}"\n'
            '  url "https://example.com/x.dmg"\n'
            '  app "X.app"\n'
            "end\n"
        )
        parsed = jige.parse_cask_rb(text)
        self.assertEqual(parsed["sha256"], {"arm": self.hash_a, "intel": self.hash_a})

    def test_pkg_artifact_detected(self):
        text = (
            'cask "x" do\n'
            '  version "1.0"\n'
            '  pkg "Installer.pkg"\n'
            "end\n"
        )
        parsed = jige.parse_cask_rb(text)
        self.assertEqual(parsed["pkg"], "Installer.pkg")

    def test_platform_marker_depends_on_not_mistaken_for_version_floor(self):
        # "depends_on :macos"(플랫폼 마커, 버전 없음)는 depends_on_macos로 안 잡혀야 함 —
        # 버전 비교형("depends_on macos: ...")과 구분하는 정규식이 실수로 둘 다 잡으면 안 됨
        text = 'cask "x" do\n  version "1.0"\n  depends_on :macos\nend\n'
        parsed = jige.parse_cask_rb(text)
        self.assertIsNone(parsed.get("depends_on_macos"))


class KindIconTest(unittest.TestCase):
    def test_unicode_icons(self):
        with mock.patch.object(jige_display, "_supports_unicode", return_value=True):
            self.assertEqual(jige.kind_icon("jim"), "💻")
            self.assertEqual(jige.kind_icon("dogu"), "🔧")

    def test_ascii_fallback(self):
        with mock.patch.object(jige_display, "_supports_unicode", return_value=False):
            self.assertEqual(jige.kind_icon("jim"), "GUI")
            self.assertEqual(jige.kind_icon("dogu"), "CLI")

    def test_unknown_kind_falls_back(self):
        with mock.patch.object(jige_display, "_supports_unicode", return_value=True):
            self.assertEqual(jige.kind_icon("something_else"), "❓")


class TrustBadgeTest(unittest.TestCase):
    def test_zero_confirmations_is_new(self):
        with mock.patch.object(jige_display, "_supports_unicode", return_value=True):
            self.assertEqual(jige.trust_badge({"confirmations": []}), "🆕")

    def test_few_confirmations(self):
        with mock.patch.object(jige_display, "_supports_unicode", return_value=True):
            self.assertEqual(jige.trust_badge({"confirmations": [1, 2]}), "✓2")

    def test_many_confirmations(self):
        with mock.patch.object(jige_display, "_supports_unicode", return_value=True):
            self.assertEqual(jige.trust_badge({"confirmations": [1, 2, 3]}), "✓✓3")

    def test_missing_confirmations_key_treated_as_zero(self):
        with mock.patch.object(jige_display, "_supports_unicode", return_value=True):
            self.assertEqual(jige.trust_badge({}), "🆕")


class PlanArtifactsTest(unittest.TestCase):
    def test_separates_supported_from_skipped(self):
        recipe = {
            "artifacts": [
                {"app": ["Example.app"]},
                {"binary": ["example"]},
                {"zsh_completion": ["_example"]},
            ]
        }
        todo, skipped = jige.plan_artifacts(recipe)
        self.assertEqual([key for key, _, _ in todo], ["app"])
        self.assertIn("CLI 명령 연결 (example)", skipped)
        self.assertIn("zsh 자동완성 (_example)", skipped)

    def test_target_and_uninstall_keys_are_not_counted_as_skipped(self):
        recipe = {
            "artifacts": [
                {"app": ["Example.app"], "target": "/Applications/Example.app"},
                {"uninstall": [{"quit": "com.example.app"}]},
            ]
        }
        todo, skipped = jige.plan_artifacts(recipe)
        self.assertEqual(len(todo), 1)
        self.assertEqual(skipped, [])

    def test_unsupported_only_artifact_list_is_still_flagged_for_caller(self):
        recipe = {"artifacts": [{"font": ["Example.ttf"]}]}
        todo, skipped = jige.plan_artifacts(recipe)
        self.assertEqual(todo, [])
        self.assertEqual(skipped, ["폰트 (Example.ttf)"])


class GuessFilePlatformArchTest(unittest.TestCase):
    def test_macos_dmg(self):
        platform_, arch_ = jige._guess_file_platform_arch("MyApp-1.0-arm64.dmg")
        self.assertEqual(platform_, "macos")
        self.assertEqual(arch_, "arm64")

    def test_windows_exe(self):
        platform_, _ = jige._guess_file_platform_arch("myapp-setup.exe")
        self.assertEqual(platform_, "windows")

    def test_linux_deb(self):
        platform_, _ = jige._guess_file_platform_arch("myapp_1.0_amd64.deb")
        self.assertEqual(platform_, "linux")

    def test_unrecognized_name_returns_none_none(self):
        self.assertEqual(jige._guess_file_platform_arch("data.bin"), (None, None))


class ResolveUserRepoFileTest(unittest.TestCase):
    def test_picks_latest_version_matching_this_machine(self):
        entry = {
            "versions": {
                "1.0": {"files": [{"platform": "macos", "arch": "arm64"}]},
                "2.0": {"files": [{"platform": "macos", "arch": "arm64"}]},
                "1.5": {"files": [{"platform": "macos", "arch": "arm64"}]},
            }
        }
        result = jige.resolve_user_repo_file(entry, "arm64")
        self.assertEqual(result["version"], "2.0")

    def test_filters_out_wrong_arch(self):
        entry = {
            "versions": {
                "1.0": {"files": [{"platform": "macos", "arch": "x86_64"}]},
            }
        }
        self.assertIsNone(jige.resolve_user_repo_file(entry, "arm64"))

    def test_missing_platform_and_arch_means_supported_everywhere(self):
        entry = {"versions": {"1.0": {"files": [{}]}}}
        result = jige.resolve_user_repo_file(entry, "arm64")
        self.assertEqual(result["version"], "1.0")

    def test_min_os_filters_by_current_machine(self):
        entry = {"versions": {"1.0": {"files": [{"min_os": "99"}]}}}
        with mock.patch.object(jige, "macos_version_tuple", return_value=(12, 0)):
            self.assertIsNone(jige.resolve_user_repo_file(entry, "arm64"))


class DetectContainerTest(unittest.TestCase):
    def test_zip(self):
        import tempfile
        import zipfile
        with tempfile.TemporaryDirectory() as tmp:
            path = jige.Path(tmp) / "a.zip"
            with zipfile.ZipFile(path, "w") as zf:
                zf.writestr("hello.txt", "hi")
            self.assertEqual(jige.detect_container(path), "zip")

    def test_tar(self):
        import tarfile
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            src = jige.Path(tmp) / "hello.txt"
            src.write_text("hi")
            path = jige.Path(tmp) / "a.tar"
            with tarfile.open(path, "w") as tf:
                tf.add(src, arcname="hello.txt")
            self.assertEqual(jige.detect_container(path), "tar")

    def test_directory(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(jige.detect_container(jige.Path(tmp)), "directory")

    def test_uncompressed_binary(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = jige.Path(tmp) / "plain.bin"
            path.write_bytes(b"\x00\x01\x02\x03not a known container")
            self.assertEqual(jige.detect_container(path), "uncompressed")


if __name__ == "__main__":
    unittest.main()
