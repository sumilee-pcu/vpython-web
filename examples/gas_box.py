# 기체 입자 상자: 벽과 입자의 탄성 충돌.
import random

box(pos=vector(0, -2, 0), size=vector(8, 0.08, 4), color=color.white, opacity=0.18)
box(pos=vector(0, 2, 0), size=vector(8, 0.08, 4), color=color.white, opacity=0.18)
box(pos=vector(-4, 0, 0), size=vector(0.08, 4, 4), color=color.white, opacity=0.18)
box(pos=vector(4, 0, 0), size=vector(0.08, 4, 4), color=color.white, opacity=0.18)
box(pos=vector(0, 0, -2), size=vector(8, 4, 0.08), color=color.white, opacity=0.12)

balls = []
for i in range(18):
    p = vector(random.uniform(-3.2, 3.2), random.uniform(-1.4, 1.4), random.uniform(-1.2, 1.2))
    b = sphere(pos=p, radius=0.14, color=vector(random.random(), 0.65, 1))
    b.velocity = vector(random.uniform(-2.2, 2.2), random.uniform(-2.2, 2.2), random.uniform(-1.8, 1.8))
    balls.append(b)

dt = 0.018
while True:
    rate(60)
    for b in balls:
        b.pos = b.pos + b.velocity * dt
        if b.pos.x < -3.85 or b.pos.x > 3.85:
            b.velocity.x = -b.velocity.x
        if b.pos.y < -1.85 or b.pos.y > 1.85:
            b.velocity.y = -b.velocity.y
        if b.pos.z < -1.85 or b.pos.z > 1.85:
            b.velocity.z = -b.velocity.z
