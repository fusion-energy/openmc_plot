import streamlit as st
import openmc
import matplotlib.pyplot as plt

st.write(
    """
    # OpenMC plot
    A geometry plotting user interface for OpenMC.
"""
)

geometry_code = st.text_area("Enter multiline text",
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

        plt = universe.plot(width=(x_width,z_width), basis='xz')
        plt.figure.savefig('xz.png')
        st.image('xz.png', use_column_width='always')

        plt = universe.plot(width=(x_width,y_width), basis='xy')
        plt.figure.savefig('xy.png')
        st.image('xy.png', use_column_width='always')

        plt = universe.plot(width=(y_width,z_width), basis='yz')
        plt.figure.savefig('yz.png')
        st.image('yz.png', use_column_width='always')
        
    else:
        st.write("Create an openmc.Universe() object called universe to display the plots")
