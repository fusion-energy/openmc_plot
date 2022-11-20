import streamlit as st
import openmc
import matplotlib.pyplot as plt
from pylab import *

def save_uploadedfile(uploadedfile):
    with open(uploadedfile.name, "wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success(f"Saved File to {uploadedfile.name}")
 
def main():


    st.set_page_config(
            page_title="OpenMC Plot",
            page_icon="⚛",
            layout="wide",
        )

    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {
                    visibility: hidden;
                    }
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

    st.write(
        """
            # OpenMC plot
            ### ⚛ A geometry plotting user interface for OpenMC.
            
            👉 Create your OpenMC model and export the xml files ```export_to_xml()``` then upload them to this app.

            🐍 Run this app locally with Python ```pip install openmc_plot``` then run with ```openmc_plot```

            💾 Raise a feature request, report and issue or make a contribution on [GitHub](https://github.com/fusion-energy/openmc_plot)

            📧 Email feedback to mail@jshimwell.com
        """
    )

    datafile = st.file_uploader("Upload your geometry.xml and materials.xml",type=['xml'],accept_multiple_files=True)


    if datafile == []:
        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 30px;">Upload your geometry.xml and materials.xml</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        
        st.markdown(
            'Not got xml files handy? Download sample [geometry.xml](https://raw.githubusercontent.com/fusion-energy/openmc_plot/main/examples/tokamak/geometry.xml) and [materials.xml](https://raw.githubusercontent.com/fusion-energy/openmc_plot/main/examples/tokamak/materials.xml)'
        )

    
    elif len(datafile)==1:
        if datafile[0].name == 'geometry.xml':
            new_title = '<p style="font-family:sans-serif; color:Red; font-size: 30px;">Upload your materials.xml</p>'
            st.markdown(new_title, unsafe_allow_html=True)
        elif datafile[0].name == 'materials.xml':
            new_title = '<p style="font-family:sans-serif; color:Red; font-size: 30px;">Upload your geometry.xml</p>'
            st.markdown(new_title, unsafe_allow_html=True)
    elif len(datafile)>2:
        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 30px;">You have uploaded too many files, upload just the geometry.xml and material.xml files.</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        
    elif len(datafile)==2:
        filenames = [datafile[0].name, datafile[1].name]
        if 'geometry.xml' in filenames and 'materials.xml' in filenames:
    
            save_uploadedfile(datafile[0])
            save_uploadedfile(datafile[1])

            my_mats = openmc.Materials.from_xml('materials.xml')
            
            # removes all the nuclides otherwise these are needed in the cross_sections.xml
            for mat in my_mats:
                for element in mat.get_elements():
                    mat.remove_element(element)
                # adds a single nuclide that is in minimal cross section xml to avoid material failing
                mat.add_nuclide('Li6', 1)
            
            my_geometry = openmc.Geometry.from_xml(materials=my_mats)
            my_universe = my_geometry.root_universe
            
            bb = my_universe.bounding_box

            col1, col2 = st.columns([1, 3])


            option = col1.selectbox(
                label='Axis basis',
                options=('XZ', 'XY', 'YZ'),
                index=0
            )
            
            x_offset = col1.slider(
                label='X axis offset',
                min_value=float(bb[0][0]),
                max_value=float(bb[1][0]),
                value=float((bb[0][0]+bb[1][0])/2)
            )

            y_offset = col1.slider(
                label='Y axis offset',
                min_value=float(bb[0][1]),
                max_value=float(bb[1][1]),
                value=float((bb[0][1]+bb[1][1])/2)
            )

            z_offset = col1.slider(
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

            plot_width = col1.number_input(
                label='Plot width (cm)',
                min_value=1.,
                step=1.,
                value=plot_width_bb,
            )

            plot_height = col1.number_input(
                label='Plot height (cm)',
                min_value=1.,
                step=1.,
                value=plot_height_bb,
            )
            global plt
            base_plot=plt.axes(xlabel=xlabel, ylabel=ylabel)
            aspect_ratio = plot_width / plot_height
            
            pixels_width = col1.number_input(
                'Image resolution (pixels in width)',
                min_value=10,
                value=1500
            )

            color_by = st.radio(
                'Color by options',
                options=['random','cell','material']
            )
            
            if color_by == 'material':
                cmap = cm.get_cmap('viridis', len(my_mats))

                initial_hex_color = []
                for i in range(cmap.N):
                    rgba = cmap(i)
                    # rgb2hex accepts rgb or rgba
                    initial_hex_color.append(matplotlib.colors.rgb2hex(rgba))
    
                my_colors   ={}
                mat_names = [mat.name for mat in my_mats]
                for c, mat_name in enumerate(mat_names):
                    st.color_picker(
                        f'Color of material {mat_name}',
                        key=mat_name,
                        value=initial_hex_color[c]
                    )

                for material in my_mats:
                    hex_color = st.session_state[material.name].lstrip('#')
                    RGB = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    my_colors[material]=RGB

            elif color_by == 'cell':
                my_cells = my_universe.cells
                my_cells_ids = my_universe.cells.keys()
                cmap = cm.get_cmap('viridis', len(my_cells))

                initial_hex_color = []
                for i in range(cmap.N):
                    rgba = cmap(i)
                    # rgb2hex accepts rgb or rgba
                    initial_hex_color.append(matplotlib.colors.rgb2hex(rgba))
    
                my_colors   ={}
                for c, cell_id in enumerate(my_cells_ids):
                    st.color_picker(
                        f'Color of cell {cell_id}',
                        key=f'cell_{cell_id}',
                        value=initial_hex_color[c]
                    )

                for cell, cell_id in zip(my_cells, my_cells_ids):
                    hex_color = st.session_state[f'cell_{cell_id}'].lstrip('#')
                    RGB = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    my_colors[cell]=RGB

            else:  #random selected
                my_colors=None
            
            pixels_height = int(1500 / aspect_ratio)

            plt = my_universe.plot(
                width=(plot_width, plot_height),
                basis=option.lower(),
                origin=(x_offset, y_offset, z_offset),
                axes=base_plot,
                pixels=(pixels_width, pixels_height),
                colors=my_colors
            )
            plt.figure.savefig('image.png')
            col2.image('image.png', use_column_width='always')
                
        else:
            new_title = '<p style="font-family:sans-serif; color:Red; font-size: 30px;">Upload just geometry.xml and material.xml with these filenames</p>'
            st.markdown(new_title, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
