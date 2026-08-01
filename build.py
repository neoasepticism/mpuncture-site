#!/usr/bin/env python3
"""
mpuncture.org 배포본 빌드

소스(Artifact 형식, head 없음) → site/ (완전한 HTML 문서)

구조:
  /                    영문 랜딩      ← index-en.html
  /bacteria/           영문 심화      ← decontamination-en.html
  /ko/                 한국어 랜딩    ← index.html
  /ko/bacteria/        한국어 심화    ← decontamination.html
"""
import re, shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
DOMAIN = "https://mpuncture.org"

# 아티팩트 URL → 실제 경로
ARTIFACT_MAP = {
    "https://claude.ai/code/artifact/67bfbe57-5a3d-4945-b3a9-e2e29a20df6b": "/",              # EN landing
    "https://claude.ai/code/artifact/2e4438eb-c097-4489-8cbf-d0d5aec8f75e": "/bacteria/",     # EN deep
    "https://claude.ai/code/artifact/af31d28f-8c55-4a8c-bdff-beafca8d4cc6": "/ko/",           # KO landing
    "https://claude.ai/code/artifact/836a590c-62fc-4591-9129-ff6dad3d77bf": "/ko/bacteria/",  # KO deep
}

PAGES = [
    dict(src="index-en.html",           out="index.html",             lang="en", path="/",
         title="M-puncture — Chronic Pain as a Problem of the Nerve Circuit",
         desc="Chronic pain understood as a problem of the nerve circuit: the M-puncture approach, "
              "a bacterial second axis, and a practical record for physicians.",
         alt="/ko/"),
    dict(src="decontamination-en.html", out="bacteria/index.html",    lang="en", path="/bacteria/",
         title="Bacteria and Chronic Pain — In the Gut, and in the Tissue",
         desc="Gut-derived input and tissue-resident organisms as drivers of chronic musculoskeletal "
              "pain — the established entities, the mechanisms, and what remains unresolved.",
         alt="/ko/bacteria/"),
    dict(src="index.html",              out="ko/index.html",          lang="ko", path="/ko/",
         title="M-puncture — 만성통증을 신경회로로 보는 관점",
         desc="만성통증을 조직이 아니라 신경회로의 문제로 보는 관점과, 그 위에 세워진 M-puncture 치료의 기록. "
              "환자와 의사를 위한 공공정보 아카이브.",
         alt="/"),
    dict(src="decontamination.html",    out="ko/bacteria/index.html", lang="ko", path="/ko/bacteria/",
         title="세균과 만성통증 — 장에서, 그리고 조직에서",
         desc="장에서 오는 자극과 조직에 정착한 세균이 만성 근골격 통증을 유지시키는 경로 — "
              "확립된 질환, 기전, 그리고 아직 확인되지 않은 것.",
         alt="/bacteria/"),
]

SKELETON = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="June-sang Yang">
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

    # .nojekyll — Jekyll 처리 우회 (밑줄 시작 파일 등 안전)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    print("  CNAME / robots.txt / sitemap.xml / .nojekyll 생성")


if __name__ == "__main__":
    print("빌드 시작")
    build()
    print("완료 → docs/")
