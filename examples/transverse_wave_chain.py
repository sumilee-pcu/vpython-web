# 횡파 줄: 이웃 입자를 cylinder로 이어 줄처럼 보이게 한다.
points = []
links = []
for i in range(22):
    x = -4 + i * 8 / 21
    points.append(sphere(pos=vector(x, 0, 0), radius=0.07, color=color.cyan))
for i in range(21):
    links.append(cylinder(radius=0.025, color=color.white, opacity=0.65))

t = 0
while True:
    rate(60)
    t = t + 0.08
    for i, p in enumerate(points):
        x = -4 + i * 8 / 21
        p.pos = vector(x, 0.55 * math.sin(2.4 * x - t), 0)
    for i, link in enumerate(links):
        link.pos = points[i].pos
        link.axis = points[i + 1].pos - points[i].pos
