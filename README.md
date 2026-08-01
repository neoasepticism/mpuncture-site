# mpuncture.org

만성통증을 신경회로의 문제로 보는 관점과 M-puncture 치료의 기록.
공공정보 사이트 — 특정 의료기관의 광고가 아님.

## 구조

| 경로 | 언어 | 소스 |
|---|---|---|
| `/` | English | `index-en.html` |
| `/bacteria/` | English | `decontamination-en.html` |
| `/ko/` | 한국어 | `index.html` |
| `/ko/bacteria/` | 한국어 | `decontamination.html` |

소스는 `<head>` 없는 본문 조각입니다. `build.py` 가 문서 골격·메타태그·hreflang 을
씌우고 내부 링크를 실제 경로로 바꿔 `docs/` 에 배포본을 만듭니다.

```
python3 build.py
```

GitHub Pages 는 `main` 브랜치의 `/docs` 를 서빙합니다.

편저 June-sang Yang
