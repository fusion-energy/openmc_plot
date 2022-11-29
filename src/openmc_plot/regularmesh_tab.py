import streamlit as st
from utils import save_uploadedfile
import openmc
import matplotlib.pyplot as plt
from pylab import *
from matplotlib.colors import LogNorm


def create_regularmesh_tab():
    st.write(
        """
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
            image_slice = np.rot90(image_slice)
        if axis_to_slice == "Z":
            image_slice = np.rot90(image_slice)
        if axis_to_slice == "X":
            image_slice = np.flipud(image_slice)

        plt.cla()
        plt.clf()

        plt.axes(title="Tally value", xlabel=x_label, ylabel=y_label)
        # could be assigned like this
        # plt.xlabel(x_label)
        # plt.ylabel(y_label)
        # plt.title('Tally value')

        plt.imshow(X=image_slice, extent=(left, right, bottom, top), norm=norm)
        plt.colorbar(label=cbar_label)
        col2.pyplot(plt)

        plt.savefig('openmc_plot_regularmesh_image.png')
        with open("openmc_plot_regularmesh_image.png", "rb") as file:
            col1.download_button(
                label="Download image",
                data=file,
                file_name="openmc_plot_regularmesh_image.png",
                mime="image/png"
            )
