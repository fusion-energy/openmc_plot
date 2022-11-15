# run with "streamlit run app.py"

import streamlit as st
import openmc
import matplotlib.pyplot as plt

st.write(
    """
    # OpenMC plot
    A geometry plotting user interface for OpenMC.
"""
)

geometry_code = st.text_area("Edit the text box below to define the universe to plot",
    height=300,
    value=(
        'surface_1 = openmc.Sphere(r=100)\n'
        '\n'
        'surface_2 = openmc.YCylinder(r=50)\n'
        '\n'
        'cell_1 = openmc.Cell(region=-surface_1&+surface_2)\n'
        '\n'
        'universe = openmc.Universe(cells=[cell_1])  '
        
    )
) 
 
if geometry_code is not None:
    exec(geometry_code)

    if 'universe' in locals():
        
        bb = universe.bounding_box

        option = st.selectbox(
            label='Axis basis',
            options=('XZ', 'XY', 'YZ'),
            index=0
        )
        
        x_offset = st.slider(
            label='X axis offset',
            min_value=float(bb[0][0]),
            max_value=float(bb[1][0]),
            value=float((bb[0][0]+bb[1][0])/2)
        )

        y_offset = st.slider(
            label='Y axis offset',
            min_value=float(bb[0][1]),
            max_value=float(bb[1][1]),
            value=float((bb[0][1]+bb[1][1])/2)
        )

        z_offset = st.slider(
            label='Z axis offset',
            min_value=float(bb[0][2]),
            max_value=float(bb[1][2]),
            value=float((bb[0][2]+bb[1][2])/2)
        )

        x_width = abs(bb[0][0] - bb[1][0])
        y_width = abs(bb[0][1] - bb[1][1])
        z_width = abs(bb[0][2] - bb[1][2])
        
        if option == 'XZ':
            plot_width_bb = x_width
            plot_height_bb = z_width
            xlabel = 'X [cm]'
            ylabel = 'Z [cm]'
        elif option == 'XY':
            plot_width_bb = x_width
            plot_height_bb = y_width
            xlabel = 'X [cm]'
            ylabel = 'Y [cm]'
        elif option == 'YZ':
            plot_width_bb = y_width
            plot_height_bb = z_width
            xlabel = 'Y [cm]'
            ylabel = 'Z [cm]'

        plot_width = st.number_input(
            label='Plot width (cm)',
            min_value=1.,
            step=1.,
            value=plot_width_bb,
        )

        plot_height = st.number_input(
            label='Plot height (cm)',
            min_value=1.,
            step=1.,
            value=plot_height_bb,
        )
        base_plot=plt.axes(xlabel=xlabel, ylabel=ylabel)
        aspect_ratio = plot_width / plot_height
        pixels_width = 1000
        pixels_height = int(1000 / aspect_ratio)
        print('pixels_width',pixels_width)
        print('pixels_height',pixels_height)
        plt = universe.plot(
            width=(plot_width, plot_height),
            basis=option.lower(),
            origin=(x_offset, y_offset, z_offset),
            axes=base_plot,
            pixels=(pixels_width, pixels_height)
        )
        plt.figure.savefig('image.png')
        st.image('image.png', use_column_width='always')
        
    else:
        st.write("Create an openmc.Universe() object called universe to display the plots")
