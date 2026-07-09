# 빗면 운동: 공이 경사면을 따라 내려간 뒤 처음으로 돌아간다.
plane = box(pos=vector(0, -1.1, 0), size=vector(7, 0.14, 2.2), axis=vector(6, -2.2, 0), color=color.green, opacity=0.55)
ball = sphere(radius=0.28, color=color.orange)

start = vector(-3, 1.0, 0)
direction = vector(6, -2.2, 0).norm()
s = 0
v = 0
dt = 0.018

while True:
    rate(70)
    v = v + 1.6 * dt
    s = s + v * dt
    ball.pos = start + direction * s + vector(0, 0.33, 0)
    if s > 6.1:
        s = 0
        v = 0
