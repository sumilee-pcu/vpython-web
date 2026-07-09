# 같은 부호 전하의 반발: 두 입자가 멀어졌다가 벽에서 되돌아온다.
left = sphere(pos=vector(-0.7, 0, 0), radius=0.28, color=color.red)
right = sphere(pos=vector(0.7, 0, 0), radius=0.28, color=color.red)
rail = cylinder(pos=vector(-4, -0.65, 0), axis=vector(8, 0, 0), radius=0.035, color=color.white)
left.velocity = vector(-0.6, 0, 0)
right.velocity = vector(0.6, 0, 0)

dt = 0.02
while True:
    rate(70)
    r = right.pos.x - left.pos.x
    force = 0.9 / (r * r)
    left.velocity.x = left.velocity.x - force * dt
    right.velocity.x = right.velocity.x + force * dt
    left.pos = left.pos + left.velocity * dt
    right.pos = right.pos + right.velocity * dt
    if left.pos.x < -3.6 or right.pos.x > 3.6:
        left.pos = vector(-0.7, 0, 0)
        right.pos = vector(0.7, 0, 0)
        left.velocity = vector(-0.6, 0, 0)
        right.velocity = vector(0.6, 0, 0)
