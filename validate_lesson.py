#!/usr/bin/env python3
"""
validate_lesson.py — Hugo 학습 페이지 품질 검증 도구 (Q1)

Hugo `.md` 자산마다 다음을 자동 검증:
  1. frontmatter 완전성         (title, date, draft, description, categories, tags, level, type, language, wikilink)
  2. wikilink 유효성             (frontmatter obsidian URI + body [[...]] 모두 wiki 자산 존재 확인)
  3. 한국어 학습자 노트          ("Korean Learner" / "한국어 학습자" / "Notes for Korean" / "🇰🇷")
  4. 단어 수                     (영어 본문 기준, 코드블록/표 제외)
  5. 표 헤더 일관성               (모든 표가 `:---:` 정렬 마커 사용)
  6. 한국어 요약 callout          (`> 🇰🇷 **한국어 요약**` 형식, full 페이지에 권장)
  7. 링크 유효성                  (Hugo 페이지 내 상대 경로 `[text](../path/)` 파일 존재 확인)
  8. 태그 일관성                  (`language: Spanish/Japanese/Chinese/Russian/Multilingual`)

사용법:
    python3 validate_lesson.py                          # Hugo 콘텐츠 전체 검증
    python3 validate_lesson.py content/lessons/foo/     # 단일 자산 검증
    python3 validate_lesson.py --lang Spanish           # 특정 언어만
    python3 validate_lesson.py --strict                  # WARN도 실패 처리
    python3 validate_lesson.py --json                    # JSON 출력
    python3 validate_lesson.py --report                   # logs/validation_YYYY-MM-DD.json 저장

Python 표준 라이브러리만 사용 (tomllib, re, json, argparse, pathlib).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Paths & constants
# ─────────────────────────────────────────────────────────────────────────────
WORKSPACE = Path("/Users/emilio/.openclaw/workspace")
HUGO_ROOT = WORKSPACE / "multilingual-blog" / "content"
WIKI_ROOT = WORKSPACE / "wiki"
LOG_DIR = WORKSPACE / "logs"

ALLOWED_LANGUAGES = {
    "Spanish",
    "Japanese",
    "Chinese",
    "Russian",
    "Multilingual",
    "Korean",
}

# Required frontmatter fields by asset type
REQUIRED_FM_FULL = ["title", "date", "draft", "description", "categories", "tags",
                    "level", "type", "wikilink"]
REQUIRED_FM_KO = ["title", "date", "draft", "description", "categories", "tags",
                  "level", "wikilink"]
REQUIRED_FM_INDEX = ["title", "date", "draft", "description"]

# Checkpoint color codes (terminal)
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"
NO_COLOR = ""

# Score weights per check (max = sum of weights)
CHECK_WEIGHTS = {
    "frontmatter": 25,
    "wikilink_fm": 15,
    "wikilink_body": 15,
    "korean_learner_note": 10,
    "word_count": 5,
    "table_alignment": 10,
    "korean_summary_callout": 8,
    "relative_links": 7,
    "language_tag": 5,
}
MAX_SCORE = sum(CHECK_WEIGHTS.values())  # 100


# ─────────────────────────────────────────────────────────────────────────────
# Result dataclass
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Issue:
    check: str
    status: str  # "PASS" / "WARN" / "FAIL"
    message: str


@dataclass
class AssetResult:
    path: str
    rel_path: str
    asset_type: str  # "full" / "ko_summary" / "section_index"
    language: Optional[str] = None
    issues: list[Issue] = field(default_factory=list)
    score: int = 0
    max_score: int = MAX_SCORE
    status: str = "PASS"  # PASS / WARN / FAIL
    word_count: int = 0
    table_count: int = 0
    wikilink_count: int = 0

    def to_dict(self) -> dict:
        d = asdict(self)
        d["issues"] = [{"check": i.check, "status": i.status, "message": i.message}
                       for i in self.issues]
        return d


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def parse_frontmatter(text: str) -> tuple[dict, str]:
    """TOML frontmatter (`+++...+++`) 분리해서 (fm_dict, body) 반환. 실패 시 ({}, text)."""
    if not text.startswith("+++"):
        return {}, text
    end = text.find("\n+++", 3)
    if end == -1:
        return {}, text
    fm_block = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    try:
        fm = tomllib.loads(fm_block)
    except tomllib.TOMLDecodeError as e:
        return {"_parse_error": str(e)}, body
    return fm, body


def classify_asset(md_path: Path, fm: dict) -> str:
    """자산 타입 분류: 'full' / 'ko_summary' / 'section_index'."""
    name = md_path.name
    if name == "_index.md":
        return "section_index"
    if name.endswith(".ko.md"):
        return "ko_summary"
    return "full"


def detect_language(fm: dict, md_path: Path) -> Optional[str]:
    """자산의 language 추론 (fm 명시 → 경로 휴리스틱 순)."""
    lang = fm.get("language")
    if lang:
        return str(lang)
    parts = md_path.parts
    # multilingual-blog/content/<section>/<slug>/index.<lang>.md
    if "russian" in parts:
        return "Russian"
    if "spanish" in parts or "lessons" in parts or "concepts" in parts or "culture" in parts or "posts" in parts:
        return "Spanish"
    if "japanese" in parts:
        return "Japanese"
    if "chinese" in parts:
        return "Chinese"
    return None


def find_wikilink_in_obsidian_uri(uri: str) -> Optional[str]:
    """`obsidian://open?vault=workspace&file=wiki/.../Foo.md` → 'wiki/.../Foo.md' 추출."""
    m = re.search(r"file=([^&\s]+)", uri)
    return m.group(1) if m else None


def build_wiki_index(wiki_root: Path) -> dict[str, list[Path]]:
    """wiki/ 전체의 .md 파일을 basename(stem) 기준으로 인덱싱.
    반환: {stem: [Path, ...]} (모호성 시 여러 후보)."""
    idx: dict[str, list[Path]] = {}
    if not wiki_root.exists():
        return idx
    for p in wiki_root.rglob("*.md"):
        # _*.md (메타 인덱스)는 wikilink 타겟에서 제외
        if p.name.startswith("_"):
            continue
        idx.setdefault(p.stem, []).append(p)
    return idx


def collect_body_wikilinks(body: str) -> list[str]:
    """본문에서 `[[X]]` 패턴을 모두 추출 (raw, 파이프|alt 표기는 첫 세그먼트만)."""
    return [m.strip() for m in re.findall(r"\[\[([^\]]+)\]\]", body)]


def count_words(body: str, lang: Optional[str]) -> int:
    """본문 단어 수 (대략). 코드블록/표/HTML 제외.
    ko_summary / Korean 본문은 CJK 문자 1개당 1단어로 계산."""
    # 코드 블록 제거
    body = re.sub(r"```.*?```", " ", body, flags=re.DOTALL)
    # 인라인 코드 제거
    body = re.sub(r"`[^`]+`", " ", body)
    # 표 제거 (| ... | 연속 라인)
    body = re.sub(r"(?:^\s*\|.*\|\s*$)+", " ", body, flags=re.MULTILINE)
    # HTML 태그 제거
    body = re.sub(r"<[^>]+>", " ", body)
    # 마크다운 기호 제거
    body = re.sub(r"[#*\[\]()>`_~]", " ", body)
    if lang in ("Korean", None) and not _looks_english(body):
        # CJK 단어 카운트
        cjk = re.findall(r"[\uac00-\ud7af\u3040-\u30ff\u4e00-\u9fff]", body)
        other = re.findall(r"[A-Za-z0-9]+", body)
        return len(cjk) + len(other)
    return len(re.findall(r"[A-Za-z0-9]+", body))


def _looks_english(text: str) -> bool:
    """텍스트가 영문 위주인지 휴리스틱."""
    en = len(re.findall(r"[A-Za-z]", text))
    ko = len(re.findall(r"[\uac00-\ud7af]", text))
    return en > ko


def collect_tables(body: str) -> list[list[str]]:
    """마크다운 표를 분리 행(row) 단위로 반환. 빈 행 기준 분할."""
    tables: list[list[str]] = []
    current: list[str] = []
    for line in body.splitlines():
        if re.match(r"^\s*\|.*\|\s*$", line):
            current.append(line)
        else:
            if current:
                tables.append(current)
                current = []
    if current:
        tables.append(current)
    return tables


def collect_relative_links(body: str) -> list[str]:
    """본문에서 상대 경로 링크 `[text](path)` 추출. 외부 http(s)·앵커·이미지는 제외."""
    links = []
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", body):
        path = m.group(2).strip()
        if not path:
            continue
        if path.startswith(("http://", "https://", "#", "mailto:", "obsidian://", "/", "tel:")):
            continue
        # 앵커만 있는 경우 (#section)
        if path.startswith("#"):
            continue
        # 이미지 스킵
        if m.group(1).startswith("!["):
            continue
        # 쿼리/프래그먼트 제거
        clean = path.split("#")[0].split("?")[0]
        links.append(clean)
    return links


def korean_learner_patterns() -> list[re.Pattern]:
    """한국어 학습자 노트 섹션 / callout 패턴."""
    return [
        re.compile(r"##\s*📌\s*한국어 학습자를 위한 요약"),
        re.compile(r"##\s*Korean Learner", re.IGNORECASE),
        re.compile(r"##\s*Notes for Korean", re.IGNORECASE),
        re.compile(r"한국어 학습자", re.IGNORECASE),
        re.compile(r"Korean Learner", re.IGNORECASE),
        re.compile(r"Notes for Korean", re.IGNORECASE),
    ]


def korean_callout_patterns() -> list[re.Pattern]:
    """한국어 요약 callout 패턴."""
    return [
        re.compile(r"^>\s*🇰🇷", re.MULTILINE),
        re.compile(r"^>\s*\*\*한국어 요약", re.MULTILINE),
        re.compile(r"한국어 요약\s*\(Korean Summary\)", re.IGNORECASE),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Validation checks
# ─────────────────────────────────────────────────────────────────────────────
def _check_frontmatter(fm: dict, asset_type: str, md_path: Path) -> tuple[Issue, int]:
    """1. frontmatter 완전성. asset_type 별로 필수 필드 확인."""
    if "_parse_error" in fm:
        return (Issue("frontmatter", "FAIL",
                      f"frontmatter 파싱 실패: {fm['_parse_error']}"),
                0)

    if asset_type == "full":
        required = REQUIRED_FM_FULL
    elif asset_type == "ko_summary":
        required = REQUIRED_FM_KO
    else:  # section_index
        required = REQUIRED_FM_INDEX

    missing = [k for k in required if k not in fm]
    # tags는 빈 배열도 허용하므로 len 검사 X (선택)
    if not missing:
        return (Issue("frontmatter", "PASS",
                      f"필수 {len(required)}개 필드 모두 존재"),
                CHECK_WEIGHTS["frontmatter"])

    # ko_summary 에선 type/language 가 없는 게 정상 → 우선도 조정
    detail = ", ".join(missing)
    if asset_type == "ko_summary" and missing and all(m in ("type", "language") for m in missing):
        return (Issue("frontmatter", "PASS",
                      f"ko_summary 정상 (선택 필드만 결여: {detail})"),
                CHECK_WEIGHTS["frontmatter"])

    # 부분 결여: 절반 이하 → WARN, 초과 → FAIL
    ratio = len(missing) / len(required)
    if ratio <= 0.3:
        return (Issue("frontmatter", "WARN",
                      f"일부 필드 결여: {detail}"),
                int(CHECK_WEIGHTS["frontmatter"] * 0.6))
    return (Issue("frontmatter", "FAIL",
                  f"필수 필드 다수 결여: {detail}"),
            0)


def _check_wikilink_fm(fm: dict, md_path: Path) -> tuple[Issue, int]:
    """2a. frontmatter wikilink (obsidian URI) → wiki/ 실제 파일 존재 확인."""
    uri = fm.get("wikilink")
    if not uri:
        if "_parse_error" in fm:
            return (Issue("wikilink_fm", "FAIL", "frontmatter 파싱 실패"), 0)
        return (Issue("wikilink_fm", "WARN",
                      "wikilink 필드 없음"),
                int(CHECK_WEIGHTS["wikilink_fm"] * 0.5))

    target = find_wikilink_in_obsidian_uri(str(uri))
    if not target:
        return (Issue("wikilink_fm", "WARN",
                      f"obsidian URI 파싱 실패: {uri}"),
                int(CHECK_WEIGHTS["wikilink_fm"] * 0.5))

    # target은 'wiki/.../File.md' 형태 → WIKI_ROOT 와 결합
    resolved = WIKI_ROOT / target.replace("wiki/", "", 1) if target.startswith("wiki/") else WIKI_ROOT / target
    # 위는 target='wiki/...' 라서 strip, 다른 형태도 시도
    if not resolved.exists():
        alt = WIKI_ROOT / target
        if alt.exists():
            resolved = alt
    if resolved.exists():
        return (Issue("wikilink_fm", "PASS",
                      f"→ {resolved.relative_to(WORKSPACE)}"),
                CHECK_WEIGHTS["wikilink_fm"])
    return (Issue("wikilink_fm", "FAIL",
                  f"타겟 파일 없음: wiki/{target}"),
            0)


def _check_wikilink_body(body: str, wiki_idx: dict) -> tuple[Issue, int, int]:
    """2b. 본문 [[X]] 위키링크 유효성. wikilink_count 도 반환."""
    raw = collect_body_wikilinks(body)
    if not raw:
        return (Issue("wikilink_body", "PASS", "본문 wikilink 없음 (정상)"),
                CHECK_WEIGHTS["wikilink_body"], 0)

    broken: list[str] = []
    for token in raw:
        # [[Name|alias]] 또는 [[Name#section]] 처리
        name = token.split("|")[0].split("#")[0].strip()
        if not name:
            continue
        if name not in wiki_idx:
            broken.append(name)

    if not broken:
        return (Issue("wikilink_body", "PASS",
                      f"{len(raw)}개 wikilink 모두 유효"),
                CHECK_WEIGHTS["wikilink_body"], len(raw))

    ratio = len(broken) / len(raw)
    detail = ", ".join(sorted(set(broken))[:5])
    more = f" 외 {len(set(broken)) - 5}개" if len(set(broken)) > 5 else ""
    if ratio <= 0.3:
        return (Issue("wikilink_body", "WARN",
                      f"{len(broken)}/{len(raw)} wikilink 깨짐: {detail}{more}"),
                int(CHECK_WEIGHTS["wikilink_body"] * 0.5),
                len(raw))
    return (Issue("wikilink_body", "FAIL",
                  f"{len(broken)}/{len(raw)} wikilink 깨짐: {detail}{more}"),
            0, len(raw))


def _check_korean_learner_note(body: str, asset_type: str) -> tuple[Issue, int]:
    """3. 한국어 학습자 노트 / callout 존재 확인."""
    if asset_type == "ko_summary":
        # ko_summary 파일 자체가 한국어 요약 → 항상 PASS
        return (Issue("korean_learner_note", "PASS",
                      "ko_summary 자산 (한국어 요약 자체)"),
                CHECK_WEIGHTS["korean_learner_note"])

    for pat in korean_learner_patterns() + korean_callout_patterns():
        if pat.search(body):
            return (Issue("korean_learner_note", "PASS",
                          f"패턴 매칭: {pat.pattern[:40]}"),
                    CHECK_WEIGHTS["korean_learner_note"])
    # 권장이지 필수는 아님 → WARN
    return (Issue("korean_learner_note", "WARN",
                  "한국어 학습자 노트/콜아웃 없음 (권장)"),
            int(CHECK_WEIGHTS["korean_learner_note"] * 0.4))


def _check_word_count(body: str, asset_type: str, lang: Optional[str], asset_path: Path) -> tuple[Issue, int, int]:
    """4. 본문 단어 수. ko_summary 는 200+ 권장, full 은 500+ 권장, index 는 50+."""
    words = count_words(body, lang)
    if asset_type == "section_index":
        threshold_warn, threshold_fail = 30, 15
    elif asset_type == "ko_summary":
        threshold_warn, threshold_fail = 150, 50
    else:  # full
        threshold_warn, threshold_fail = 400, 100

    if words >= threshold_warn:
        return (Issue("word_count", "PASS",
                      f"{words} 단어 (권장 ≥ {threshold_warn})"),
                CHECK_WEIGHTS["word_count"], words)
    if words >= threshold_fail:
        return (Issue("word_count", "WARN",
                      f"{words} 단어 (권장 ≥ {threshold_warn}, 최소 ≥ {threshold_fail})"),
                int(CHECK_WEIGHTS["word_count"] * 0.6), words)
    return (Issue("word_count", "FAIL",
                  f"{words} 단어 (최소 {threshold_fail} 미만)"),
            0, words)


def _check_table_alignment(body: str) -> tuple[Issue, int, int]:
    """5. 표 헤더 정렬 마커(:---:, :---, ---:) 일관성."""
    tables = collect_tables(body)
    if not tables:
        return (Issue("table_alignment", "PASS", "표 없음 (해당없음)"),
                CHECK_WEIGHTS["table_alignment"], 0)

    bad: list[int] = []  # bad table indices
    for idx, rows in enumerate(tables):
        if len(rows) < 2:
            continue
        # 두 번째 행이 정렬 마커 행이어야 함
        sep = rows[1]
        if not re.search(r"\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?", sep):
            # 단순 --- 도 허용
            if not re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", sep):
                bad.append(idx)

    if not bad:
        return (Issue("table_alignment", "PASS",
                      f"{len(tables)}개 표 모두 정렬 마커 사용"),
                CHECK_WEIGHTS["table_alignment"], len(tables))

    if len(bad) <= max(1, len(tables) // 3):
        return (Issue("table_alignment", "WARN",
                      f"{len(bad)}/{len(tables)} 표에 정렬 마커 누락"),
                int(CHECK_WEIGHTS["table_alignment"] * 0.6), len(tables))
    return (Issue("table_alignment", "FAIL",
                  f"{len(bad)}/{len(tables)} 표에 정렬 마커 누락"),
            0, len(tables))


def _check_korean_callout(body: str, asset_type: str, lang: Optional[str]) -> tuple[Issue, int]:
    """6. 한국어 요약 callout (`> 🇰🇷 **한국어 요약**`) — full 페이지 권장."""
    if asset_type == "ko_summary":
        return (Issue("korean_summary_callout", "PASS",
                      "ko_summary 자산은 callout 불요"),
                CHECK_WEIGHTS["korean_summary_callout"])
    for pat in korean_callout_patterns():
        if pat.search(body):
            return (Issue("korean_summary_callout", "PASS",
                          f"패턴 매칭: {pat.pattern[:40]}"),
                    CHECK_WEIGHTS["korean_summary_callout"])
    # 권장이지 필수는 아님
    return (Issue("korean_summary_callout", "WARN",
                  "한국어 요약 callout 없음 (권장)"),
            int(CHECK_WEIGHTS["korean_summary_callout"] * 0.4))


def _check_relative_links(body: str, asset_path: Path) -> tuple[Issue, int]:
    """7. 본문 상대 경로 링크 파일 존재 확인."""
    links = collect_relative_links(body)
    if not links:
        return (Issue("relative_links", "PASS", "상대 링크 없음"),
                CHECK_WEIGHTS["relative_links"])

    broken: list[str] = []
    for link in links:
        # Hugo 페이지의 상대 경로는 asset_path 의 부모 디렉터리 기준
        # 예: lessons/daily-routine/index.en.md 의 `./travel-directions/` →
        #     lessons/travel-directions/index.md 또는 .en.md / .ko.md
        target = (asset_path.parent / link).resolve()
        if target.exists():
            continue
        # index.md 자동 추가 시도 (디렉터리 링크)
        if target.is_dir() or (target.parent / "index.md").exists():
            continue
        # .en.md / .ko.md 자동 추가 시도
        for suffix in (".md", "/index.md", "/index.en.md", "/index.ko.md"):
            candidate = (asset_path.parent / (link.rstrip("/") + suffix)).resolve()
            if candidate.exists():
                break
        else:
            broken.append(link)

    if not broken:
        return (Issue("relative_links", "PASS",
                      f"{len(links)}개 링크 모두 유효"),
                CHECK_WEIGHTS["relative_links"])
    detail = ", ".join(broken[:5])
    return (Issue("relative_links", "WARN",
                  f"{len(broken)}/{len(links)} 링크 깨짐: {detail}"),
            int(CHECK_WEIGHTS["relative_links"] * 0.4))


def _check_language_tag(fm: dict) -> tuple[Issue, int]:
    """8. language 필드 일관성 (있으면 허용 목록 안에 있어야 함)."""
    if "language" not in fm:
        # 없는 건 정상 (대부분 en 자산) → PASS
        return (Issue("language_tag", "PASS",
                      "language 필드 없음 (영문 기본)"),
                CHECK_WEIGHTS["language_tag"])
    lang = str(fm["language"]).strip()
    if lang in ALLOWED_LANGUAGES:
        return (Issue("language_tag", "PASS",
                      f"language = {lang}"),
                CHECK_WEIGHTS["language_tag"])
    return (Issue("language_tag", "FAIL",
                  f"허용되지 않은 language: {lang} (허용: {sorted(ALLOWED_LANGUAGES)})"),
            0)


# ─────────────────────────────────────────────────────────────────────────────
# Asset validation driver
# ─────────────────────────────────────────────────────────────────────────────
def validate_asset(md_path: Path, wiki_idx: dict, use_color: bool = True) -> AssetResult:
    """자산 1개 검증 → AssetResult."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = md_path.read_text(encoding="utf-8", errors="replace")

    fm, body = parse_frontmatter(text)
    asset_type = classify_asset(md_path, fm)
    lang = detect_language(fm, md_path)

    result = AssetResult(
        path=str(md_path),
        rel_path=str(md_path.relative_to(HUGO_ROOT)),
        asset_type=asset_type,
        language=lang,
    )

    # ── 8 checks ──
    checks = []
    issue, pts = _check_frontmatter(fm, asset_type, md_path)
    checks.append((issue, pts))
    issue, pts = _check_wikilink_fm(fm, md_path)
    checks.append((issue, pts))
    issue, pts, n_wikilinks = _check_wikilink_body(body, wiki_idx)
    checks.append((issue, pts))
    result.wikilink_count = n_wikilinks
    issue, pts = _check_korean_learner_note(body, asset_type)
    checks.append((issue, pts))
    issue, pts, words = _check_word_count(body, asset_type, lang, md_path)
    checks.append((issue, pts))
    result.word_count = words
    issue, pts, n_tables = _check_table_alignment(body)
    checks.append((issue, pts))
    result.table_count = n_tables
    issue, pts = _check_korean_callout(body, asset_type, lang)
    checks.append((issue, pts))
    issue, pts = _check_relative_links(body, md_path)
    checks.append((issue, pts))
    issue, pts = _check_language_tag(fm)
    checks.append((issue, pts))

    # 집계
    total_pts = 0
    max_pts = 0
    worst = "PASS"
    rank = {"PASS": 0, "WARN": 1, "FAIL": 2}
    for issue, pts in checks:
        result.issues.append(issue)
        total_pts += pts
        # frontmatter/korean_learner_note/korean_callout/table_alignment은
        # max = 가중치, 나머지는 절반 가중치 (WARN 부분점)
        if issue.check in ("frontmatter", "korean_learner_note", "korean_summary_callout",
                           "table_alignment", "wikilink_fm", "wikilink_body",
                           "word_count", "relative_links", "language_tag"):
            max_pts += CHECK_WEIGHTS[issue.check]
        if rank[issue.status] > rank[worst]:
            worst = issue.status

    result.score = total_pts
    result.max_score = max_pts if max_pts > 0 else MAX_SCORE
    result.status = worst
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Discovery
# ─────────────────────────────────────────────────────────────────────────────
def discover_assets(target: Optional[Path], lang: Optional[str]) -> list[Path]:
    """타겟(파일/디렉터리/HUGO_ROOT) → 검증 대상 .md 자산 목록."""
    if target is None:
        root = HUGO_ROOT
    else:
        root = target.resolve()
        if root.is_file():
            return [root]
        if root.is_dir():
            # Hugo 자산 루트 보안: HUGO_ROOT 밖이면 무시
            try:
                root.relative_to(HUGO_ROOT)
            except ValueError:
                # 단, hugo.toml 기준 정상 경로면 인정
                pass
        else:
            return []

    assets: list[Path] = []
    for p in root.rglob("*.md"):
        # _index.md (섹션 인덱스) 포함 — 별도 카운트
        assets.append(p)

    # 언어 필터: frontmatter language 또는 경로 휴리스틱
    if lang:
        lang_lower = lang.lower()
        filtered: list[Path] = []
        for p in assets:
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            fm, _ = parse_frontmatter(text)
            asset_lang = (fm.get("language") or detect_language(fm, p) or "").lower()
            if asset_lang == lang_lower:
                filtered.append(p)
        assets = filtered

    return sorted(assets)


