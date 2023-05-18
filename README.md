A Python app for plotting OpenMC.

This repository contains the source code for the OpenMC plot.

Try the web app at [http://openmc-plot.xsplot.com](http://openmc-plot.xsplot.com)

This repository contains:
- A Python [Streamlit](https://streamlit.io) based GUI 🐍
- A Dockerfile that provides the hosting environment for the web app 🐳

# Plot geometry
![openmc plot geometry](https://canada1.discourse-cdn.com/free1/uploads/openmc/original/2X/d/d7bcce794d51d34381371fc991c0e1ff2a65df08.gif)

# Plot sources
![openmc plot source](https://canada1.discourse-cdn.com/free1/uploads/openmc/original/2X/8/89f138350ace7b2bb0699dcb7ddfff49e336d051.gif)

# Plot regular mesh tallies
![openmc plot mesh](https://canada1.discourse-cdn.com/free1/uploads/openmc/original/2X/2/24a9db7bc9cc227908dbaf13a54d1245a4d16f20.gif)

# Plot weight windows
![openmc plot mesh](https://canada1.discourse-cdn.com/free1/uploads/openmc/original/2X/1/114aeb91172c7577e9231ffe30edf141678d26f6.gif)

# Plot cylindrical mesh tallies
![openmc cylinder mesh plot GUI](https://user-images.githubusercontent.com/8583900/228016577-d5d9f541-1b4d-4d9b-a207-f3f1d08e27a8.gif)

# Install

First you will need to [install OpenMC](https://docs.openmc.org/en/stable/quickinstall.html)

OpenMC_plot can then be install directly from the Python package index (PyPi) using pip.

```
pip install openmc_plot
```

# Usage

In the terminal type ...

```
openmc_plot
```

Your default web browser should then load with the GUI.

You will also need to have [OpenMC installed](https://docs.openmc.org/en/stable/quickinstall.html).

# Run web app locally (developers)

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

# Maintenance (developers)

Pushing to the main branch of this repository triggers an automatic rebuild and
deployment of the new code using Google Cloud build at [xsplot.com](http://xsplot.com)
