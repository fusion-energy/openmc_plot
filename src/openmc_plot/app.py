import streamlit as st
import openmc
import openmc_source_plotter
import matplotlib.pyplot as plt
from pylab import *
import xml.etree.ElementTree as ET
from matplotlib.colors import LogNorm


def save_uploadedfile(uploadedfile):
    with open(uploadedfile.name, "wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success(f"Saved File to {uploadedfile.name}")


def header():

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

            🐍 Run this app locally with Python ```pip install openmc_plot``` then run with ```openmc_plot```

            💾 Raise a feature request, report and issue or make a contribution on [GitHub](https://github.com/fusion-energy/openmc_plot)

            📧 Email feedback to mail@jshimwell.com
        """
    )
    st.write("<br>", unsafe_allow_html=True)


def create_geometry_tab():

    st.write(
        """
            👉 Create your ```openmc.Geometry()``` and export the geometry xml file using ```export_to_xml()```.
        """
    )
    geometry_xml_file = st.file_uploader("Upload your geometry.xml", type=["xml"])

    if geometry_xml_file == None:
        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 30px;">Upload your geometry.xml</p>'
        st.markdown(new_title, unsafe_allow_html=True)

        st.markdown(
            'Not got xml files handy? Download sample [geometry.xml](https://raw.githubusercontent.com/fusion-energy/openmc_plot/main/examples/tokamak/geometry.xml "download")'
        )

    else:

        save_uploadedfile(geometry_xml_file)

        tree = ET.parse(geometry_xml_file.name)

        root = tree.getroot()
        all_cells = root.findall("cell")
        mat_ids = []
        for cell in all_cells:
            if "material" in cell.keys():
                if cell.get("material") == "void":
                    print(f"material for cell {cell} is void")
                else:
                    mat_ids.append(int(cell.get("material")))

        if len(mat_ids) >= 1:
            set_mat_ids = set(mat_ids)
        else:
            set_mat_ids = ()

        my_mats = []
        for mat_id in set_mat_ids:
            new_mat = openmc.Material()
            new_mat.id = mat_id
            new_mat.add_nuclide("Li6", 1)
            # adds a single nuclide that is in minimal cross section xml to avoid material failing
            my_mats.append(new_mat)

        my_geometry = openmc.Geometry.from_xml(
            path=geometry_xml_file.name, materials=my_mats
        )

        my_universe = my_geometry.root_universe

        bb = my_universe.bounding_box

        col1, col2 = st.columns([1, 3])

        option = col1.selectbox(label="Axis basis", options=("XZ", "XY", "YZ"), index=0)

        # bb may have -inf or inf values in, these break the slider bar automatic scaling
        if np.isinf(bb[0][0]) or np.isinf(bb[1][0]):
            msg = "Infinity value found in X axis, axis length can't be automatically found. Input desired Z axis length"
            x_width = col1.number_input(msg, value=1.0)
            x_offset = col1.number_input("X axis offset")
        x_width = abs(bb[0][0] - bb[1][0])
        x_offset = col1.slider(
            label="X axis offset",
            min_value=float(bb[0][0]),
            max_value=float(bb[1][0]),
            value=float((bb[0][0] + bb[1][0]) / 2),
        )

        if np.isinf(bb[0][1]) or np.isinf(bb[1][1]):
            msg = "Infinity value found in Y axis, axis length can't be automatically found. Input desired Z axis length"
            y_width = col1.number_input(msg, value=1.0)
            y_offset = col1.number_input("Y axis offset")
        y_width = abs(bb[0][1] - bb[1][1])
        y_offset = col1.slider(
            label="Y axis offset",
            min_value=float(bb[0][1]),
            max_value=float(bb[1][1]),
            value=float((bb[0][1] + bb[1][1]) / 2),
        )

        if np.isinf(bb[0][2]) or np.isinf(bb[1][2]):
            msg = "Infinity value found in Z axis, axis length can't be automatically found. Input desired Z axis length"
            z_width = col1.number_input(msg, value=1.0)
            z_offset = col1.number_input("Z axis offset")
        else:
            z_width = abs(bb[0][2] - bb[1][2])
            z_offset = col1.slider(
                label="Z axis offset",
                min_value=float(bb[0][2]),
                max_value=float(bb[1][2]),
                value=float((bb[0][2] + bb[1][2]) / 2),
            )

        if option == "XZ":
            plot_width_bb = x_width
            plot_height_bb = z_width
            xlabel = "X [cm]"
            ylabel = "Z [cm]"
        elif option == "XY":
            plot_width_bb = x_width
            plot_height_bb = y_width
            xlabel = "X [cm]"
            ylabel = "Y [cm]"
        elif option == "YZ":
            plot_width_bb = y_width
            plot_height_bb = z_width
            xlabel = "Y [cm]"
            ylabel = "Z [cm]"

        plot_width = col1.number_input(
            label="Plot width (cm)",
            min_value=0.0,
            step=1.0,
            value=plot_width_bb,
        )

        plot_height = col1.number_input(
            label="Plot height (cm)",
            min_value=0.0,
            step=1.0,
            value=plot_height_bb,
        )
        global plt
        base_plot = plt.axes(xlabel=xlabel, ylabel=ylabel)
        aspect_ratio = plot_width / plot_height

        pixels_width = col1.number_input(
            "Image resolution (pixels in width)", min_value=10, value=1500
        )

        color_by = st.radio("Color by options", options=["cell", "material"])

        if color_by == "material":
            cmap = cm.get_cmap("viridis", len(my_mats))

            initial_hex_color = []
            for i in range(cmap.N):
                rgba = cmap(i)
                # rgb2hex accepts rgb or rgba
                initial_hex_color.append(matplotlib.colors.rgb2hex(rgba))

            my_colors = {}
            for c, id in enumerate(set_mat_ids):
                st.color_picker(
                    f"Color of material with id {id}",
                    key=f"mat_{id}",
                    value=initial_hex_color[c],
                )

            for material in my_mats:
                hex_color = st.session_state[f"mat_{material.id}"].lstrip("#")
                RGB = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
                my_colors[material] = RGB
            if len(set_mat_ids) == 0:
                col1.write("No material IDs found in the geometry.xml")

        elif color_by == "cell":
            my_cells = my_universe.cells
            my_cells_ids = my_universe.cells.keys()
            cmap = cm.get_cmap("viridis", len(my_cells))

            initial_hex_color = []
            for i in range(cmap.N):
                rgba = cmap(i)
                # rgb2hex accepts rgb or rgba
                initial_hex_color.append(matplotlib.colors.rgb2hex(rgba))

            my_colors = {}
            for c, cell_id in enumerate(my_cells_ids):
                st.color_picker(
                    f"Color of cell {cell_id}",
                    key=f"cell_{cell_id}",
                    value=initial_hex_color[c],
                )

            for cell, cell_id in zip(my_cells, my_cells_ids):
                hex_color = st.session_state[f"cell_{cell_id}"].lstrip("#")
                RGB = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
                my_colors[cell] = RGB

        else:  # random selected
            my_colors = None

        pixels_height = int(1500 / aspect_ratio)

        geom_plt = my_universe.plot(
            width=(plot_width, plot_height),
            basis=option.lower(),
            origin=(x_offset, y_offset, z_offset),
            axes=base_plot,
            pixels=(pixels_width, pixels_height),
            colors=my_colors,
            color_by=color_by,
        )
        geom_plt.figure.savefig("image.png")
        col2.image("image.png", use_column_width="always")


def create_source_tab():

    st.write(
        """
            👉 Create your ```openmc.Settings()``` assign the Source and export the settings xml file using ```export_to_xml()```.
        """
    )
    settings_xml_file = st.file_uploader(
        "Upload your settings.xml", type=["xml"], key="settings_uploader"
    )

    if settings_xml_file == None:
        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 30px;">Upload your settings.xml</p>'
        st.markdown(new_title, unsafe_allow_html=True)

        st.markdown(
            'Not got xml files handy? Download sample [settings.xml](https://github.com/fusion-energy/openmc_plot/blob/main/examples/ring_source/settings.xml "download")'
        )

    else:

        save_uploadedfile(settings_xml_file)

        my_settings = openmc.Settings.from_xml(settings_xml_file.name)

        col1, col2 = st.columns([1, 3])

        type_of_source_plot = col1.radio(
            "Select type of plot", options=["Energy", "Space", "Angle"]
        )

        n_samples = col1.number_input(
            label="number of samples",
            min_value=1,
            step=1,
            value=1000,
        )

        fig = None

        if type_of_source_plot == "Energy":

            for old_source in my_settings.source:

                new_source = openmc.Source()
                new_source.energy = old_source.energy

                fig = new_source.plot_source_energy(figure=fig, n_samples=n_samples)

        if type_of_source_plot == "Angle":

            for old_source in my_settings.source:

                new_source = openmc.Source()
                new_source.angle = old_source.angle
                new_source.space = old_source.space
                new_source.energy = old_source.energy

                fig = new_source.plot_source_direction(figure=fig, n_samples=n_samples)

        if type_of_source_plot == "Space":

            for old_source in my_settings.source:

                new_source = openmc.Source()
                new_source.space = old_source.space

                fig = new_source.plot_source_position(figure=fig, n_samples=n_samples)

        col2.plotly_chart(fig)


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

    if statepoint_file == None:
        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 30px;">Upload your statepoint h5 file</p>'
        st.markdown(new_title, unsafe_allow_html=True)

        # TODO make a small statepoint file for the repo
        # st.markdown(
        #     'Not got statepoint.h5 files handy? Download sample [statepoint.h5](https://github.com/fusion-energy/openmc_plot/blob/main/examples/regularmesh_tally/statepoint.40.h5 "download")'
        # )

    else:

        save_uploadedfile(statepoint_file)

        # loads up the output file from the simulation
        statepoint = openmc.StatePoint(statepoint_file.name)

        tally_description = []
        # TODO allow multiple tallies and multiple scores
        for id, tally in statepoint.tallies.items():
            print(tally)
            for filter in tally.filters:
                print(filter)
                if isinstance(filter, openmc.filter.MeshFilter):
                    mesh = filter.mesh
                    if isinstance(mesh, openmc.mesh.RegularMesh):
                        for score in tally.scores:
                            tally_description.append(
                                f"ID={tally.id} score={score} mesh_ID={mesh.id}"
                            )
                        # tally_score = tally.scores[0]
                        break

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
            )  # todo find correct numbers
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
        plt.imshow(X=image_slice, extent=(left, right, bottom, top), norm=norm)
        # plt.xlabel(x_label)
        # plt.ylabel(y_label)
        # plt.title('Tally value')
        plt.colorbar(label=cbar_label)
        col2.pyplot(plt)


def main():

    header()

    geometry_tab, source_tab, regularmesh_tab = st.tabs(
        ["🖼 Geometry plot", "✴️ Source Plot", "🧊 Regular Mesh Plot"]
    )
    with geometry_tab:
        create_geometry_tab()
    with source_tab:
        create_source_tab()
    with regularmesh_tab:
        create_regularmesh_tab()


if __name__ == "__main__":
    main()