# ─────────────────────────────────────────────────────────────────────────────
# Reporting
# ─────────────────────────────────────────────────────────────────────────────
def status_icon(status: str, use_color: bool) -> str:
    palette = {"PASS": GREEN, "WARN": YELLOW, "FAIL": RED}
    color = palette.get(status, "") if use_color else ""
    return f"{color}{status:<4}{RESET if use_color else ''}"


def print_human_report(results: list[AssetResult], use_color: bool) -> None:
    """사람이 읽기 좋은 콘솔 리포트."""
    if not results:
        print("⚠️  검증 대상 자산 없음")
        return

    # 자산별
    print(f"\n{BOLD}── 자산별 결과 ({len(results)}개) ──{RESET if use_color else ''}")
    for r in results:
        icon = status_icon(r.status, use_color)
        type_label = {"full": "📘", "ko_summary": "🇰🇷", "section_index": "📂"}.get(r.asset_type, "?")
        lang_tag = f" [{r.language}]" if r.language else ""
        print(f"{icon} {type_label} {r.rel_path}{lang_tag}  "
              f"{BOLD}{r.score}/{r.max_score}{RESET if use_color else ''}  "
              f"(words={r.word_count}, tables={r.table_count}, wikilinks={r.wikilink_count})")
        # 이슈 요약
        for issue in r.issues:
            if issue.status == "PASS":
                continue
            icon = status_icon(issue.status, use_color)
            print(f"    {icon} [{issue.check}] {issue.message}")

    # 통계
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    for r in results:
        counts[r.status] += 1
    total = len(results)
    avg_score = sum(r.score for r in results) / total if total else 0
    print(f"\n{BOLD}── 통계 ──{RESET if use_color else ''}")
    print(f"  PASS: {GREEN}{counts['PASS']}{RESET if use_color else ''}  "
          f"WARN: {YELLOW}{counts['WARN']}{RESET if use_color else ''}  "
          f"FAIL: {RED}{counts['FAIL']}{RESET if use_color else ''}  "
          f"(total {total})")
    print(f"  평균 점수: {avg_score:.1f}/{MAX_SCORE}")

    # 체크별 통계
    print(f"\n{BOLD}── 체크별 집계 ──{RESET if use_color else ''}")
    check_stats: dict[str, dict[str, int]] = {}
    for r in results:
        for issue in r.issues:
            check_stats.setdefault(issue.check, {"PASS": 0, "WARN": 0, "FAIL": 0})
            check_stats[issue.check][issue.status] += 1
    for check, stats in check_stats.items():
        print(f"  {check:<22} PASS={stats['PASS']:<3}  "
              f"WARN={stats['WARN']:<3}  FAIL={stats['FAIL']:<3}")


