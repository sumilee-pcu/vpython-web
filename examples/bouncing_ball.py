# 바닥에서 튀는 공 (VPython 고전 예제)
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
