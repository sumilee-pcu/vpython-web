# 태양 주위를 도는 행성 (중력 시뮬레이션)
sun = sphere(pos=vector(0, 0, 0), radius=1.2, color=color.yellow)
planet = sphere(pos=vector(6, 0, 0), radius=0.4, color=color.cyan)

planet.velocity = vector(0, 0, 5.5)
GM = 200
dt = 0.005

while True:
    rate(200)
    r = planet.pos - sun.pos
    a = -GM / r.mag2 * r.norm()
    planet.velocity = planet.velocity + a * dt
    planet.pos = planet.pos + planet.velocity * dt
