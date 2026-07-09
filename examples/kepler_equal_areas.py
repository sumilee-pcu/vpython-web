# 케플러 제2법칙 느낌: 가까울수록 빠르게 움직이는 타원 궤도.
sun = sphere(pos=vector(-0.7, 0, 0), radius=0.35, color=color.yellow)
planet = sphere(radius=0.18, color=color.cyan)
markers = [sphere(radius=0.035, color=color.white, opacity=0.45) for i in range(36)]

t = 0
while True:
    rate(60)
    t = t + 0.018
    # 균일하지 않은 각도 증가를 흉내낸다.
    a = t + 0.45 * math.sin(t)
    planet.pos = vector(2.8 * math.cos(a) - 0.7, 0, 1.35 * math.sin(a))
    markers[int(t * 6) % len(markers)].pos = planet.pos
