import { Renderer } from './renderer.js';
import { EXAMPLES } from './examples.js';

const statusEl = document.getElementById('status');
const outputEl = document.getElementById('output');
const runBtn = document.getElementById('run');
const exampleSelect = document.getElementById('example-select');
const loadExampleBtn = document.getElementById('load-example');
const previewCanvas = document.getElementById('example-preview-canvas');
const previewTitle = document.getElementById('example-preview-title');
const previewDescription = document.getElementById('example-preview-description');

const renderer = new Renderer(document.getElementById('canvas-host'));
// Python 쪽(vpython.py)에서 `from js import vpw` 로 접근하는 브리지
globalThis.vpw = renderer;

const editor = CodeMirror.fromTextArea(document.getElementById('code'), {
  mode: 'python',
  theme: 'material-darker',
  lineNumbers: true,
  indentUnit: 4,
});
globalThis.vpwEditor = editor; // 자동 테스트용 훅

function status(msg) {
  statusEl.textContent = msg;
}

function print(text) {
  outputEl.textContent += text + '\n';
  outputEl.scrollTop = outputEl.scrollHeight;
}

// ---- 에러 표시: 사용자 코드 기준 줄번호 + 해당 줄 하이라이트 ----
let errorLine = null;

function clearError() {
  if (errorLine !== null) {
    editor.removeLineClass(errorLine, 'background', 'cm-error-line');
    errorLine = null;
  }
}

function showError(e) {
  const msg = String(e.message || e);
  console.error(msg); // 전체 트레이스백은 콘솔에
  const frames = [...msg.matchAll(/File "<exec>", line (\d+)/g)];
  const lines = msg.trimEnd().split('\n');
  const last = lines[lines.length - 1];
  if (frames.length) {
    const n = parseInt(frames[frames.length - 1][1], 10);
    print(`${n}행: ${last}`);
    if (n - 1 < editor.lineCount()) {
      errorLine = n - 1;
      editor.addLineClass(errorLine, 'background', 'cm-error-line');
    }
  } else {
    print(last);
  }
}

let pyodide = null;
let transformFn = null; // vpython.py의 _transform (tokenize 기반, 줄 수 보존)

function initExamples() {
  for (const [i, example] of EXAMPLES.entries()) {
    const option = document.createElement('option');
    option.value = String(i);
    option.textContent = `${example.category} · ${example.title}`;
    exampleSelect.appendChild(option);
  }
  renderExamplePreview(0);
}

async function loadExample(index = Number(exampleSelect.value || 0)) {
  const example = EXAMPLES[index];
  if (!example) return;
  exampleSelect.value = String(index);
  renderExamplePreview(index);
  exampleSelect.disabled = true;
  loadExampleBtn.disabled = true;
  try {
    const response = await fetch(example.path);
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    editor.setValue(await response.text());
    clearError();
    outputEl.textContent = '';
    status(`예제 로드: ${example.title}`);
  } catch (e) {
    print(`예제 로드 실패: ${example.title} (${e.message || e})`);
    status('예제 로드 실패');
  } finally {
    exampleSelect.disabled = false;
    loadExampleBtn.disabled = false;
  }
}

