import streamlit as st
import openmc
import openmc_source_plotter
import matplotlib.pyplot as plt
from pylab import *
import xml.etree.ElementTree as ET
from matplotlib.colors import LogNorm
import pathlib
from header import header
from source_tab import create_source_tab
from geometry_tab import create_geometry_tab
from regularmesh_tab import create_regularmesh_tab

# assigns a minimal cross section xml file
# this means the user does not need to set the environment variable
# the h5 files are not actually needed as we are only plotting
cross_section_path = pathlib.Path(__file__).parent.resolve() / 'cross_sections.xml'
openmc.config['cross_sections'] = cross_section_path


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
