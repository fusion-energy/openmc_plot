import streamlit as st
from utils import save_uploadedfile
import openmc
import openmc_source_plotter


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
            'Not got xml files handy? Download sample [settings.xml](https://raw.githubusercontent.com/fusion-energy/openmc_plot/main/examples/ring_source/settings.xml)'
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

        for old_source in my_settings.source:
            new_source = openmc.Source()
            if old_source.angle is not None:
                new_source.angle = old_source.angle
            if old_source.space is not None:
                new_source.space = old_source.space
            if old_source.energy is not None:
                new_source.energy = old_source.energy

            if type_of_source_plot == "Energy":
                fig = new_source.plot_source_energy(figure=fig, n_samples=n_samples)
            if type_of_source_plot == "Angle":
                fig = new_source.plot_source_direction(figure=fig, n_samples=n_samples)
            if type_of_source_plot == "Space":
                fig = new_source.plot_source_position(figure=fig, n_samples=n_samples)

        col2.plotly_chart(fig)

        fig.write_html('openmc_plot_source_image.html')

        with open("openmc_plot_source_image.html", "rb") as file:
            col1.download_button(
                label="Download image",
                data=file,
                file_name="openmc_plot_source_image.html",
                mime=None
            )
