# 회전하는 막대들: cylinder의 axis/pos 갱신 예제.
center = sphere(pos=vector(0, 0, 0), radius=0.18, color=color.white)
rods = []
tips = []

for i in range(6):
    rods.append(cylinder(radius=0.06, color=vector(1, 0.35 + 0.1 * i, 0.1)))
    tips.append(sphere(radius=0.14, color=color.yellow))

t = 0
while True:
    rate(70)
    t = t + 0.035
    for i in range(len(rods)):
        a = t + i * pi / 3
        end = vector(2.4 * math.cos(a), 1.1 * math.sin(2 * a), 2.4 * math.sin(a))
        rods[i].pos = center.pos
        rods[i].axis = end
        tips[i].pos = end
