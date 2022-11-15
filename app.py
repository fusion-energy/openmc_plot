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

        x_width = bb[0][0] - bb[1][0]
        y_width = bb[0][1] - bb[1][1]
        z_width = bb[0][2] - bb[1][2]
        
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

        # TODO add an offset to slice using origin arg
        # https://github.com/openmc-dev/openmc/blob/765df9115f58624bd77c6304435c4f5166df67be/openmc/universe.py#L273

        if option == 'XZ':
            width=(x_width,z_width)
        elif option == 'XY':
            width=(x_width,y_width)
        elif option == 'YZ':
            width=(y_width,z_width)

        plt = universe.plot(
            width=width,
            basis=option.lower(),
            origin=(x_offset, y_offset, z_offset)
        )
        plt.figure.savefig('image.png')
        st.image('image.png', use_column_width='always')
        
    else:
        st.write("Create an openmc.Universe() object called universe to display the plots")
