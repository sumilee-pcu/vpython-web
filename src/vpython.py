# vpython-web: 브라우저(Pyodide)에서 실행되는 VPython API 계층.
# 3D 렌더링은 JS 쪽 three.js 렌더러(globalThis.vpw)에 위임한다.
import asyncio
import json
import math

from js import vpw

# ---------------------------------------------------------------- 실행 제어
# Run 버튼을 다시 누르면 세대(generation)가 올라가고,
# 이전 실행의 while 루프는 다음 rate() 호출에서 _Stopped 로 종료된다.
_generation = 0


class _Stopped(Exception):
    pass


def _new_run():
    global _generation
    _generation += 1


async def rate(n):
    g = _generation
    await asyncio.sleep(1.0 / n)
    if g != _generation:
        raise _Stopped()


# ---------------------------------------------------------------- vector
class vector:
    __slots__ = ("x", "y", "z")

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

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
        return f"<{self.x}, {self.y}, {self.z}>"


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


def _encode(d):
    return {k: _encode_val(v) for k, v in d.items()}


class _Object3D:
    # 렌더러와 동기화되는 속성. 그 외(velocity 등)는 자유 속성으로 허용.
    _known = ("pos", "color", "opacity", "size", "radius", "visible")

    def __init__(self, _type, defaults, kw):
        props = dict(defaults)
        for k in list(kw):
            if k in self._known:
                props[k] = kw.pop(k)
        object.__setattr__(self, "_props", props)
        object.__setattr__(self, "_id", vpw.createObject(_type, json.dumps(_encode(props))))
        for k, v in kw.items():
            object.__setattr__(self, k, v)

    def __getattr__(self, name):
        props = object.__getattribute__(self, "_props")
        if name in props:
            return props[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self._known:
            self._props[name] = value
            vpw.updateObject(self._id, json.dumps({name: _encode_val(value)}))
        else:
            object.__setattr__(self, name, value)


def box(**kw):
    defaults = {"pos": vector(0, 0, 0), "size": vector(1, 1, 1),
                "color": color.white, "opacity": 1.0, "visible": True}
    return _Object3D("box", defaults, kw)


def sphere(**kw):
    defaults = {"pos": vector(0, 0, 0), "radius": 1.0,
                "color": color.white, "opacity": 1.0, "visible": True}
    return _Object3D("sphere", defaults, kw)


# ---------------------------------------------------------------- scene (스텁)
# GlowScript의 scene 객체 흉내. 아직 미구현 속성은 조용히 무시한다.
class _Scene:
    def __setattr__(self, name, value):
        pass

    def __getattr__(self, name):
        return None


scene = _Scene()

pi = math.pi
