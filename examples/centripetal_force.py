# 구심력 느낌: 공은 원을 돌고, 안쪽 막대가 중심 방향을 가리킨다.
center = sphere(pos=vector(0, 0, 0), radius=0.16, color=color.white)
ball = sphere(radius=0.26, color=color.yellow)
radius_rod = cylinder(radius=0.04, color=color.cyan)
force_rod = cylinder(radius=0.07, color=color.red)

t = 0
while True:
    rate(70)
    t = t + 0.04
    ball.pos = vector(2.7 * math.cos(t), 1.1 * math.sin(0.5 * t), 2.7 * math.sin(t))
    radius_rod.pos = center.pos
    radius_rod.axis = ball.pos - center.pos
    force_rod.pos = ball.pos
    force_rod.axis = (center.pos - ball.pos).norm() * 0.85
