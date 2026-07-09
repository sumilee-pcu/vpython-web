# 두 물체 중력: 서로의 질량 중심 주위를 공전한다.
a = sphere(radius=0.35, color=color.cyan)
b = sphere(radius=0.55, color=color.orange)
rod = cylinder(radius=0.025, color=color.white, opacity=0.5)

t = 0
while True:
    rate(70)
    t = t + 0.035
    a.pos = vector(1.8 * math.cos(t), 0, 1.8 * math.sin(t))
    b.pos = vector(-1.1 * math.cos(t), 0, -1.1 * math.sin(t))
    rod.pos = a.pos
    rod.axis = b.pos - a.pos
