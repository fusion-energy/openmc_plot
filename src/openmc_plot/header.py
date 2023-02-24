import streamlit as st
import os


def header():
    """This section writes out the page header common to all tabs"""

    st.set_page_config(
        page_title="OpenMC Plot",
        page_icon="⚛",
        layout="wide",
    )

    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {
                    visibility: hidden;
                    }
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    version = "v0.2.2"
    location = os.getenv("OPENMC_PLOT_LOCATION")

    if location == "cloud":
        st.write(
            f"""
                # OpenMC plot ```{version}```

                ## ⚛ A plotting user interface for OpenMC.

                ### ⚡ Install this app locally for faster performance and improved stability.
                
                ### 🐍 Install with Python ```pip install openmc_plot``` then run with ```openmc_plot```

                💾 Raise a feature request, report and issue or make a contribution on [GitHub](https://github.com/fusion-energy/openmc_plot)

                📧 Email feedback to mail@jshimwell.com
            """
        )
    else:
        st.write(
            f"""
                # OpenMC plot ```{version}```

                ### ⚛ A plotting user interface for OpenMC.

                💾 Raise a feature request, report and issue or make a contribution on [GitHub](https://github.com/fusion-energy/openmc_plot)

                📧 Email feedback to mail@jshimwell.com
            """
        )
    st.write("<br>", unsafe_allow_html=True)
