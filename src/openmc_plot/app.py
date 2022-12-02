import streamlit as st
import openmc
from header import header
from source_tab import create_source_tab
from geometry_tab import create_geometry_tab
from regularmesh_tab import create_regularmesh_tab
from weightwindows_tab import create_weightwindow_tab
from dagmcslice_tab import create_dagmcslice_tab
from pathlib import Path

# assigns a minimal cross section xml file
# this means the user does not need to set the environment variable
# the h5 files are not actually needed as we are only plotting
cross_section_path = Path(__file__).parent.resolve() / 'cross_sections.xml'
openmc.config['cross_sections'] = cross_section_path


def main():

    header()

    geometry_tab, dagmcslice_tab, source_tab, regularmesh_tab, weightwindow_tab = st.tabs(
        ["🖼 Geometry plot", "🍕 DAGMC Slice Plot", "✴️ Source Plot", "🧊 Regular Mesh Plot", "🪟 Weight Windows Plot"]
    )
    with geometry_tab:
        create_geometry_tab()
    with dagmcslice_tab:
        create_dagmcslice_tab()
    with source_tab:
        create_source_tab()
    with regularmesh_tab:
        create_regularmesh_tab()
    with weightwindow_tab:
        create_weightwindow_tab()


if __name__ == "__main__":
    main()
