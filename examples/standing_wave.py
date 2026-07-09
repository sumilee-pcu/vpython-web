# 정상파: 양끝은 고정되고 가운데가 크게 흔들린다.
points = []
for i in range(31):
    x = -4 + i * 8 / 30
    points.append(sphere(pos=vector(x, 0, 0), radius=0.075, color=color.orange))

t = 0
while True:
    rate(70)
    t = t + 0.08
    for i, p in enumerate(points):
        x = -4 + i * 8 / 30
        envelope = math.sin(pi * i / 30)
        p.pos = vector(x, 0.95 * envelope * math.cos(t), 0)
