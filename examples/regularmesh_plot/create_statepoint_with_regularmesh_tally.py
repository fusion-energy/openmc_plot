import openmc
import os

import matplotlib.pyplot as plt
import numpy as np

# MATERIALS

breeder_material = openmc.Material()  # Pb84.2Li15.8
# breeder_material.add_element('Pb', 84.2, percent_type='ao')
breeder_material.add_element("Li", 1.0)  # natural enrichment = 7% Li6
breeder_material.set_density("g/cm3", 0.01)  # around 11 g/cm3

copper_material = openmc.Material()
copper_material.set_density("g/cm3", 0.01)
copper_material.add_element("Li", 1.0)

eurofer_material = openmc.Material()
eurofer_material.set_density("g/cm3", 0.01)
eurofer_material.add_element("Li", 1)

# dt_plasma_material = openmc.Material()
# dt_plasma_material.set_density("g/cm3", 1e-7)
# dt_plasma_material.add_nuclide("H2", 0.5)
# dt_plasma_material.add_nuclide("H3", 0.5)

mats = openmc.Materials(
    [breeder_material, eurofer_material, copper_material]#, dt_plasma_material]
)


# GEOMETRY

# surfaces
central_sol_surface = openmc.ZCylinder(r=100)
central_shield_outer_surface = openmc.ZCylinder(r=110)
# plasma_surface = openmc.ZTorus(x0=200,y0=200)
port_hole = openmc.Sphere(r=60, x0=500)
upper_port_hole = openmc.Sphere(r=100, z0=500)
vessel_inner_surface = openmc.Sphere(r=500)
first_wall_outer_surface = openmc.Sphere(r=510)
breeder_blanket_outer_surface = openmc.Sphere(r=610, boundary_type="vacuum")

# cells
central_sol_region = -central_sol_surface & -breeder_blanket_outer_surface & +upper_port_hole
central_sol_cell = openmc.Cell(region=central_sol_region)
central_sol_cell.fill = copper_material

central_shield_region = (
    +central_sol_surface
    & -central_shield_outer_surface
    & -breeder_blanket_outer_surface
    & +upper_port_hole
)
central_shield_cell = openmc.Cell(region=central_shield_region)
central_shield_cell.fill = eurofer_material

# plasma_cell_region = -plasma_surface
# plasma_cell_cell = openmc.Cell(region=plasma_cell_region)
# plasma_cell_cell.fill = dt_plasma_material

inner_vessel_region = (
    -vessel_inner_surface & +central_shield_outer_surface  & +port_hole & +upper_port_hole
    #& +plasma_surface
)
inner_vessel_cell = openmc.Cell(region=inner_vessel_region)
# inner_vessel_cell.fill = eurofer_material
# no material set as default is vacuum

upper_port_hole_region = -upper_port_hole
upper_port_hole_cell = openmc.Cell(region=upper_port_hole_region)

port_hole_region = -port_hole
port_hole_cell = openmc.Cell(region=port_hole_region)
# port_hole_cell.fill = eurofer_material
# no material set as default is vacuum

first_wall_region = -first_wall_outer_surface & +vessel_inner_surface & +port_hole &+upper_port_hole
first_wall_cell = openmc.Cell(region=first_wall_region)
first_wall_cell.fill = eurofer_material

breeder_blanket_region = (
    +first_wall_outer_surface
    & -breeder_blanket_outer_surface
    & +central_shield_outer_surface
    & +port_hole
    & +upper_port_hole
)
breeder_blanket_cell = openmc.Cell(region=breeder_blanket_region)
breeder_blanket_cell.fill = breeder_material

universe = openmc.Universe(
    cells=[
        central_sol_cell,
        central_shield_cell,
        inner_vessel_cell,
        first_wall_cell,
        breeder_blanket_cell,
        port_hole_cell,
        upper_port_hole_cell
        # plasma_cell_cell,
    ]
)
my_geometry = openmc.Geometry(universe)


