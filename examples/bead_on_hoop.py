# 원형 고리 위의 구슬: 고리를 점으로 그리고 구슬이 따라 움직인다.
hoop = []
for i in range(48):
    a = 2 * pi * i / 48
    hoop.append(sphere(pos=vector(0, 2.1 * math.cos(a), 2.1 * math.sin(a)),
                       radius=0.035, color=color.gray(0.7), opacity=0.6))
bead = sphere(radius=0.22, color=color.orange)

t = 0
while True:
    rate(70)
    t = t + 0.035
    a = 1.2 * math.sin(t)
    bead.pos = vector(0, 2.1 * math.cos(a), 2.1 * math.sin(a))
