import openmc

# initialises a new source object
my_source1 = openmc.Source()

# the distribution of radius is just a single value
radius = openmc.stats.Discrete([10], [1])

# the distribution of source z values is just a single value
z_values = openmc.stats.Discrete([0], [1])

# the distribution of source azimuthal angles values is a uniform distribution between 0 and 2 Pi
angle = openmc.stats.Uniform(a=0., b=2* 3.14159265359)

# this makes the ring source using the three distributions and a radius
my_source1.space = openmc.stats.CylindricalIndependent(r=radius, phi=angle, z=z_values, origin=(0.0, 0.0, 0.0))

# sets the direction to isotropic
my_source1.angle = openmc.stats.Isotropic()

# sets the energy distribution to a Muir distribution neutrons
my_source1.energy = openmc.stats.Muir(e0=14080000.0, m_rat=5.0, kt=20000.0)



# initialises a new source object
my_source2 = openmc.Source()

# the distribution of radius is just a single value
radius = openmc.stats.Discrete([9], [1])

# the distribution of source z values is just a single value
z_values = openmc.stats.Discrete([0], [1])

# the distribution of source azimuthal angles values is a uniform distribution between 0 and 2 Pi
angle = openmc.stats.Uniform(a=0., b=2* 3.14159265359)

# this makes the ring source using the three distributions and a radius
my_source2.space = openmc.stats.CylindricalIndependent(r=radius, phi=angle, z=z_values, origin=(0.0, 0.0, 0.0))

# sets the direction to isotropic
my_source2.angle = openmc.stats.Isotropic()

# sets the energy distribution to a Muir distribution neutrons
my_source2.energy = openmc.stats.Muir(e0=2000000.0, m_rat=4.0, kt=20000.0)

my_settings = openmc.Settings()

my_settings.source = [my_source1, my_source2]

my_settings.export_to_xml('settings_multiple_sources.xml')