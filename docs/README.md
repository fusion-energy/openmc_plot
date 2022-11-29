image magic commands for making gifs

convert -delay 60 -loop 0 geometry/g_*.png -scale 520x960 openmc_plot_geometry.gif
convert -delay 60 -loop 0 source/s_*.png -scale 520x960 openmc_plot_source.gif
convert -delay 60 -loop 0 mesh/m_*.png -scale 520x960 openmc_plot_mesh.gif
convert -delay 60 -loop 0 weightwindows/w_*.png -scale 520x960 openmc_plot_weight.gif
