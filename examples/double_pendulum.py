# 이중 진자 모양의 결합 진동. 실제 동역학 대신 보기 좋은 위상 운동을 사용한다.
pivot = sphere(pos=vector(0, 2.2, 0), radius=0.16, color=color.white)
rod1 = cylinder(radius=0.045, color=color.cyan)
rod2 = cylinder(radius=0.045, color=color.green)
mass1 = sphere(radius=0.22, color=color.orange)
mass2 = sphere(radius=0.28, color=color.red)

L1 = 1.8
L2 = 1.5
t = 0

while True:
    rate(70)
    t = t + 0.035
    a1 = 0.85 * math.sin(t)
    a2 = 1.15 * math.sin(1.6 * t + 0.8)

    p1 = pivot.pos + vector(L1 * math.sin(a1), -L1 * math.cos(a1), 0)
    p2 = p1 + vector(L2 * math.sin(a2), -L2 * math.cos(a2), 0)

    rod1.pos = pivot.pos
    rod1.axis = p1 - pivot.pos
    rod2.pos = p1
    rod2.axis = p2 - p1
    mass1.pos = p1
    mass2.pos = p2
