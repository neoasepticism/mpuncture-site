#!/usr/bin/env python3
"""
mpuncture.org 배포본 빌드

소스(Artifact 형식, head 없음) → docs/ (완전한 HTML 문서)

구조:
  /                    한국어 랜딩 (기본)  ← index.html
  /bacteria/           한국어 심화        ← decontamination.html
  /en/                 영문 랜딩          ← index-en.html
  /en/bacteria/        영문 심화          ← decontamination-en.html
"""
import re, shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
DOMAIN = "https://mpuncture.org"

# 아티팩트 URL → 실제 경로
ARTIFACT_MAP = {
    "https://claude.ai/code/artifact/af31d28f-8c55-4a8c-bdff-beafca8d4cc6": "/",              # KO landing (기본)
    "https://claude.ai/code/artifact/836a590c-62fc-4591-9129-ff6dad3d77bf": "/bacteria/",     # KO deep
    "https://claude.ai/code/artifact/67bfbe57-5a3d-4945-b3a9-e2e29a20df6b": "/en/",           # EN landing
    "https://claude.ai/code/artifact/2e4438eb-c097-4489-8cbf-d0d5aec8f75e": "/en/bacteria/",  # EN deep
}

PAGES = [
    dict(src="index.html",              out="index.html",                lang="ko", path="/",
         title="M-puncture 엠펑쳐 — 만성통증을 신경회로로 보는 관점",
         desc="만성통증을 조직이 아니라 신경회로의 문제로 보는 관점과, 그 위에 세워진 M-puncture(엠펑쳐, 엠펑처) "
              "치료의 기록. 환자와 의사를 위한 공공정보 아카이브.",
         alt="/en/"),
    dict(src="decontamination.html",    out="bacteria/index.html",       lang="ko", path="/bacteria/",
         title="세균과 만성통증 — 장에서, 그리고 조직에서 | 엠펑쳐",
         desc="장에서 오는 자극과 조직에 정착한 세균이 만성 근골격 통증을 유지시키는 경로 — "
              "확립된 질환, 기전, 그리고 아직 확인되지 않은 것.",
         alt="/en/bacteria/"),
    dict(src="index-en.html",           out="en/index.html",             lang="en", path="/en/",
         title="M-puncture — Chronic Pain as a Problem of the Nerve Circuit",
         desc="Chronic pain understood as a problem of the nerve circuit: the M-puncture approach, "
              "a bacterial second axis, and a practical record for physicians.",
         alt="/"),
    dict(src="decontamination-en.html", out="en/bacteria/index.html",    lang="en", path="/en/bacteria/",
         title="Bacteria and Chronic Pain — In the Gut, and in the Tissue",
         desc="Gut-derived input and tissue-resident organisms as drivers of chronic musculoskeletal "
              "pain — the established entities, the mechanisms, and what remains unresolved.",
         alt="/en/bacteria/".replace("/en/bacteria/","/bacteria/")),
    dict(src="principle.html",          out="principle/index.html",      lang="ko", path="/principle/",
         title="M-puncture의 원리 — 통증 회로를 어떻게 보는가 | 엠펑쳐",
         desc="만성통증을 신경 회로의 문제로 보는 M-puncture 이론(전동휘·이영진 모델)의 심화 정리 — "
              "C-신경섬유·PML/SML·제3의 통증 NNPS·시술 원리, 그리고 어디까지가 근거인가.",
         alt="/en/principle/"),
    dict(src="principle-en.html",       out="en/principle/index.html",   lang="en", path="/en/principle/",
         title="The Principle of M-puncture — How It Reads the Pain Circuit",
         desc="An in-depth account of the M-puncture theory (the Jun & Lee model): the C-fiber, PML/SML, "
              "the third pain type NNPS, the technique, and where the evidence stands.",
         alt="/principle/"),
    dict(src="lineage.html",            out="lineage/index.html",        lang="ko", path="/lineage/",
         title="M-puncture의 계보와 출처 — 어디에서 왔고, 무엇이 확인되는가 | 엠펑쳐",
         desc="M-puncture(엠펑쳐)의 계보와 출처를 투명하게 정리 — 전동휘·이영진의 세 판본과 ISBN, "
              "'acupuncture→needle-puncture' 이름의 변화, 편저자 이영진의 확인되는 이력, 근거상 위치.",
         alt="/en/lineage/"),
    dict(src="lineage-en.html",         out="en/lineage/index.html",     lang="en", path="/en/lineage/",
         title="The Lineage and Sources of M-puncture — Where It Came From, and What Can Be Verified",
         desc="A transparent account of M-puncture's lineage and sources: the three editions by Jun & Lee, "
              "the 'acupuncture to needle-puncture' name change, the editor's verifiable record, and where the evidence stands.",
         alt="/lineage/"),
]

