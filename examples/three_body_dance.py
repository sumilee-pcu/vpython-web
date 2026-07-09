# 세 물체의 라그랑주식 춤: 같은 궤도를 위상 차이로 따라간다.
balls = [
    sphere(radius=0.26, color=color.red),
    sphere(radius=0.26, color=color.green),
    sphere(radius=0.26, color=color.blue),
]
links = [cylinder(radius=0.025, color=color.white, opacity=0.45) for i in range(3)]

t = 0
while True:
    rate(70)
    t = t + 0.035
    for i in range(3):
        a = t + i * 2 * pi / 3
        balls[i].pos = vector(2.2 * math.cos(a), 0.7 * math.sin(2 * a), 2.2 * math.sin(a))
    for i in range(3):
        links[i].pos = balls[i].pos
        links[i].axis = balls[(i + 1) % 3].pos - balls[i].pos
