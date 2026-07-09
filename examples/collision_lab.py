# 1차원 충돌 실험: 질량이 다른 두 공의 탄성 충돌.
track = cylinder(pos=vector(-4, -0.65, 0), axis=vector(8, 0, 0), radius=0.04, color=color.white)
left_wall = box(pos=vector(-4.2, 0, 0), size=vector(0.12, 1.4, 1.2), color=color.gray(0.45))
right_wall = box(pos=vector(4.2, 0, 0), size=vector(0.12, 1.4, 1.2), color=color.gray(0.45))

a = sphere(pos=vector(-2.2, 0, 0), radius=0.35, color=color.cyan)
b = sphere(pos=vector(1.6, 0, 0), radius=0.5, color=color.orange)
a.mass = 1
b.mass = 2.4
a.velocity = vector(2.4, 0, 0)
b.velocity = vector(-0.8, 0, 0)

dt = 0.012
while True:
    rate(90)
    a.pos = a.pos + a.velocity * dt
    b.pos = b.pos + b.velocity * dt

    if a.pos.x < -3.7 or a.pos.x > 3.7:
        a.velocity.x = -a.velocity.x
    if b.pos.x < -3.5 or b.pos.x > 3.5:
        b.velocity.x = -b.velocity.x

    if abs(a.pos.x - b.pos.x) < a.radius + b.radius and a.velocity.x > b.velocity.x:
        u1 = a.velocity.x
        u2 = b.velocity.x
        m1 = a.mass
        m2 = b.mass
        a.velocity.x = ((m1 - m2) * u1 + 2 * m2 * u2) / (m1 + m2)
        b.velocity.x = (2 * m1 * u1 + (m2 - m1) * u2) / (m1 + m2)
