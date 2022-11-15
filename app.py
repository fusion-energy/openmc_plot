# run with "streamlit run app.py"

import streamlit as st
import openmc
import matplotlib.pyplot as plt

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            footer:after {
                content:'Made by Jonathan Shimwell'; 
                visibility: visible;
                display: block;
                position: relative;
                #background-color: red;
                padding: 5px;
                top: 2px;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.write(
    """
    # OpenMC plot
    ⚛ A geometry plotting user interface for OpenMC ⚛.
"""
)

st.write("👉 Add your openmc.Surfaces, openmc.Cells and openmc.Universe to the text box below.")
st.write("👉 Then set the openmc.Universe equal to a variable called my_universe.")
st.write("👉 To assign colors create a variable called my_colors which contains a dictionary of cells or materials and their colors.")

geometry_code = st.text_area(
    label="Edit the contents of the text box then press ⌨ ctrl and enter to update ♻ the plot",
    height=420,
    value=(
        '# makes 4 surfaces\n'
        'surface_1 = openmc.Sphere(r=100)\n'
        'surface_2 = openmc.ZPlane(z0=40)\n'
        'surface_3 = openmc.Plane(a=1.5, b=0, c=0.75, d=1)\n'
        'surface_4 = openmc.Plane(a=1, b=0, c=-0.6, d=25)\n'
        '\n'
        '# makes 3 cells\n'
        'cell_1 = openmc.Cell(region=-surface_1&+surface_2)\n'
        'cell_2 = openmc.Cell(region=-surface_1&+surface_3)\n'
        'cell_3 = openmc.Cell(region=-surface_1&+surface_4)\n'
        '\n'

        '# sets the openmc.Universe equal to a variable called my_universe.\n'
        'my_universe = openmc.Universe(cells=[cell_1, cell_2, cell_3])\n'

        '\n'
        '# sets the colors of each cell to red\n'
        'my_colors = {cell_1: "red", cell_2: "red", cell_3: "red"}\n'
    )
) 
 
if geometry_code is not None:
    exec(geometry_code)

    if 'my_universe' in locals():
        if 'my_colors' not in locals():
            st.write('No variable called "colors" found, using random colors for plot')
            my_colors=None
        
        bb = my_universe.bounding_box

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

        plt = my_universe.plot(
            width=(plot_width, plot_height),
            basis=option.lower(),
            origin=(x_offset, y_offset, z_offset),
            axes=base_plot,
            pixels=(pixels_width, pixels_height),
            colors=my_colors
        )
        plt.figure.savefig('image.png')
        st.image('image.png', use_column_width='always')
        
    else:
        st.write("Create an openmc.Universe() object called my_universe to display the plots")


st.write("Link to 🐍 [source code repository](https://github.com/fusion-energy/openmc_plot) where you can raise a feature request, report and issue or make a contribution.")
