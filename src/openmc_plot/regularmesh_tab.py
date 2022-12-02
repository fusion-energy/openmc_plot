import streamlit as st
from utils import save_uploadedfile
import openmc
import matplotlib.pyplot as plt
from pylab import *
from matplotlib.colors import LogNorm
import plotly.graph_objects as go
import numpy as np


def create_regularmesh_tab():
    st.write(
        """
        This tab makes use of the 🐍 Python package ```regular_mesh_plotter``` which is available on [GitHub](https://github.com/fusion-energy/regular_mesh_plotter).

            👉 Run an OpenMC simulation with a 3D tally containing a RegularMesh filter.
        """
    )
    statepoint_file = st.file_uploader(
        "Upload your statepoint file", type=["h5"], key="statepoint_uploader"
    )

    # TODO add image of 3d regular mesh
    # col2.image("image.png", use_column_width="always")

    if statepoint_file == None:
        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 30px;">Upload your statepoint h5 file</p>'
        st.markdown(new_title, unsafe_allow_html=True)

        st.markdown(
            'Not got statepoint.h5 files handy? Download sample [statepoint.h5](https://github.com/fusion-energy/openmc_plot/raw/adding_statepoint_example_file/examples/regularmesh_plot/statepoint.40.h5 "download")'
        )

    else:

        save_uploadedfile(statepoint_file)

        # loads up the output file from the simulation
        statepoint = openmc.StatePoint(statepoint_file.name)

        # finds all the tallies that have a regular mesh and gets their ID,
        # score and mesh ID. These are used to make the "tally to plot" dropdown
        tally_description = []
        for id, tally in statepoint.tallies.items():
            for filter in tally.filters:
                if isinstance(filter, openmc.filter.MeshFilter):
                    mesh = filter.mesh
                    if isinstance(mesh, openmc.mesh.RegularMesh):
                        for score in tally.scores:
                            tally_description.append(
                                f"ID={tally.id} score={score} mesh_ID={mesh.id}"
                            )

        col1, col2 = st.columns([1, 3])

        tally_description_to_plot = col1.selectbox(
            label="Tally to plot", options=tally_description, index=0
        )
        tally_id_to_plot = tally_description_to_plot.split(" ")[0][3:]
        tally_score_to_plot = tally_description_to_plot.split(" ")[1][6:]

        my_tally = statepoint.get_tally(id=int(tally_id_to_plot))

        axis_to_slice = col1.selectbox(
            label="Slice plane", options=("X", "Y", "Z"), index=0
        )

        tally_or_std = col1.radio(
            "Tally value or std dev", options=["value", "std dev"]
        )

        if tally_or_std == "value":
            plotted_part_of_tally = my_tally.mean.flatten()
            cbar_label = tally_score_to_plot
        else:  # 'std dev'
            plotted_part_of_tally = my_tally.std_dev.flatten()
            cbar_label = f"standard deviation {tally_score_to_plot}"

        reshaped_tally = plotted_part_of_tally.reshape(mesh.dimension, order="F")

        if axis_to_slice == "X":
            tally_aligned = reshaped_tally.transpose(1, 2, 0)
            bb_index = 0
            x_label = "Y [cm]"
            y_label = "Z [cm]"
        elif axis_to_slice == "Y":
            tally_aligned = reshaped_tally.transpose(
                0, 1, 2
            )
            bb_index = 1
            x_label = "X [cm]"
            y_label = "Z [cm]"
        else:  # axis_to_slice == 'Z':
            tally_aligned = reshaped_tally.transpose(2, 0, 1)
            bb_index = 2
            x_label = "X [cm]"
            y_label = "Y [cm]"

        left = mesh.lower_left[bb_index]
        right = mesh.upper_right[bb_index]
        bottom = mesh.lower_left[bb_index]
        top = mesh.upper_right[bb_index]

        slice_value = col1.slider(
            label="slice index",
            min_value=0,
            max_value=len(tally_aligned) - 1,
            value=int(len(tally_aligned) / 2),
        )

        log_lin_scale = col1.radio("Normalization", options=["log", "linear"])
        if log_lin_scale == "linear":
            norm = None
        else:
            norm = LogNorm()

        image_slice = tally_aligned[slice_value]

        if axis_to_slice == "Y":
            mpl_image_slice = np.rot90(image_slice)
            plotly_image_slice = np.rot90(image_slice, 3)
        if axis_to_slice == "Z":
            mpl_image_slice = np.rot90(image_slice)
            plotly_image_slice = np.rot90(image_slice, 1)
        if axis_to_slice == "X":
            mpl_image_slice = np.flipud(image_slice)
            plotly_image_slice = image_slice

        col_mpl, col_plotly = col2.tabs(
            ["📉 MatplotLib image", "📈 Plotly interactive plot"]
        )
        with col_mpl:

            plt.cla()
            plt.clf()

            plt.axes(title="Tally value", xlabel=x_label, ylabel=y_label)
            # could be assigned like this
            # plt.xlabel(x_label)
            # plt.ylabel(y_label)
            # plt.title('Tally value')

            plt.imshow(X=mpl_image_slice, extent=(left, right, bottom, top), norm=norm)
            plt.colorbar(label=cbar_label)

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
                        x0 =left,
                        dx=abs(left-right)/(len(plotly_image_slice[0])-1),
                        y0 =bottom,
                        dy=abs(bottom-top)/(len(plotly_image_slice)-1),
                        showscale=False  # avoids the color bar not being log scale
                        ),
                    )
            else:
                figure = go.Figure(
                    data=go.Heatmap(
                        z=plotly_image_slice,
                        colorscale='viridis',
                        x0 =left,
                        dx=abs(left-right)/(len(plotly_image_slice[0])-1),
                        y0 =bottom,
                        dy=abs(bottom-top)/(len(plotly_image_slice)-1),
                        colorbar=dict(title=dict(side="right", text=cbar_label)),
                        ),
                    )
                

            figure.update_layout(
                xaxis={"title": x_label},
                yaxis={"title": y_label},
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
