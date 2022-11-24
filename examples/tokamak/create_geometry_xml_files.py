

import openmc
import matplotlib.pyplot as plt

# surfaces
central_column_surface = openmc.ZCylinder(r=100) # note the new surface type
inner_sphere_surface = openmc.Sphere(r=480)
middle_sphere_surface = openmc.Sphere(r=500) 
outer_sphere_surface = openmc.Sphere(r=600, boundary_type='vacuum')

# regions
# the center column region is cut at the top and bottom using the -outer_sphere_surface
central_column_region = -central_column_surface & -outer_sphere_surface
firstwall_region = -middle_sphere_surface & +inner_sphere_surface & +central_column_surface
blanket_region = +middle_sphere_surface & -outer_sphere_surface & +central_column_surface
inner_vessel_region = +central_column_surface & -inner_sphere_surface

# cells
firstwall_cell = openmc.Cell(region=firstwall_region)
central_column_cell = openmc.Cell(region=central_column_region)
blanket_cell = openmc.Cell(region=blanket_region)
inner_vessel_cell = openmc.Cell(region=inner_vessel_region)

universe = openmc.Universe(cells=[central_column_cell, firstwall_cell,
                                  blanket_cell, inner_vessel_cell])

my_geometry = openmc.Geometry(universe)

my_geometry.export_to_xml('geometry_no_materials.xml')

mat_1 = openmc.Material()
mat_1.id = 1
mat_1.add_element('Na', 1)
mat_1.set_density('g/cm3', 1)
blanket_cell.fill = mat_1

universe = openmc.Universe(cells=[central_column_cell, firstwall_cell,
                                  blanket_cell, inner_vessel_cell])

my_geometry = openmc.Geometry(universe)

my_geometry.export_to_xml('geometry_some_materials.xml')