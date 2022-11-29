import streamlit as st
from utils import save_uploadedfile
import xml.etree.ElementTree as ET
import openmc
import matplotlib.pyplot as plt
from pylab import *
import xml.etree.ElementTree as ET


def create_weightwindow_tab():

    st.write(
        """
            👉 Create your ```openmc.WeightWindows()``` and export the settings xml file using ```export_to_xml()```.
        """
    )
    settings_xml_file = st.file_uploader("Upload your settings.xml", type=["xml"])

    if settings_xml_file == None:
        new_title = '<p style="font-family:sans-serif; color:Red; font-size: 30px;">Upload your settings.xml</p>'
        st.markdown(new_title, unsafe_allow_html=True)

        st.markdown(
            'Not got xml files handy? Download sample [settings.xml]()'
        )

    else:

        save_uploadedfile(settings_xml_file)

        my_settings = openmc.Settings.from_xml(settings_xml_file.name)
        
        weight_windows = my_settings.weight_windows

        weight_window_by_id = {}
        for weight_window in weight_windows:
            weight_window_by_id[weight_window.id] = weight_window
        col1, col2 = st.columns([1, 3])

        weight_window_selector = col1.selectbox(
            label="Weight window ID to plot", options=weight_window_by_id.keys(), index=0
        )

        # plt.imshow(
        #     weight_windows[0].lower_ww_bounds[slice_index],
        #     origin='lower', extent=(llc[0], urc[0], llc[1], urc[1]), norm=LogNorm())
        # plt.title('lower_ww_bounds')
        # plt.colorbar()
