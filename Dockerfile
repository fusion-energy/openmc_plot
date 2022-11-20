
# build with
# docker build -t openmc_plot .

# run with
# docker run --network host -t openmc_plot

# maintained at https://github.com/fusion_energy/openmc_plot.com/

FROM continuumio/miniconda3:4.12.0

RUN conda install -c conda-forge openmc

RUN pip install openmc_data_downloader
RUN openmc_data_downloader -l FENDL-3.1d -i Li6
ENV OPENMC_CROSS_SECTIONS="/cross_sections.xml"
# include when logo exists
# COPY assets assets

RUN pip install streamlit
COPY src/openmc_plot/app.py .
COPY .streamlit/config.toml .streamlit/config.toml

ENV PORT 8501
# normally 8080 in dash apps

EXPOSE 8501
# normally 8080 in dash apps

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run
# to handle instance scaling. For more details see
# https://cloud.google.com/run/docs/quickstarts/build-and-deploy/python
# CMD streamlit run app.py --server.port=${PORT} --browser.serverAddress="0.0.0.0"

# solves bug of streamlit not running in container
# https://github.com/streamlit/streamlit/issues/4842
ENTRYPOINT [ "streamlit", "run" ]
CMD [ "app.py", "--server.headless", "true", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"]
