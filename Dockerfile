# A Docker image for hosting the openmc_plot web app at https://www.xsplot.com

# build with
# docker build -t openmc_plot .

# run with
# docker run --network host -t openmc_plot

# maintained at https://github.com/fusion_energy/openmc_plot.com/

FROM continuumio/miniconda3:4.12.0

RUN conda install -c conda-forge openmc==0.13.3

# Could be used to make matplotlib in streamlit interactive
# see https://blog.streamlit.io/make-your-st-pyplot-interactive/
# RUN pip install mpld3
RUN pip install "openmc_source_plotter>=0.6.2"
RUN pip install "dagmc_geometry_slice_plotter>=0.3.1"
RUN pip install "openmc_geometry_plot>=0.3.5"
RUN pip install "regular_mesh_plotter>=0.5.3"
RUN pip install "openmc_depletion_plotter>=0.3.1"
RUN pip install "openmc_cylindrical_mesh_plotter>=0.1.2"


COPY src/* /
# optional copy
# COPY .streamlit/config.toml .streamlit/config.toml

ENV PORT 8501

EXPOSE 8501

ENV OPENMC_PLOT_LOCATION cloud

# solves bug of streamlit not running in container
# https://github.com/streamlit/streamlit/issues/4842
ENTRYPOINT [ "streamlit", "run" ]
CMD [ "app.py", "--server.headless", "true", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"]