SKELETON = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="June-sang Yang">
<meta name="msvalidate.01" content="5C3321B5366EE5A7E53AE1374649D57D">
<link rel="canonical" href="{domain}{path}">
<link rel="alternate" hreflang="{lang}" href="{domain}{path}">
<link rel="alternate" hreflang="{altlang}" href="{domain}{alt}">
<link rel="alternate" hreflang="x-default" href="{domain}/">
<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{domain}{path}">
<meta property="og:locale" content="{locale}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🧠</text></svg>">
<style>
  html{{ -webkit-text-size-adjust:100%; }}
  img,svg{{ max-width:100%; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    for p in PAGES:
        body = (ROOT / p["src"]).read_text(encoding="utf-8")

        # Artifact 소스 맨 앞의 <title>은 skeleton 의 <head><title> 과 중복되므로 제거
        body = re.sub(r'^\s*<title>.*?</title>\s*', '', body, count=1, flags=re.S)

        # 아티팩트 절대주소 → 사이트 내부 경로
        for url, path in ARTIFACT_MAP.items():
            body = body.replace(url, path)

        # 남은 아티팩트 주소가 없는지 확인
        leftover = re.findall(r"https://claude\.ai/code/artifact/[0-9a-f-]+", body)
        assert not leftover, f"{p['src']}: 미치환 주소 {set(leftover)}"

        html = SKELETON.format(
            lang=p["lang"],
            altlang="ko" if p["lang"] == "en" else "en",
            locale="en_US" if p["lang"] == "en" else "ko_KR",
            title=p["title"].replace('"', "&quot;"),
            desc=p["desc"].replace('"', "&quot;"),
            domain=DOMAIN, path=p["path"], alt=p["alt"],
            body=body,
        )

        dest = OUT / p["out"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        print(f"  {p['src']:28} → docs/{p["out"]:26} ({len(html):,}자)")

    # GitHub Pages 커스텀 도메인
    (OUT / "CNAME").write_text("mpuncture.org\n", encoding="utf-8")

    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")

    urls = "".join(
        f'  <url><loc>{DOMAIN}{p["path"]}</loc>'
        f'<xhtml:link rel="alternate" hreflang="{"ko" if p["lang"]=="en" else "en"}" '
        f'href="{DOMAIN}{p["alt"]}"/></url>\n'
        for p in PAGES)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n",
        encoding="utf-8")


    # ── 구 URL 리디렉션 (언어 구조 전환 전 주소) ──
    REDIRECTS = {"ko/index.html": "/", "ko/bacteria/index.html": "/bacteria/"}
    for src, dest in REDIRECTS.items():
        d = OUT / src
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_text(
            '<!doctype html>\n<html lang="ko">\n<head>\n'
            '<meta charset="utf-8">\n'
            f'<meta http-equiv="refresh" content="0; url={DOMAIN}{dest}">\n'
            f'<link rel="canonical" href="{DOMAIN}{dest}">\n'
            '<meta name="robots" content="noindex">\n'
            '<title>이동합니다 — M-puncture 엠펑쳐</title>\n</head>\n<body>\n'
            f'<p>이 주소는 <a href="{DOMAIN}{dest}">{DOMAIN}{dest}</a> 로 옮겨졌습니다.</p>\n'
            f'<script>location.replace("{dest}");</script>\n</body>\n</html>\n',
            encoding="utf-8")
    print(f"  구 URL 리디렉션 {len(REDIRECTS)}개 생성")

    # .nojekyll — Jekyll 처리 우회 (밑줄 시작 파일 등 안전)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    print("  CNAME / robots.txt / sitemap.xml / .nojekyll 생성")


if __name__ == "__main__":
    print("빌드 시작")
    build()
    print("완료 → docs/")
