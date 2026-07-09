# 트랙 위 구슬: 굴러가는 느낌을 위해 작은 표시점이 공 주위를 돈다.
track = cylinder(pos=vector(-4, -0.75, 0), axis=vector(8, 0, 0), radius=0.04, color=color.white)
ball = sphere(radius=0.35, color=color.orange)
mark = sphere(radius=0.08, color=color.black)

t = 0
while True:
    rate(70)
    t = t + 0.04
    x = -3.5 + (t * 1.1) % 7
    ball.pos = vector(x, 0, 0)
    mark.pos = ball.pos + vector(0, 0.35 * math.cos(4 * t), 0.35 * math.sin(4 * t))
