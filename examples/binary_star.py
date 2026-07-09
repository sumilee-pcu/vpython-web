# 쌍성계: 두 별과 작은 행성이 함께 도는 장면.
star1 = sphere(radius=0.42, color=color.yellow)
star2 = sphere(radius=0.36, color=color.orange)
planet = sphere(radius=0.16, color=color.cyan)
link = cylinder(radius=0.025, color=color.white, opacity=0.35)

t = 0
while True:
    rate(60)
    t = t + 0.025
    star1.pos = vector(0.9 * math.cos(t), 0, 0.9 * math.sin(t))
    star2.pos = vector(-1.1 * math.cos(t), 0, -1.1 * math.sin(t))
    planet.pos = vector(3.2 * math.cos(0.55 * t), 0, 3.2 * math.sin(0.55 * t))
    link.pos = star1.pos
    link.axis = star2.pos - star1.pos
