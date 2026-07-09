# 감쇠 진동: 시간이 지나며 진폭이 줄어드는 운동.
track = cylinder(pos=vector(-4, -0.65, 0), axis=vector(8, 0, 0), radius=0.035, color=color.white)
mass = sphere(radius=0.35, color=color.orange)
ghost = sphere(radius=0.35, color=color.cyan, opacity=0.25)

t = 0
while True:
    rate(80)
    t = t + 0.035
    amp = 3.0 * math.exp(-0.08 * (t % 35))
    mass.pos = vector(amp * math.cos(2.4 * t), 0, 0)
    ghost.pos = vector(3.0 * math.cos(2.4 * t), -1.15, 0)
    if t > 35:
        t = 0
