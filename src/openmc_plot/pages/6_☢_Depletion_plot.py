import streamlit as st
from utils import save_uploadedfile
import openmc
import openmc_depletion_plotter

st.write(
    f"""
        This tab makes use of the 🐍 Python package ```openmc_depletion_plottter {openmc_depletion_plotter.__version__}``` which is available on [GitHub](https://github.com/fusion-energy/openmc_depletion_plottter).
    """
)
openmc_depletion_plotter.main()
