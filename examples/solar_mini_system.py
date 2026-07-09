# 간단한 태양계: 여러 행성이 중심 질량을 공전한다.
sun = sphere(pos=vector(0, 0, 0), radius=0.65, color=color.yellow)

planets = []
for r, speed, radius, c in [
    (2.0, 1.15, 0.16, color.cyan),
    (3.1, 0.72, 0.22, color.orange),
    (4.4, 0.48, 0.18, color.green),
]:
    p = sphere(pos=vector(r, 0, 0), radius=radius, color=c)
    p.r = r
    p.speed = speed
    p.angle = r
    planets.append(p)

while True:
    rate(60)
    for p in planets:
        p.angle = p.angle + p.speed * 0.025
        p.pos = vector(p.r * math.cos(p.angle), 0, p.r * math.sin(p.angle))
