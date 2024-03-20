import streamlit as st
import openmc_geometry_plot

def header():
    st.write(
        f"""This tab makes use of the 🐍 Python package ```openmc_geometry_plot v{openmc_geometry_plot.__version__}``` which is available separately on [GitHub](https://github.com/fusion-energy/openmc_geometry_plot)."""
    )

header()
openmc_geometry_plot.main()
