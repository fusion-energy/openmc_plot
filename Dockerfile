# A Docker image for hosting the openmc_plot web app at https://www.xsplot.com

# build with
# docker build -t openmc_plot .

# run with
# docker run --network host -t openmc_plot

# maintained at https://github.com/fusion_energy/openmc_plot.com/

FROM continuumio/miniconda3:4.12.0

RUN conda install -c conda-forge openmc

RUN pip install streamlit
# Could be used to make mpl interactive
# see https://blog.streamlit.io/make-your-st-pyplot-interactive/
# RUN pip install mpld3
RUN pip install openmc_source_plotter>=0.6.2
RUN pip install dagmc_geometry_slice_plotter>=0.2.0

COPY src/openmc_plot/app.py .
COPY src/openmc_plot/header.py .
COPY src/openmc_plot/geometry_tab.py .
COPY src/openmc_plot/source_tab.py .
COPY src/openmc_plot/regularmesh_tab.py .
COPY src/openmc_plot/weightwindows_tab.py .
COPY src/openmc_plot/dagmcslice_tab.py .
COPY src/openmc_plot/utils.py .
COPY src/openmc_plot/cross_sections.xml .
# optional copy
# COPY .streamlit/config.toml .streamlit/config.toml

ENV PORT 8501

EXPOSE 8501


# solves bug of streamlit not running in container
# https://github.com/streamlit/streamlit/issues/4842
ENTRYPOINT [ "streamlit", "run" ]
CMD [ "app.py", "--server.headless", "true", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"]
