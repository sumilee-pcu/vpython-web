# 단순 조화 운동: x = A cos(wt)
track = cylinder(pos=vector(-4, -0.6, 0), axis=vector(8, 0, 0), radius=0.035, color=color.white)
mass = sphere(pos=vector(2, 0, 0), radius=0.32, color=color.cyan)
origin = sphere(pos=vector(0, 0, 0), radius=0.08, color=color.white)

markers = []
for i in range(25):
    markers.append(sphere(pos=mass.pos, radius=0.035, color=color.orange, opacity=0.35))

t = 0
while True:
    rate(80)
    t = t + 0.04
    mass.pos.x = 2.8 * math.cos(t)
    if int(t * 10) % 2 == 0:
        markers[int(t * 5) % len(markers)].pos = mass.pos
