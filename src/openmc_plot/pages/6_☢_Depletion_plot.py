import streamlit as st
from utils import save_uploadedfile
import openmc
from openmc_depletion_plotter import main

st.write(
    """
        This tab makes use of the 🐍 Python package [openmc_depletion_plottter](https://github.com/fusion-energy/openmc_depletion_plottter) which is available on GitHub.
    """
)
main()
