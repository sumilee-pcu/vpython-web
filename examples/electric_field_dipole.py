# 전기 쌍극자 느낌: +전하와 -전하 주변의 방향 막대.
plus = sphere(pos=vector(-1.2, 0, 0), radius=0.3, color=color.red)
minus = sphere(pos=vector(1.2, 0, 0), radius=0.3, color=color.blue)
bars = []
for i in range(18):
    bars.append(cylinder(radius=0.025, color=color.cyan, opacity=0.65))

t = 0
while True:
    rate(30)
    t = t + 0.03
    for i, bar in enumerate(bars):
        a = 2 * pi * i / len(bars)
        p = vector(2.6 * math.cos(a), 1.4 * math.sin(a), 0)
        direction = (p - plus.pos).norm() - (p - minus.pos).norm()
        bar.pos = p - direction.norm() * 0.22
        bar.axis = direction.norm() * 0.44
