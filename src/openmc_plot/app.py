import streamlit as st
import openmc
import os

from pathlib import Path

# assigns a minimal cross section xml file
# this means the user does not need to set the environment variable
# the h5 files are not actually needed as we are only plotting
cross_section_path = Path(__file__).parent.resolve() / "cross_sections.xml"
openmc.config["cross_sections"] = cross_section_path

st.set_page_config(
    layout="wide",
    page_icon="⚛",
    page_title="OpenMC Plot",
)


st.sidebar.success("Select a plot above.")


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {
                visibility: hidden;
                }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

version = "v0.3.1"
location = os.getenv("OPENMC_PLOT_LOCATION")

if location == "cloud":
    st.write(
        f"""
            # OpenMC plot ```{version}```

            ## A plotting tool for OpenMC.

            ### ⚡ Install this app locally for faster performance and improved stability.
            
            ### 🐍 Install with Python ```pip install openmc_plot``` then run with ```openmc_plot```

            💾 Raise a feature request, report and issue or make a contribution on [GitHub](https://github.com/fusion-energy/openmc_plot)

        """
    )
else:
    st.write(
        f"""
            # OpenMC plot ```{version}```

            ### A plotting tool for OpenMC.
            
            👈 Select a plotting app from the sidebar on the left to get started.

            💾 Raise a feature request, report and issue or make a contribution on [GitHub](https://github.com/fusion-energy/openmc_plot).

            📧 Email feedback to mail@jshimwell.com
            
            ⭐ If you like this project we appreciate a star on the [GitHub repository](https://github.com/fusion-energy/openmc_plot/stargazers).
        """
    )
st.write("<br>", unsafe_allow_html=True)
