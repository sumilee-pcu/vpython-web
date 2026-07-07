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

function status(msg) {
  statusEl.textContent = msg;
}

function print(text) {
  outputEl.textContent += text + '\n';
  outputEl.scrollTop = outputEl.scrollHeight;
}

let pyodide = null;

async function init() {
  status('Pyodide 로딩 중... (첫 로딩은 수십 초 걸릴 수 있음)');
  pyodide = await loadPyodide({ indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/' });
  pyodide.setStdout({ batched: print });
  pyodide.setStderr({ batched: print });

  const src = await (await fetch('./src/vpython.py')).text();
  pyodide.runPython(src); // vpython API를 전역 네임스페이스에 등록

  status('준비 완료');
  runBtn.disabled = false;
}

async function run() {
  outputEl.textContent = '';
  pyodide.runPython('_new_run()'); // 이전 실행 루프에 중단 신호
  renderer.reset();

  // VPython의 블로킹 스타일 rate()를 브라우저에서 돌리기 위해 await로 변환
  let code = editor.getValue();
  code = code.replace(/\bawait\s+rate\(/g, 'rate(').replace(/\brate\(/g, 'await rate(');

  runBtn.disabled = true;
  status('실행 중...');
  try {
    await pyodide.runPythonAsync(code);
    status('실행 완료');
  } catch (e) {
    if (String(e).includes('_Stopped')) {
      status('이전 실행 중단됨');
    } else {
      print(String(e));
      status('오류 발생');
    }
  } finally {
    runBtn.disabled = false;
  }
}

runBtn.addEventListener('click', run);
init();
