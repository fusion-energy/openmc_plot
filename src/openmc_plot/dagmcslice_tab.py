import streamlit as st
from utils import save_uploadedfile
import openmc
from dagmc_geometry_slice_plotter import plot_axis_slice


def create_dagmcslice_tab():

    st.write(
        """
            This tab makes use of the 🐍 Python package ```dagmc_geometry_slice_plotter``` which is available on [GitHub](https://github.com/fusion-energy/dagmc_geometry_slice_plotter).

            👉 Create your ```dagmc.h5m``` file using one of the methods listed in on the [DAGMC tools discussion](https://github.com/svalinn/DAGMC/discussions/812):
        """
    )
    dagmc_h5m_file = st.file_uploader("Upload your dagmc.h5m file", type=["h5m"])

    if dagmc_h5m_file == None:
        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 30px;">Upload your geometry.xml</p>'
        st.markdown(new_title, unsafe_allow_html=True)

        st.markdown(
            'Not got h5m files handy? Download sample [dagmc.xml](https://raw.githubusercontent.com/fusion-energy/openmc_plot/main/examples/dagmc_geometry/dagmc_text.h5m "download")'
        )

    else:
    
        save_uploadedfile(dagmc_h5m_file)
        
        dagunv = openmc.DAGMCUniverse(dagmc_h5m_file.name).bounded_universe()
        bb = dagunv.bounding_box

        col1, col2 = st.columns([1, 3])

        view_direction = col1.selectbox(
            label="View Direction",
            options=('-z', 'z', '-x', 'x', '-y', 'y'),
            index=0
        )
        
        if view_direction in ['-x', 'x']:
            x_offset = col1.slider(
                    label="X axis offset",
                    min_value=float(bb[0][0]),
                    max_value=float(bb[1][0]),
                    value=float((bb[0][0] + bb[1][0]) / 2),
                )
        else:
            x_offset = float((bb[0][0] + bb[1][0]) / 2)
            
        if view_direction in ['-y', 'y']:
            y_offset = col1.slider(
                    label="Y axis offset",
                    min_value=float(bb[0][1]),
                    max_value=float(bb[1][1]),
                    value=float((bb[0][1] + bb[1][1]) / 2),
                )
        else:
            y_offset = float((bb[0][1] + bb[1][1]) / 2)

        if view_direction in ['-z', 'z']:
            z_offset = col1.slider(
                    label="Z axis offset",
                    min_value=float(bb[0][2]),
                    max_value=float(bb[1][2]),
                    value=float((bb[0][2] + bb[1][2]) / 2),
                )
        else:
            z_offset = float((bb[0][2] + bb[1][2]) / 2)

        dag_plt = plot_axis_slice(
            dagmc_file_or_trimesh_object=dagmc_h5m_file.name,
            view_direction=view_direction,
            plane_origin=[x_offset, y_offset, z_offset]
        )
        col2.pyplot(dag_plt)
        
        dag_plt.savefig("openmc_plot_dagmc_slice_image.png")

        with open("openmc_plot_dagmc_slice_image.png", "rb") as file:
            col1.download_button(
                label="Download image",
                data=file,
                file_name="openmc_plot_dagmc_slice_image.png",
                mime="image/png"
            )