# SIMULATION SETTINGS

# Instantiate a Settings object
sett = openmc.Settings()
batches = 40
sett.batches = batches
sett.inactive = 0
sett.particles = 50000
sett.run_mode = "fixed source"

# Create a DT point source
# initialises a new source object
my_source = openmc.Source()

# the distribution of radius is just a single value
radius = openmc.stats.Discrete([200], [1])

# the distribution of source z values is just a single value
z_values = openmc.stats.Discrete([0], [1])

# the distribution of source azimuthal angles values is a uniform distribution between 0 and 2 Pi
angle = openmc.stats.Uniform(a=0.0, b=2 * 3.14159265359)

# this makes the ring source using the three distributions and a radius
my_source.space = openmc.stats.CylindricalIndependent(
    r=radius, phi=angle, z=z_values, origin=(0.0, 0.0, 0.0)
)

# sets the direction to isotropic
my_source.angle = openmc.stats.Isotropic()

# sets the energy distribution to a Muir distribution neutrons
my_source.energy = openmc.stats.muir(e0=14080000.0, m_rat=5.0, kt=20000.0)

sett.source = my_source

# Create mesh which will be used for tally
mesh = openmc.RegularMesh().from_domain(
    my_geometry,  # the corners of the mesh are being set automatically to surround the geometry
    # dimension=[10, 20, 30] # voxels in each axis direction (x, y, z)
    dimension=[50, 60, 30],  # voxels in each axis direction (x, y, z)
)

tallies = openmc.Tallies()
# Create mesh filter for tally
mesh_filter = openmc.MeshFilter(mesh)

# Create flux mesh tally to score flux
mesh_tally_1 = openmc.Tally(name="flux_on_mesh")
mesh_tally_1.filters = [mesh_filter]
mesh_tally_1.scores = ["flux"]
tallies.append(mesh_tally_1)

mesh_tally_1 = openmc.Tally(name="heating_on_mesh")
mesh_tally_1.filters = [mesh_filter]
mesh_tally_1.scores = ["heating"]
tallies.append(mesh_tally_1)

model = openmc.model.Model(my_geometry, mats, sett, tallies)
sp_filename = model.run()
sp_filename = f'statepoint.{sett.batches}.h5'

# loads up the output file from the simulation
statepoint = openmc.StatePoint(sp_filename)

# extracts the mesh tally by name
my_tbr_tally = statepoint.get_tally(name="heating_on_mesh")

# converts the tally result into a VTK file
mesh.write_data_to_vtk(
    filename="tbr_tally_on_reg_mesh.vtk",
    datasets={
        "mean": my_tbr_tally.mean
    },  # the first "mean" is the name of the data set label inside the vtk file
)


f = my_tbr_tally.mean
ff = f.flatten()
ff2 = ff.reshape(mesh.dimension, order="F")


ffx = ff2.transpose(1, 2, 0)
left = mesh.lower_left[0]
right = mesh.upper_right[0]
bottom = mesh.lower_left[0]
top = mesh.upper_right[0]
extent = (left, right, bottom, top)
slice_value = int(len(ffx) / 2)
plt.imshow(X=ffx[slice_value], extent=extent)
plt.show()

ffy = ff2#.transpose(2, 1, 0)
left = mesh.lower_left[1]
right = mesh.upper_right[1]
bottom = mesh.lower_left[1]
top = mesh.upper_right[1]
extent = (left, right, bottom, top)
slice_value = int(len(ffy) / 2)
plt.imshow(X=ffy[slice_value], extent=extent)
plt.show()

ffz = ff2.transpose(2, 0, 1)
# ffz = ff2.transpose(0,2,1)
left = mesh.lower_left[2]
right = mesh.upper_right[2]
bottom = mesh.lower_left[2]
top = mesh.upper_right[2]
slice_value = int(len(ffz) / 2)
plt.imshow(X=ffz[slice_value], extent=extent)
plt.show()
