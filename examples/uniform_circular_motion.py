# 등속 원운동: 위치와 반지름 막대가 일정한 각속도로 회전한다.
center = sphere(pos=vector(0, 0, 0), radius=0.12, color=color.white)
radius_rod = cylinder(radius=0.045, color=color.cyan)
ball = sphere(radius=0.28, color=color.orange)

ring_points = []
for i in range(36):
    a = 2 * pi * i / 36
    ring_points.append(sphere(pos=vector(2.5 * math.cos(a), 0, 2.5 * math.sin(a)),
                              radius=0.035, color=color.gray(0.65), opacity=0.55))

t = 0
while True:
    rate(70)
    t = t + 0.035
    ball.pos = vector(2.5 * math.cos(t), 0, 2.5 * math.sin(t))
    radius_rod.pos = center.pos
    radius_rod.axis = ball.pos - center.pos
