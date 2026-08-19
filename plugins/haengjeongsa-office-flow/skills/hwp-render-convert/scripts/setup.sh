#!/usr/bin/env bash
# 행정사사무소 - hwp-render-convert 환경 준비
# @rhwp/core(WASM 파서·렌더러)와 playwright(chromium)를 준비한다.
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "[1/3] @rhwp/core 설치 확인"
node -e "require.resolve('@rhwp/core/package.json')" 2>/dev/null \
  || npm install @rhwp/core >/dev/null 2>&1
echo "      @rhwp/core: $(node -e "console.log(require('@rhwp/core/package.json').version)" 2>/dev/null || echo '설치실패')"

echo "[2/3] playwright(chromium) 확인"
# 렌더링(PDF/PNG)에만 필요. 로컬 → 전역 순으로 존재하면 통과.
if node -e "require.resolve('playwright')" 2>/dev/null; then
  echo "      playwright: 로컬 존재"
elif [ -d "$(npm root -g)/playwright" ]; then
  echo "      playwright: 전역 존재"
else
  echo "      playwright 설치 시도(기존 chromium 재사용, 재다운로드 안 함)"
  PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install playwright >/dev/null 2>&1 || true
fi

echo "[3/3] (선택) 한국어 폰트 확인"
# 렌더링 글꼴 대체용. Noto CJK KR 있으면 충분.
fc-list 2>/dev/null | grep -iq "Noto Sans CJK KR" \
  && echo "      Noto CJK KR: 있음" \
  || echo "      Noto CJK KR 없음 → 필요시: apt-get install -y fonts-noto-cjk fonts-nanum"

echo "준비 완료."
