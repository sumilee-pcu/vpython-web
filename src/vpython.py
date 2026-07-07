# vpython-web: 브라우저(Pyodide)에서 실행되는 VPython API 계층.
# 3D 렌더링은 JS 쪽 three.js 렌더러(globalThis.vpw)에 위임한다.
# 브리지 프로토콜 v2(배칭): 속성 변경은 _dirty에 쌓이고 rate()/_flush()에서 일괄 전송.
import asyncio
import io
import json
import math
import tokenize

from js import vpw

# ---------------------------------------------------------------- 실행 제어
# Run 버튼을 다시 누르면 세대(generation)가 올라가고,
# 이전 실행의 while 루프는 다음 rate() 호출에서 _Stopped 로 종료된다.
_generation = 0
_dirty = {}  # {obj_id: {prop: 최신값}} — rate()/_flush()에서 일괄 전송


class _Stopped(Exception):
    pass


def _new_run():
    global _generation, _dirty
    _generation += 1
    _dirty = {}


def _flush():
    global _dirty
    if not _dirty:
        return
    batch = {str(oid): {k: _encode_val(v) for k, v in props.items()}
             for oid, props in _dirty.items()}
    _dirty = {}
    vpw.applyUpdates(json.dumps(batch))


async def rate(n):
    _flush()
    g = _generation
    await asyncio.sleep(1.0 / n)
    if g != _generation:
        raise _Stopped()


# ---------------------------------------------------------------- 코드 변환
# rate(...) 호출 앞에 await를 삽입한다 (줄 수 보존 — 에러 줄번호 유지에 필수).
# tokenize 기반이라 문자열/주석 안의 rate( 는 건드리지 않는다.
_ASYNC_CALLS = ("rate",)  # Phase 4에서 sleep, scene.pause 등 추가 예정
_TRIVIA = (tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT,
           tokenize.INDENT, tokenize.DEDENT)


def _transform(code):
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except Exception:
        return code  # 문법 오류는 실행 시점에 그대로 드러나게 둔다
    insertions = []
    prev = None
    for i, tok in enumerate(tokens):
        if tok.type == tokenize.NAME and tok.string in _ASYNC_CALLS:
            nxt = next((t for t in tokens[i + 1:] if t.type not in _TRIVIA), None)
            if nxt is not None and nxt.type == tokenize.OP and nxt.string == "(":
                skip = prev is not None and (
                    (prev.type == tokenize.NAME and prev.string in ("await", "def"))
                    or (prev.type == tokenize.OP and prev.string == ".")
                )
                if not skip:
                    insertions.append(tok.start)
        if tok.type not in _TRIVIA:
            prev = tok
    if not insertions:
        return code
    lines = code.split("\n")
    for row, col in sorted(insertions, reverse=True):
        line = lines[row - 1]
        lines[row - 1] = line[:col] + "await " + line[col:]
    return "\n".join(lines)