function renderExamplePreview(index = Number(exampleSelect.value || 0)) {
  const example = EXAMPLES[index];
  if (!example) return;
  previewTitle.textContent = `${example.title} · ${example.category} · ${example.difficulty}`;
  previewDescription.textContent = example.description;

  const ctx = previewCanvas.getContext('2d');
  const w = previewCanvas.width;
  const h = previewCanvas.height;
  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = '#0d1117';
  ctx.fillRect(0, 0, w, h);
  drawGrid(ctx, w, h);

  const line = (x1, y1, x2, y2, color, width = 4) => {
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  };
  const circle = (x, y, r, color) => {
    const g = ctx.createRadialGradient(x - r * 0.35, y - r * 0.4, r * 0.1, x, y, r);
    g.addColorStop(0, '#ffffff');
    g.addColorStop(0.18, color);
    g.addColorStop(1, '#111827');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  };

  if (example.preview === 'bounce') {
    line(40, 140, 260, 140, '#7cb342', 8);
    circle(150, 74, 24, '#ff9800');
    line(150, 100, 150, 132, '#ffcc80', 2);
  } else if (example.preview === 'orbit') {
    circle(150, 92, 24, '#fdd835');
    ctx.strokeStyle = '#607d8b';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.ellipse(150, 92, 96, 46, -0.2, 0, Math.PI * 2);
    ctx.stroke();
    circle(232, 56, 10, '#4dd0e1');
  } else if (example.preview === 'axes') {
    line(70, 120, 230, 120, '#ef5350', 8);
    line(70, 120, 70, 38, '#66bb6a', 8);
    line(70, 120, 144, 70, '#42a5f5', 8);
    circle(70, 120, 10, '#ffffff');
  } else if (example.preview === 'projectile') {
    line(30, 145, 270, 145, '#7cb342', 6);
    ctx.strokeStyle = '#4dd0e1';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(45, 132);
    ctx.quadraticCurveTo(145, 18, 255, 130);
    ctx.stroke();
    circle(92, 78, 13, '#ff9800');
  } else if (example.preview === 'gas') {
    ctx.strokeStyle = '#cfd8dc';
    ctx.lineWidth = 3;
    ctx.strokeRect(48, 34, 204, 112);
    for (let i = 0; i < 14; i++) {
      circle(62 + (i * 43) % 174, 48 + (i * 29) % 84, 6, i % 2 ? '#4dd0e1' : '#ffb74d');
    }
  } else if (example.preview === 'spring') {
    line(58, 44, 220, 44, '#8d6e63', 10);
    ctx.strokeStyle = '#cfd8dc';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(150, 44);
    for (let i = 0; i < 9; i++) ctx.lineTo(i % 2 ? 128 : 172, 54 + i * 9);
    ctx.lineTo(150, 142);
    ctx.stroke();
    circle(150, 148, 18, '#66bb6a');
  } else if (example.preview === 'pendulum') {
    const p0 = [150, 36], p1 = [116, 96], p2 = [184, 138];
    line(p0[0], p0[1], p1[0], p1[1], '#4dd0e1', 5);
    line(p1[0], p1[1], p2[0], p2[1], '#66bb6a', 5);
    circle(p0[0], p0[1], 8, '#ffffff');
    circle(p1[0], p1[1], 14, '#ff9800');
    circle(p2[0], p2[1], 18, '#ef5350');
  } else if (example.preview === 'rods') {
    circle(150, 90, 10, '#ffffff');
    for (let i = 0; i < 6; i++) {
      const a = i * Math.PI / 3;
      line(150, 90, 150 + Math.cos(a) * 82, 90 + Math.sin(a) * 48, '#ffb74d', 5);
    }
  } else if (example.preview === 'collision') {
    line(44, 128, 256, 128, '#cfd8dc', 5);
    circle(96, 106, 19, '#4dd0e1');
    circle(190, 106, 28, '#ff9800');
    line(124, 106, 156, 106, '#f5f5f5', 2);
  } else if (example.preview === 'solar') {
    circle(150, 90, 20, '#fdd835');
    for (const r of [44, 70, 96]) {
      ctx.strokeStyle = '#455a64';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.ellipse(150, 90, r, r * 0.45, 0, 0, Math.PI * 2);
      ctx.stroke();
    }
    circle(194, 90, 6, '#4dd0e1');
    circle(110, 62, 8, '#ff9800');
    circle(224, 122, 7, '#66bb6a');
  }
}

function drawGrid(ctx, w, h) {
  ctx.strokeStyle = 'rgba(255,255,255,0.06)';
  ctx.lineWidth = 1;
  for (let x = 20; x < w; x += 20) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h);
    ctx.stroke();
  }
  for (let y = 20; y < h; y += 20) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }
}

async function init() {
  initExamples();
  await loadExample(0);

  status('Pyodide 로딩 중... (첫 로딩은 수십 초 걸릴 수 있음)');
  pyodide = await loadPyodide({ indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/' });
  pyodide.setStdout({ batched: print });
  pyodide.setStderr({ batched: print });

  const src = await (await fetch('./src/vpython.py')).text();
  pyodide.runPython(src); // vpython API를 전역 네임스페이스에 등록
  transformFn = pyodide.globals.get('_transform');

  status('준비 완료');
  runBtn.disabled = false;
}

// Run은 실행 중에도 항상 클릭 가능해야 한다 (무한 루프 프로그램의 재실행 수단).
// runCounter로 "이 호출이 최신 실행인가"를 판별해 상태 표시 경합을 정리한다.
let runCounter = 0;

async function run() {
  const myRun = ++runCounter;
  outputEl.textContent = '';
  clearError();
  pyodide.runPython('_new_run()'); // 이전 실행 루프에 중단 신호 + dirty 초기화
  renderer.reset();

  const code = transformFn(editor.getValue());

  status('실행 중...');
  try {
    await pyodide.runPythonAsync(code);
    if (runCounter === myRun) {
      pyodide.runPython('_flush()'); // 루프 없이 끝나는 프로그램의 잔여 변경분 반영
      status('실행 완료');
    }
  } catch (e) {
    if (String(e).includes('_Stopped')) {
      // 이전 세대 루프의 정상 종료 — 조용히 무시
    } else if (runCounter === myRun) {
      showError(e);
      status('오류 발생');
    } else {
      console.error(e); // 교체된 실행의 에러는 콘솔로만
    }
  }
}

runBtn.addEventListener('click', run);
loadExampleBtn.addEventListener('click', () => loadExample());
exampleSelect.addEventListener('change', () => renderExamplePreview());
init();
