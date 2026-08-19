// hwp/hwpx/hml → PDF (및 선택적 페이지별 PNG) 렌더링 (한컴 한글 불필요)
// 사용법:
//   node render.mjs <입력파일> [출력.pdf] [--png <폴더>] [--scale 1.5]
// 예:
//   node render.mjs 청구서.hwp                       → 청구서.pdf
//   node render.mjs 청구서.hwp 검수.pdf --png preview → 검수.pdf + preview/청구서_p1.png ...
import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import path from 'path';
import { loadRhwp, loadChromium, svgSize } from './lib.mjs';

const args = process.argv.slice(2);
if (!args.length) {
  console.error('사용법: node render.mjs <입력파일> [출력.pdf] [--png <폴더>] [--scale 1.5]');
  process.exit(1);
}
let pngDir = null, scale = 1.5;
const pIdx = args.indexOf('--png');
if (pIdx !== -1) { pngDir = args[pIdx + 1]; args.splice(pIdx, 2); }
const sIdx = args.indexOf('--scale');
if (sIdx !== -1) { scale = parseFloat(args[sIdx + 1]); args.splice(sIdx, 2); }
const input = args[0];
const base = path.basename(input, path.extname(input));
const output = args[1] || path.join(path.dirname(input), base + '.pdf');

const { HwpDocument, version } = await loadRhwp();
const doc = new HwpDocument(new Uint8Array(readFileSync(input)));
const pages = doc.pageCount();

const svgs = [];
let W, H;
for (let i = 0; i < pages; i++) {
  const s = doc.renderPageSvg(i);
  if (i === 0) ({ W, H } = svgSize(s));
  svgs.push(s);
}

const html = `<!doctype html><html><head><meta charset="utf-8"><style>
  @page{size:${W}px ${H}px;margin:0}
  html,body{margin:0;padding:0;background:#fff}
  .page{width:${W}px;height:${H}px;overflow:hidden;page-break-after:always}
  .page:last-child{page-break-after:auto}
  svg{display:block}
</style></head><body>${svgs.map(s => `<div class="page">${s}</div>`).join('')}</body></html>`;
const htmlPath = output.replace(/\.pdf$/i, '') + '.src.html';
writeFileSync(htmlPath, html);

const chromium = await loadChromium();
const browser = await chromium.launch();
const page = await browser.newPage({ deviceScaleFactor: scale });
await page.goto(pathToFileUrl(htmlPath), { waitUntil: 'networkidle' });
await page.pdf({ path: output, width: `${W}px`, height: `${H}px`, printBackground: true, pageRanges: `1-${pages}` });

let pngs = [];
if (pngDir) {
  mkdirSync(pngDir, { recursive: true });
  await page.setViewportSize({ width: Math.ceil(W), height: Math.ceil(H) });
  const handles = await page.$$('.page');
  for (let i = 0; i < handles.length; i++) {
    const out = path.join(pngDir, `${base}_p${i + 1}.png`);
    await handles[i].screenshot({ path: out });
    pngs.push(out);
  }
}
await browser.close();

console.log(JSON.stringify({ rhwp: version(), input, pages, pdf: output, pngs, ok: true }, null, 2));

function pathToFileUrl(p) {
  const abs = path.resolve(p);
  return 'file://' + (abs.startsWith('/') ? '' : '/') + abs;
}
