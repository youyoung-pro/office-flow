// hwp/hwpx/hml 상호 변환 (한컴 한글 불필요)
// 사용법:
//   node convert.mjs <입력파일> [출력파일] [--to hwpx|hwp|hml]
// 예:
//   node convert.mjs 청구서.hwp                → 청구서.hwpx
//   node convert.mjs 청구서.hwp out.hwpx --to hwpx
import { readFileSync, writeFileSync } from 'fs';
import path from 'path';
import { loadRhwp } from './lib.mjs';

const args = process.argv.slice(2);
if (!args.length) {
  console.error('사용법: node convert.mjs <입력파일> [출력파일] [--to hwpx|hwp|hml]');
  process.exit(1);
}
let to = 'hwpx';
const toIdx = args.indexOf('--to');
if (toIdx !== -1) { to = args[toIdx + 1]; args.splice(toIdx, 2); }
const input = args[0];
const output = args[1] || path.join(path.dirname(input), path.basename(input, path.extname(input)) + '.' + to);

const { HwpDocument, version } = await loadRhwp();
const buf = new Uint8Array(readFileSync(input));
const doc = new HwpDocument(buf);

let bytes;
if (to === 'hwpx') bytes = doc.exportHwpx();
else if (to === 'hwp') bytes = doc.exportHwp();
else if (to === 'hml') bytes = doc.exportHml();
else { console.error('지원 형식: hwpx | hwp | hml'); process.exit(1); }

writeFileSync(output, Buffer.from(bytes));

// 자체 검증: 변환본을 다시 로드해 페이지 수 확인
let reloadPages = null, reloadErr = null;
try { reloadPages = new HwpDocument(new Uint8Array(bytes)).pageCount(); }
catch (e) { reloadErr = e.message || String(e); }

console.log(JSON.stringify({
  rhwp: version(), input, output, to,
  inPages: doc.pageCount(), outBytes: bytes.length,
  reloadPages, reloadErr, ok: reloadErr === null
}, null, 2));
