# 진행파: 줄 위의 입자들이 위아래로 흔들리며 파동이 이동한다.
points = []
for i in range(28):
    x = -4 + i * 8 / 27
    points.append(sphere(pos=vector(x, 0, 0), radius=0.08, color=color.cyan))

baseline = cylinder(pos=vector(-4.2, 0, 0), axis=vector(8.4, 0, 0), radius=0.02, color=color.white, opacity=0.35)
t = 0
while True:
    rate(70)
    t = t + 0.08
    for i, p in enumerate(points):
        x = -4 + i * 8 / 27
        p.pos = vector(x, 0.75 * math.sin(2.3 * x - t), 0)
