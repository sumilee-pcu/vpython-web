# 결합 진동자: 두 질량이 서로 에너지를 주고받는 모양.
left = sphere(radius=0.28, color=color.cyan)
right = sphere(radius=0.28, color=color.orange)
spring = cylinder(radius=0.045, color=color.white)
track = cylinder(pos=vector(-4, -0.75, 0), axis=vector(8, 0, 0), radius=0.035, color=color.gray(0.7))

t = 0
while True:
    rate(70)
    t = t + 0.035
    left.pos = vector(-1.2 + 0.9 * math.cos(t), 0, 0)
    right.pos = vector(1.2 + 0.9 * math.cos(t + 1.3 * math.sin(0.45 * t)), 0, 0)
    spring.pos = left.pos
    spring.axis = right.pos - left.pos
