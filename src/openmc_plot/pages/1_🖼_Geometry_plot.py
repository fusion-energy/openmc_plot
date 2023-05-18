import xml.etree.ElementTree as ET
from pathlib import Path
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import openmc
import streamlit as st
from matplotlib import colors
from pylab import cm, colormaps
import numpy as np

import openmc_geometry_plot  # adds extra functions to openmc.Geometry

from utils import save_uploadedfile


def header():
    st.write(
        f"""This tab makes use of the 🐍 Python package ```openmc_geometry_plot v{openmc_geometry_plot.__version__}``` which is available on [GitHub](https://github.com/fusion-energy/openmc_geometry_plot)."""
    )

header()
openmc_geometry_plot.main()
