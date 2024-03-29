import streamlit as st
from utils import save_uploadedfile
import xml.etree.ElementTree as ET
import openmc
import matplotlib.pyplot as plt
from pylab import *
import xml.etree.ElementTree as ET
from matplotlib.colors import LogNorm


st.write(
    """
        👉 Create your ```openmc.WeightWindows()``` and export the settings xml file using ```export_to_xml()```.

        Weight windows on RegularMesh and CylindricalMesh are supported
    """
)
settings_xml_file = st.file_uploader("Upload your settings.xml", type=["xml"])

if settings_xml_file == None:
    new_title = '<p style="font-family:sans-serif; color:Red; font-size: 30px;">Upload your settings.xml</p>'
    st.markdown(new_title, unsafe_allow_html=True)

    st.write(
        """
            Not got a settings xml file handy, right mouse 🖱️ click and save these links 
            [ example 1 ](https://fusion-energy.github.io/openmc_plot/examples/weightwindows/settings.xml)
        """
    )
else:
    save_uploadedfile(settings_xml_file)

    my_settings = openmc.Settings.from_xml(settings_xml_file.name)

    weight_windows = my_settings.weight_windows

    if weight_windows == []:
        msg = f"{settings_xml_file.name} does not contain weight windows"
        new_title = (
            f'<p style="font-family:sans-serif; color:Red; font-size: 30px;">{msg}</p>'
        )
        st.markdown(new_title, unsafe_allow_html=True)

    else:
        weight_window_by_id = {}
        for weight_window in weight_windows:
            weight_window_by_id[weight_window.id] = weight_window

        if len(weight_window_by_id.keys()) > 1:
            weight_window_selector = st.sidebar.selectbox(
                label="Weight window ID to plot",
                options=weight_window_by_id.keys(),
                index=0,
            )
        else:
            weight_window_selector = list(weight_window_by_id.keys())[0]

        selected_weight_window = weight_window_by_id[weight_window_selector]

        upper_or_lower = st.sidebar.radio(
            "upper or lower bounds", options=["upper bounds", "lower bounds"]
        )
        if upper_or_lower == "upper bounds":
            plotted_part_of_weight_window = (
                selected_weight_window.upper_ww_bounds.flatten()
            )
        else:
            plotted_part_of_weight_window = (
                selected_weight_window.lower_ww_bounds.flatten()
            )

        mesh = selected_weight_window.mesh

        if isinstance(mesh, openmc.CylindricalMesh):
            reshaped_tally = plotted_part_of_weight_window.reshape(
                mesh.dimension, order="F"
            )

            # TODO add XY top down slice
            # axis_to_slice = st.sidebar.selectbox(
            #     label="Slice plane", options=("RZ", "XY"), index=0, key='ww_axis_to_slice'
            # )
            axis_to_slice = "RZ"

            reshaped_tally = plotted_part_of_weight_window.reshape(
                (mesh.dimension[2], mesh.dimension[1], mesh.dimension[0]), order="F"
            )

            tally_aligned = reshaped_tally.transpose(2, 0, 1)
            x_label = "R [cm]"
            y_label = "Z [cm]"

            left = mesh.r_grid[0]
            right = mesh.r_grid[-1]
            bottom = mesh.z_grid[0]
            top = mesh.z_grid[-1]

            slice_value = st.sidebar.slider(
                label="slice index",
                min_value=0,
                max_value=len(mesh.phi_grid) - 1,
                value=int(len(mesh.phi_grid) / 2),
            )

        elif isinstance(mesh, openmc.RegularMesh):
            reshaped_tally = plotted_part_of_weight_window.reshape(
                mesh.dimension, order="F"
            )

            axis_to_slice = st.sidebar.selectbox(
                label="Slice plane",
                options=("X", "Y", "Z"),
                index=0,
                key="ww_axis_to_slice",
            )

            if axis_to_slice == "X":
                tally_aligned = reshaped_tally.transpose(1, 2, 0)
                bb_index = 0
                x_label = "Y [cm]"
                y_label = "Z [cm]"
            elif axis_to_slice == "Y":
                tally_aligned = reshaped_tally.transpose(0, 1, 2)
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

            slice_value = st.sidebar.slider(
                label="slice index",
                min_value=0,
                max_value=len(tally_aligned) - 1,
                value=int(len(tally_aligned) / 2),
            )

        log_lin_scale = st.sidebar.radio(
            "Normalization", options=["log", "linear"], key="ww_log_lin_scale"
        )
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
        # if axis_to_slice == "RZ":
        #     image_slice = np.flipud(image_slice)

        plt.cla()
        plt.clf()

        plt.axes(
            title=f"Weight window {upper_or_lower}", xlabel=x_label, ylabel=y_label
        )
        # could be assigned like this
        # plt.xlabel(x_label)
        # plt.ylabel(y_label)
        # plt.title('Tally value')
        if np.amax(image_slice) == np.amin(image_slice) and norm is not None:
            msg = "slice contains the uniform values, can't be plotted on log scale"
            format = f'<p style="font-family:sans-serif; color:Red; font-size: 30px;">{msg}</p>'
            st.markdown(format, unsafe_allow_html=True)
        else:
            plt.imshow(X=image_slice, extent=(left, right, bottom, top), norm=norm)
            plt.colorbar(label=upper_or_lower)
            st.pyplot(plt)
            plt.savefig("openmc_plot_weightwindow_image.png")

            with open("openmc_plot_weightwindow_image.png", "rb") as file:
                st.sidebar.download_button(
                    label="Download image",
                    data=file,
                    file_name="openmc_plot_weightwindow_image.png",
                    mime="image/png",
                )
