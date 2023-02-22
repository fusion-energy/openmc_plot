import os
import runpy
import sys
import openmc_plot
from pathlib import Path


def main():

    path_to_app = str(Path(openmc_plot.__path__[0])/'app.py')

    # default is 200MB, this sets uplod file zise to 100GB
    os.environ['STREAMLIT_SERVER_MAX_UPLOAD_SIZE'] = '100000'

    sys.argv = ["streamlit", "run", path_to_app]; 
    runpy.run_module("streamlit", run_name="__main__")


if __name__ == "__main__":
    main()
