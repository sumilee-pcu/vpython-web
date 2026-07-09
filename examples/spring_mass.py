# 스프링-질량 진동: cylinder 여러 개로 지그재그 스프링을 표현.
anchor = sphere(pos=vector(-4, 0, 0), radius=0.18, color=color.white)
wall = box(pos=vector(-4.25, 0, 0), size=vector(0.18, 2.4, 2.4), color=color.gray(0.45))
mass = sphere(pos=vector(2, 0, 0), radius=0.45, color=color.orange)

segments = []
for i in range(16):
    segments.append(cylinder(radius=0.04, color=color.cyan))

def spring_point(i, n, start, end):
    s = i / n
    x = start.x * (1 - s) + end.x * s
    y = 0.35 if i % 2 == 1 else -0.35
    if i == 0 or i == n:
        y = 0
    return vector(x, y, 0)

def update_spring(start, end):
    n = len(segments)
    prev = spring_point(0, n, start, end)
    for i in range(n):
        nxt = spring_point(i + 1, n, start, end)
        segments[i].pos = prev
        segments[i].axis = nxt - prev
        prev = nxt

t = 0
while True:
    rate(60)
    t = t + 0.045
    mass.pos.x = 1.6 + 1.0 * math.sin(t)
    update_spring(anchor.pos, mass.pos)
