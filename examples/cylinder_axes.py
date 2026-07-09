base = vector(-2, 0, 0)

cylinder(pos=base, axis=vector(4, 0, 0), radius=0.12, color=color.red)
cylinder(pos=base, axis=vector(0, 2, 0), radius=0.12, color=color.green)
cylinder(pos=base, axis=vector(0, 0, 2), radius=0.12, color=color.blue)

marker = sphere(pos=base, radius=0.18, color=color.white)

while True:
    rate(30)
    marker.pos.x = marker.pos.x + 0.01
    if marker.pos.x > 2:
        marker.pos.x = base.x
