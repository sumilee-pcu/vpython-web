# 2D 격자 진동: 결정 격자의 작은 진동을 흉내낸다.
atoms = []
for ix in range(7):
    for iy in range(5):
        atoms.append(sphere(pos=vector(-3 + ix, -2 + iy, 0), radius=0.09, color=color.cyan))

t = 0
while True:
    rate(60)
    t = t + 0.06
    for n, atom in enumerate(atoms):
        ix = n % 7
        iy = n // 7
        base = vector(-3 + ix, -2 + iy, 0)
        atom.pos = base + vector(0.13 * math.sin(t + ix), 0.13 * math.cos(1.4 * t + iy), 0)
