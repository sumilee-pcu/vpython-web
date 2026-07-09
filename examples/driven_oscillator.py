# 강제 진동: 외부 구동점과 질량의 위상 차이를 비교한다.
driver = sphere(pos=vector(-3, 0.8, 0), radius=0.2, color=color.green)
mass = sphere(pos=vector(1, 0, 0), radius=0.34, color=color.orange)
spring = cylinder(radius=0.05, color=color.cyan)
track = cylinder(pos=vector(-4, -0.7, 0), axis=vector(8, 0, 0), radius=0.035, color=color.white)

t = 0
while True:
    rate(70)
    t = t + 0.04
    driver.pos.x = -3 + 0.55 * math.sin(1.7 * t)
    mass.pos.x = 1.5 * math.sin(1.7 * t - 0.8) + 0.2 * math.sin(3.4 * t)
    spring.pos = driver.pos
    spring.axis = mass.pos - driver.pos
