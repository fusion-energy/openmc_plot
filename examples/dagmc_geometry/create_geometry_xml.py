
import openmc

dagunv = openmc.DAGMCUniverse("dagmc_text.h5m").bounded_universe()

geometry = openmc.Geometry(dagunv)

geometry.export_to_xml()