# ---------------------------------------------------------------- vector
class vector:
    # _owner/_attr: 이 벡터가 3D 객체의 동기화 속성(pos 등)에 바인딩된 경우,
    # 성분(x/y/z) 수정 시 소유자에게 dirty 마킹을 전달한다.
    __slots__ = ("x", "y", "z", "_owner", "_attr")

    def __init__(self, x=0.0, y=0.0, z=0.0):
        if isinstance(x, vector):  # 복사 생성자
            x, y, z = x.x, x.y, x.z
        _set = object.__setattr__
        _set(self, "x", float(x))
        _set(self, "y", float(y))
        _set(self, "z", float(z))
        _set(self, "_owner", None)
        _set(self, "_attr", None)

    def __setattr__(self, name, value):
        if name in ("x", "y", "z"):
            object.__setattr__(self, name, float(value))
            owner = self._owner
            if owner is not None:
                owner._mark_dirty(self._attr)
        else:
            object.__setattr__(self, name, value)

    def __add__(self, o):
        return vector(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o):
        return vector(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, s):
        return vector(self.x * s, self.y * s, self.z * s)

    __rmul__ = __mul__

    def __truediv__(self, s):
        return vector(self.x / s, self.y / s, self.z / s)

    def __neg__(self):
        return vector(-self.x, -self.y, -self.z)

    def __eq__(self, o):
        return isinstance(o, vector) and (self.x, self.y, self.z) == (o.x, o.y, o.z)

    @property
    def mag(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    @property
    def mag2(self):
        return self.x * self.x + self.y * self.y + self.z * self.z

    def norm(self):
        m = self.mag
        return self / m if m > 0 else vector(0, 0, 0)

    def dot(self, o):
        return self.x * o.x + self.y * o.y + self.z * o.z

    def cross(self, o):
        return vector(
            self.y * o.z - self.z * o.y,
            self.z * o.x - self.x * o.z,
            self.x * o.y - self.y * o.x,
        )

    def _tolist(self):
        return [self.x, self.y, self.z]

    def __repr__(self):
        return f"<{self.x:g}, {self.y:g}, {self.z:g}>"


def mag(v):
    return v.mag


def mag2(v):
    return v.mag2


def norm(v):
    return v.norm()


def dot(a, b):
    return a.dot(b)


def cross(a, b):
    return a.cross(b)


# ---------------------------------------------------------------- color
class color:
    red = vector(1, 0, 0)
    green = vector(0, 1, 0)
    blue = vector(0, 0, 1)
    yellow = vector(1, 1, 0)
    orange = vector(1, 0.6, 0)
    cyan = vector(0, 1, 1)
    magenta = vector(1, 0, 1)
    purple = vector(0.4, 0.2, 0.6)
    white = vector(1, 1, 1)
    black = vector(0, 0, 0)

    @staticmethod
    def gray(luminance):
        return vector(luminance, luminance, luminance)


# ---------------------------------------------------------------- 3D 객체
def _encode_val(v):
    return v._tolist() if isinstance(v, vector) else v


_SIZE_ALIASES = {"length": "x", "height": "y", "width": "z"}


class _Object3D:
    # 렌더러와 동기화되는 속성. 그 외(velocity 등)는 자유 속성으로 허용.
    # 성능: 동기화 속성도 실제 인스턴스 속성으로 저장한다 (읽기가 __getattr__
    # 예외 경로를 타지 않도록 — b.pos 읽기는 물리 루프에서 가장 빈번한 연산).
    _known = frozenset(("pos", "axis", "up", "color", "opacity", "size", "radius", "visible"))

    def __init__(self, _type, defaults, kw, coupled=False):
        # coupled=True(box 계열): size.x == mag(axis) 를 항상 유지
        _set = object.__setattr__
        _set(self, "_coupling", False)
        _set(self, "_coupled", coupled)
        props = {k: (vector(v) if isinstance(v, vector) else v)
                 for k, v in defaults.items()}  # 기본값 공유 방지 복사

        alias_given = False
        if "size" in props:
            for alias, comp in _SIZE_ALIASES.items():
                if alias in kw:
                    object.__setattr__(props["size"], comp, float(kw.pop(alias)))
                    alias_given = True
        axis_given = "axis" in kw
        size_given = "size" in kw or alias_given
        for k in list(kw):
            if k in self._known:
                props[k] = kw.pop(k)

        if coupled:
            axis, size = props["axis"], props["size"]
            if axis_given:
                object.__setattr__(size, "x", axis.mag)
            elif size_given:
                n = axis.norm()
                if n.mag == 0:
                    n = vector(1, 0, 0)
                props["axis"] = n * size.x

        _set(self, "_sync_keys", tuple(props))  # 이 객체가 렌더러와 동기화하는 속성 목록
        for k, v in props.items():
            _set(self, k, self._bind(k, v) if isinstance(v, vector) else v)

        _flush()  # 생성 순서와 이전 업데이트 순서가 꼬이지 않게
        _set(self, "_id", vpw.createObject(
            _type, json.dumps({k: _encode_val(getattr(self, k)) for k in self._sync_keys})))

        for k, v in kw.items():  # 자유 속성 (velocity, mass 등)
            _set(self, k, v)

    def _bind(self, name, value):
        # 대입은 복사 시맨틱: 같은 vector를 두 객체에 대입해도 서로 간섭하지 않는다
        v = vector(value)
        object.__setattr__(v, "_owner", self)
        object.__setattr__(v, "_attr", name)
        return v

    def __getattr__(self, name):
        # 동기화 속성은 실제 인스턴스 속성이라 여기 오지 않는다. 별칭만 처리.
        if name in _SIZE_ALIASES:
            try:
                size = object.__getattribute__(self, "size")
            except AttributeError:
                raise AttributeError(name) from None
            return getattr(size, _SIZE_ALIASES[name])
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self._known:
            if isinstance(value, vector):
                value = self._bind(name, value)
            object.__setattr__(self, name, value)
            self._mark_dirty(name)
        elif name in _SIZE_ALIASES and hasattr(self, "size"):
            # b.length = 4 → size.x 성분 대입 (성분 셋이 dirty + axis 결합까지 처리)
            setattr(self.size, _SIZE_ALIASES[name], float(value))
        else:
            object.__setattr__(self, name, value)

    def _mark_dirty(self, name):
        d = _dirty.get(self._id)
        if d is None:
            d = _dirty[self._id] = {}
        d[name] = getattr(self, name)
        if self._coupled and not self._coupling and (name == "axis" or name == "size"):
            object.__setattr__(self, "_coupling", True)
            try:
                axis, size = self.axis, self.size
                if name == "axis":
                    m = axis.mag
                    if abs(size.x - m) > 1e-12:
                        size.x = m  # 성분 셋 → dirty 마킹 (결합은 _coupling으로 재진입 차단)
                else:
                    length = size.x
                    if abs(axis.mag - length) > 1e-12:
                        n = axis.norm()
                        if n.mag == 0:
                            n = vector(1, 0, 0)
                        t = n * length
                        axis.x, axis.y, axis.z = t.x, t.y, t.z
            finally:
                object.__setattr__(self, "_coupling", False)


def box(**kw):
    defaults = {"pos": vector(0, 0, 0), "axis": vector(1, 0, 0), "up": vector(0, 1, 0),
                "size": vector(1, 1, 1), "color": color.white,
                "opacity": 1.0, "visible": True}
    return _Object3D("box", defaults, kw, coupled=True)


def sphere(**kw):
    defaults = {"pos": vector(0, 0, 0), "axis": vector(1, 0, 0), "up": vector(0, 1, 0),
                "radius": 1.0, "color": color.white,
                "opacity": 1.0, "visible": True}
    return _Object3D("sphere", defaults, kw)


# ---------------------------------------------------------------- scene (스텁)
# GlowScript의 scene 객체 흉내. 아직 미구현 속성은 조용히 무시한다. (Phase 4에서 구현)
class _Scene:
    def __setattr__(self, name, value):
        pass

    def __getattr__(self, name):
        return None


scene = _Scene()

pi = math.pi
