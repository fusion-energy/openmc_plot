import streamlit as st
from utils import save_uploadedfile
import openmc
import dagmc_geometry_slice_plotter
from dagmc_geometry_slice_plotter import main

st.write(
    f"""
        This tab makes use of the 🐍 Python package ```dagmc_geometry_slice_plotter v{dagmc_geometry_slice_plotter.__version__}``` which is available on [GitHub](https://github.com/fusion-energy/dagmc_geometry_slice_plotter).

        👉 Create your ```dagmc.h5m``` file using one of the methods listed in on the [DAGMC tools discussion](https://github.com/svalinn/DAGMC/discussions/812):
    """
)

main()