def build_json_report(results: list[AssetResult]) -> dict:
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "hugo_root": str(HUGO_ROOT),
        "asset_count": len(results),
        "summary": {
            "pass": sum(1 for r in results if r.status == "PASS"),
            "warn": sum(1 for r in results if r.status == "WARN"),
            "fail": sum(1 for r in results if r.status == "FAIL"),
            "avg_score": round(
                sum(r.score for r in results) / len(results), 1
            ) if results else 0,
            "max_score": MAX_SCORE,
        },
        "assets": [r.to_dict() for r in results],
    }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Hugo 학습 페이지 품질 검증 도구 (Q1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("path", nargs="?",
                    help="자산 경로 (없으면 Hugo 전체)")
    ap.add_argument("--lang", help="특정 언어 (Spanish/Japanese/Chinese/Russian/Multilingual)")
    ap.add_argument("--strict", action="store_true",
                    help="엄격 모드 (WARN 도 실패 처리)")
    ap.add_argument("--json", action="store_true", help="JSON 출력 (stdout)")
    ap.add_argument("--report", action="store_true",
                    help="logs/validation_YYYY-MM-DD.json 저장")
    ap.add_argument("--no-color", action="store_true", help="컬러 끄기")
    ap.add_argument("--quiet", "-q", action="store_true", help="요약만")
    args = ap.parse_args()

    use_color = (sys.stdout.isatty() and not args.no_color and not args.json)

    target = Path(args.path) if args.path else None
    assets = discover_assets(target, args.lang)
    if not assets:
        print(f"❌ 자산 0개 (target={target or 'Hugo 전체'}, lang={args.lang})", file=sys.stderr)
        return 1

    wiki_idx = build_wiki_index(WIKI_ROOT)

    if not args.quiet and not args.json:
        print(f"{BOLD}🔍 Hugo 학습 페이지 검증{RESET if use_color else ''}")
        print(f"   자산 {len(assets)}개, wiki 인덱스 {len(wiki_idx)}개")

    results = [validate_asset(p, wiki_idx, use_color=use_color) for p in assets]

    # strict 모드: WARN → FAIL 승격
    if args.strict:
        for r in results:
            if r.status == "WARN":
                r.status = "FAIL"
                for issue in r.issues:
                    if issue.status == "WARN":
                        issue.status = "FAIL"
            elif r.status == "FAIL":
                for issue in r.issues:
                    if issue.status == "WARN":
                        issue.status = "FAIL"

    if args.json:
        json.dump(build_json_report(results), sys.stdout, ensure_ascii=False, indent=2)
        print()  # newline
    else:
        print_human_report(results, use_color)

    if args.report or not args.json:
        # 기본적으로 JSON 리포트 저장 (--json 단독일 땐 stdout만)
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        report_path = LOG_DIR / f"validation_{datetime.now():%Y-%m-%d}.json"
        report_path.write_text(
            json.dumps(build_json_report(results), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        if not args.quiet:
            print(f"\n📄 JSON 리포트: {report_path.relative_to(WORKSPACE)}")

    # 종료 코드: FAIL 이 있으면 1 (strict 시 WARN 도 1)
    has_fail = any(r.status == "FAIL" for r in results)
    has_warn = any(r.status == "WARN" for r in results)
    if has_fail:
        return 1
    if args.strict and has_warn:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())