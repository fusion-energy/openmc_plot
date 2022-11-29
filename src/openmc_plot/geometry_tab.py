import streamlit as st
from utils import save_uploadedfile
import xml.etree.ElementTree as ET
import openmc
import matplotlib.pyplot as plt
from pylab import *
import xml.etree.ElementTree as ET


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
        else:
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
        else:
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
                # todo add
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
        geom_plt.figure.savefig("openmc_plot_geometry_image.png")

        col2.image("openmc_plot_geometry_image.png", use_column_width="always")

        with open("openmc_plot_geometry_image.png", "rb") as file:
            col1.download_button(
                label="Download image",
                data=file,
                file_name="openmc_plot_geometry_image.png",
                mime="image/png"
            )

