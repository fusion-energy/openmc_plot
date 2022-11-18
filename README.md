A Python app for plotting OpenMC geometry.

This repository contains part of the source code for the OpenMC geometry plotting app which is part of the website [xsplot.com](http://xsplot.com)

This repository contains:
- A Python [Streamlit](https://streamlit.io) based GUI 🐍
- A Dockerfile that provides the hosting environment for the web app 🐳


# Install

OpenMC_plot can be install directly from PyPi using pip.

```
pip install openmc_plot
```

# Usage

In the terminal type ...

```
openmc_plot
```

Your default web browser should then load with the GUI.

# Run web app locally

You can view the hosted version of this repository here [xsplot.com](http://xsplot.com). However you might want to host your own version locally.

To host your own local version of [xsplot.com](http://xsplot.com) you will need [Docker](https://www.docker.com/) installed and then can build and run the Dockerfile
with the following commands.

First clone the repository
```bash
git clone https://github.com/fusion-energy/openmc_plot
```

Then navigate into the repository folder
```bash
cd openmc_plot
```

Then build the docker image
```bash
docker build -t openmc_plot .
```

Then run the docker image
```bash
docker run --network host -t openmc_plot
```

The URL of your locally hosted version should appear in the terminal, copy and paste this URL into a web browser address bar.

# Maintenance

Pushing to the main branch of this repository triggers an automatic rebuild and
deployment of the new code using Google Cloud build at [xsplot.com](http://xsplot.com)
