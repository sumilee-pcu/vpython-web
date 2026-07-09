# 포물선 운동: 작은 점들이 최근 궤적을 따라간다.
floor = box(pos=vector(0, -2, 0), size=vector(14, 0.12, 4), color=color.green, opacity=0.45)
ball = sphere(pos=vector(-6, -1.6, 0), radius=0.22, color=color.orange)

trail = []
for i in range(42):
    trail.append(sphere(pos=ball.pos, radius=0.035, color=color.cyan, opacity=0.35))

ball.velocity = vector(7.5, 7.2, 0)
g = vector(0, -9.8, 0)
dt = 0.012
t = 0

while True:
    rate(80)
    ball.velocity = ball.velocity + g * dt
    ball.pos = ball.pos + ball.velocity * dt

    t = t + 1
    if t % 2 == 0:
        trail[(t // 2) % len(trail)].pos = ball.pos

    if ball.pos.y < -1.75 or ball.pos.x > 6.5:
        ball.pos = vector(-6, -1.6, 0)
        ball.velocity = vector(7.5, 7.2, 0)
        for p in trail:
            p.pos = ball.pos
