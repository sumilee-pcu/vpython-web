# 자기장 격자 느낌: 회전하는 막대들이 공간의 방향장을 표현한다.
bars = []
for ix in range(7):
    for iy in range(5):
        bars.append(cylinder(pos=vector(-3 + ix, -2 + iy, 0), radius=0.025, color=color.green))

t = 0
while True:
    rate(40)
    t = t + 0.04
    for n, bar in enumerate(bars):
        ix = n % 7
        iy = n // 7
        a = t + 0.5 * ix - 0.35 * iy
        bar.axis = vector(0.5 * math.cos(a), 0.5 * math.sin(a), 0)
