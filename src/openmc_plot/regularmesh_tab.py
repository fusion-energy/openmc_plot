import streamlit as st
from utils import save_uploadedfile, make_pretend_mats

import openmc
import matplotlib.pyplot as plt
from pylab import *
from matplotlib.colors import LogNorm
import plotly.graph_objects as go
import numpy as np
import regular_mesh_plotter as rmp
import xml.etree.ElementTree as ET

def create_regularmesh_tab():
    st.write(
        """
        This tab makes use of the 🐍 Python package ```regular_mesh_plotter``` which is available on [GitHub](https://github.com/fusion-energy/regular_mesh_plotter).
        """
    )
    
    file_col1, file_col2 = st.columns([1, 1])

    file_col1.write(
        """
            👉 Run an OpenMC simulation with a mesh tally containing a RegularMesh filter and produce a statepoint.h5 output file.
        """
    )
    file_col2.write(
        """
            To get the cell or material outline you can optionally load a geometry xml file or a DAGMC h5m file.
        """
    )
    statepoint_file = file_col1.file_uploader(
        "Upload your statepoint h5 file", type=["h5"], key="statepoint_uploader"
    )
    geometry_file = file_col2.file_uploader(
        "Upload your geometry.xml or DAGMC h5m file", type=["xml", 'hm5']
    )

    # TODO add image of 3d regular mesh
    # col2.image("image.png", use_column_width="always")

    if statepoint_file == None:
        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 30px;">Upload your statepoint h5 file</p>'
        st.markdown(new_title, unsafe_allow_html=True)

        st.markdown(
            """
            Not got a Statepoint h5 file handy, right mouse 🖱️ click and save this link
            [example 1](https://github.com/fusion-energy/openmc_plot/raw/adding_statepoint_example_file/examples/regularmesh_plot/statepoint.40.h5)
            """
        )
    else:
    
        save_uploadedfile(statepoint_file)


        # loads up the output file from the simulation
        statepoint = openmc.StatePoint(statepoint_file.name)

        # finds all the tallies that have a regular mesh and gets their ID,
        # score and mesh ID. These are used to make the "tally to plot" dropdown
        tally_description = rmp.get_regularmesh_tallies_and_scores(statepoint)
        tally_description_str = [f"ID={td['id']} score={td['score']} name={td['name']}" for td in tally_description]
        col1, col2 = st.columns([1, 3])

        tally_description_to_plot = col1.selectbox(
            label="Tally to plot",options=tally_description_str, index=0
        )
        tally_id_to_plot = tally_description_to_plot.split(" ")[0][3:]
        tally_score_to_plot = tally_description_to_plot.split(" ")[1][6:]

        view_direction = col1.selectbox(
            label="Slice plane", options=("x", "y", "z"), index=0
        )

        tally_or_std = col1.radio(
            "Tally mean or std dev", options=["mean", "std_dev"]
        )
        volume_normalization = col1.radio(
            "Divide value by mesh voxel volume", options=[True, False]
        )
        
        value_multiple = col1.number_input(
            "Multiplier value", value=1., help='Input a number that will be used to scale the mesh values. For example a input of 2 would double all the values.'
        )
        
        my_tally = statepoint.get_tally(id=int(tally_id_to_plot))
        score = my_tally.get_values(scores=[tally_score_to_plot],value =tally_or_std)
        mesh = my_tally.find_filter(filter_type=openmc.MeshFilter).mesh
        extent = mesh.get_mpl_plot_extent(view_direction=view_direction)

        transposed_ds = mesh.reshape_data(score, view_direction)

        slice_index = col1.slider(
            label="slice index",
            min_value=0,
            max_value=len(transposed_ds) - 1,
            value=int(len(transposed_ds) / 2),
        )

        contour_levels_str = col1.text_input(
            "Contour levels",
            help="Optionally add some comma deliminated contour values",
            # value=,
        )
        if contour_levels_str:
            contour_levels = sorted([float(v) for v in contour_levels_str.strip().split(',')])
        else:
            contour_levels = None
            
        if geometry_file:
            save_uploadedfile(geometry_file)

            if geometry_file.name.endswith('xml'):
                tree = ET.parse(geometry_file.name)
                root = tree.getroot()
                all_cells = root.findall("cell")
                mat_ids = []

                for cell in all_cells:
                    if "material" in cell.keys():
                        if cell.get("material") == "void":
                            mat_ids.append(0)
                            print(f"material for cell {cell} is void")
                        else:
                            mat_ids.append(int(cell.get("material")))

                if len(mat_ids) >= 1:
                    set_mat_ids = set(mat_ids)
                else:
                    set_mat_ids = ()
                my_mats = make_pretend_mats(set_mat_ids)
                my_geometry = openmc.Geometry.from_xml(
                path=geometry_file.name, materials=my_mats
                )
                outline = col1.radio(
                    "Outline", options=["material", "cell", "None"]
                )
            
                slice_value=mesh.get_slice_axis_value_from_index(slice_index=slice_index, view_direction=view_direction)
            
                if outline == "cell":
                    outline_data_slice = my_geometry.get_slice_of_cell_ids(
                        view_direction=view_direction,
                        plot_left=extent[0],
                        plot_right=extent[1],
                        plot_top=extent[2],
                        plot_bottom=extent[3],
                        pixels_across=500,
                        slice_value=slice_value,
                    )
                elif outline == 'material':
                    outline_data_slice = my_geometry.get_slice_of_material_ids(
                        view_direction=view_direction,
                        plot_left=extent[0],
                        plot_right=extent[1],
                        plot_top=extent[2],
                        plot_bottom=extent[3],
                        pixels_across=500,
                        slice_value=slice_value,
                    )
                else:
                    outline_data_slice = None
                    
        else:
            outline_data_slice = None

        image_slice= mesh.slice_of_data(
            dataset=score,#,
            view_direction=view_direction,
            slice_index=slice_index,
            volume_normalization=volume_normalization
        )
        
        image_slice=image_slice*value_multiple

        if tally_or_std == "mean":
            cbar_label = tally_score_to_plot
        else:  # 'std dev'
            cbar_label = f"standard deviation {tally_score_to_plot}"
        
        title = col1.text_input(
            "Colorbar title",
            help="Optionally set your own colorbar label for the plot",
            value=cbar_label,
        )


        xlabel, ylabel = mesh.get_axis_labels(view_direction=view_direction)

        log_lin_scale = col1.radio("Scale", options=["log", "linear"])
        if log_lin_scale == "linear":
            norm = None
        else:
            norm = LogNorm()

        if view_direction == "y":
            mpl_image_slice = np.rot90(image_slice)
            plotly_image_slice = np.rot90(image_slice, 3)
        if view_direction == "z":
            mpl_image_slice = np.rot90(image_slice)
            plotly_image_slice = np.rot90(image_slice, 1)
        if view_direction == "x":
            mpl_image_slice = np.flipud(image_slice)
            plotly_image_slice = image_slice

        col_mpl, col_plotly = col2.tabs(
            ["📉 MatplotLib image", "📈 Plotly interactive plot"]
        )
        with col_mpl:

            heatmap_axes = plt.subplot(1,1,1)
            
            (xlabel, ylabel) = mesh.get_axis_labels(
                view_direction=view_direction
            )

            heatmap_axes.set_xlabel(xlabel)
            heatmap_axes.set_ylabel(ylabel)

            im=heatmap_axes.imshow(
                X=mpl_image_slice,
                extent=extent,
                norm=norm
            )

            if contour_levels_str:
                heatmap_axes.contour(
                    mpl_image_slice,
                    levels=contour_levels,
                    colors='grey',
                    linewidths=1,
                    extent=extent,
                )

            plt.colorbar(im, label=title, ax=heatmap_axes)

            if outline_data_slice is not None:
                levels = np.unique(
                    [item for sublist in outline_data_slice for item in sublist]
                )
                # contour_axes = heatmap_axes
                heatmap_axes.contour(
                    outline_data_slice,
                    origin="upper",
                    colors="k",
                    linestyles="solid",
                    levels=levels,
                    linewidths=0.5,
                    extent=extent,
                )


            plt.savefig('openmc_plot_regularmesh_image.png')
            with open("openmc_plot_regularmesh_image.png", "rb") as file:
                col_mpl.download_button(
                    label="Download image",
                    data=file,
                    file_name="openmc_plot_regularmesh_image.png",
                    mime="image/png"
                )
            col_mpl.pyplot(plt)

        with col_plotly:
            
            # plotly does not fully support log heatmaps so z values are logged
            # docs on heatmaps
            # https://plotly.github.io/plotly.py-docs/generated/plotly.graph_objects.Heatmap.html
            # https://plotly.com/python/heatmaps/
            if log_lin_scale == "log":
                figure = go.Figure(
                    data=go.Heatmap(
                        z=np.log(plotly_image_slice),
                        colorscale='viridis',
                        x0 =extent[0],
                        dx=abs(extent[0]-extent[1])/(len(plotly_image_slice[0])-1),
                        y0 =extent[2],
                        dy=abs(extent[2]-extent[3])/(len(plotly_image_slice)-1),
                        showscale=False  # avoids the color bar not being log scale
                        ),
                    )
            else:
                figure = go.Figure(
                    data=go.Heatmap(
                        z=plotly_image_slice,
                        colorscale='viridis',
                        x0 =extent[0],
                        dx=abs(extent[0]-extent[1])/(len(plotly_image_slice[0])-1),
                        y0 =extent[2],
                        dy=abs(extent[2]-extent[3])/(len(plotly_image_slice)-1),
                        colorbar=dict(title=dict(side="right", text=cbar_label)),
                        ),
                    )
                

            figure.update_layout(
                xaxis={"title": xlabel},
                yaxis={"title": ylabel},
                autosize=False,
                height=800,
            )
            figure.update_yaxes(
                scaleanchor = "x",
                scaleratio = 1,
            )

            figure.write_html('openmc_plot_regularmesh_image.html')

            with open("openmc_plot_regularmesh_image.html", "rb") as file:
                col_plotly.download_button(
                    label="Download image",
                    data=file,
                    file_name="openmc_plot_regularmesh_image.html",
                    mime=None
                )
            col_plotly.plotly_chart(figure, use_container_width=True, height=800)
