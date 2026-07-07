import { Renderer } from './renderer.js';

const statusEl = document.getElementById('status');
const outputEl = document.getElementById('output');
const runBtn = document.getElementById('run');

const renderer = new Renderer(document.getElementById('canvas-host'));
// Python 쪽(vpython.py)에서 `from js import vpw` 로 접근하는 브리지
globalThis.vpw = renderer;

const DEFAULT_CODE = `# 바닥에서 튀는 공 (VPython 고전 예제)
floor = box(pos=vector(0, -4, 0), size=vector(8, 0.4, 8), color=color.green)
ball = sphere(pos=vector(0, 3, 0), radius=0.7, color=color.orange)

ball.velocity = vector(0, 0, 0)
g = vector(0, -9.8, 0)
dt = 0.01

while True:
    rate(100)
    ball.velocity = ball.velocity + g * dt
    ball.pos = ball.pos + ball.velocity * dt
    if ball.pos.y < floor.pos.y + 0.2 + ball.radius:
        ball.velocity.y = abs(ball.velocity.y) * 0.98
`;

const editor = CodeMirror.fromTextArea(document.getElementById('code'), {
  mode: 'python',
  theme: 'material-darker',
  lineNumbers: true,
  indentUnit: 4,
});
editor.setValue(DEFAULT_CODE);
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

async function init() {
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
init();
