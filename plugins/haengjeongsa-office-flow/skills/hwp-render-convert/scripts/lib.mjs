// 행정사사무소 - hwp-render-convert 공용 로더
// @rhwp/core(WASM)와 playwright(전역/로컬 무관)를 견고하게 로드한다.
import { readFileSync } from 'fs';
import { execSync } from 'child_process';
import { createRequire } from 'module';
import { pathToFileURL } from 'url';
import path from 'path';

const require = createRequire(import.meta.url);

// --- @rhwp/core 초기화 -------------------------------------------------------
export async function loadRhwp() {
  let corePkgJson;
  try {
    corePkgJson = require.resolve('@rhwp/core/package.json');
  } catch {
    throw new Error('@rhwp/core 미설치. 먼저 scripts/setup.sh 를 실행하세요.');
  }
  const coreDir = path.dirname(corePkgJson);
  const mod = await import(pathToFileURL(path.join(coreDir, 'rhwp.js')).href);
  const wasm = readFileSync(path.join(coreDir, 'rhwp_bg.wasm'));
  await mod.default({ module_or_path: wasm });
  return mod; // { HwpDocument, HwpViewer, version, ... }
}

// --- playwright(chromium) 로드 : 로컬 → 전역 순으로 탐색 ----------------------
export async function loadChromium() {
  const pick = (m) => m?.chromium ?? m?.default?.chromium; // CJS/ESM interop 대응
  try {
    const c = pick(await import('playwright'));
    if (c) return c;
  } catch {}
  // 전역 node_modules 경로에서 재시도
  try {
    const groot = execSync('npm root -g', { encoding: 'utf8' }).trim();
    const c = pick(await import(pathToFileURL(path.join(groot, 'playwright', 'index.js')).href));
    if (c) return c;
  } catch {}
  throw new Error('playwright(chromium) 로드 실패. scripts/setup.sh 실행 또는 `npm i playwright` 필요.');
}

// SVG 루트에서 페이지 px 크기 추출(기본 A4 96dpi)
export function svgSize(svg) {
  const m = svg.match(/width="([\d.]+)"\s+height="([\d.]+)"/);
  return m ? { W: +m[1], H: +m[2] } : { W: 793.7066666666667, H: 1122.5066666666667 };
}
