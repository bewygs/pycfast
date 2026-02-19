Installation
============

PyCFAST requires **Python 3.10 or later**. It fully supports **CFAST 7.7.5** and is
expected to be compatible with all **CFAST 7.7.x** versions.

Pip
---

PyCFAST can be installed from `PyPI <https://pypi.org/project/pycfast>`_::

    pip install pycfast

Conda
-----

PyCFAST can also be installed from the `conda-forge <https://anaconda.org/conda-forge/pycfast>`_ channel::

    conda install -c conda-forge pycfast

Source
------

To install the latest development version of PyCFAST, you can install from source, clone the repository and install the required dependencies::

    git clone https://github.com/bewygs/pycfast.git
    cd pycfast
    python -m pip install .

CFAST Installation
------------------

Download and install CFAST from the `NIST CFAST website <https://pages.nist.gov/cfast/>`_ or
the `CFAST GitHub repository <https://github.com/firemodels/cfast>`_. Follow the installation
instructions for your operating system and ensure ``cfast`` is available in your PATH. If 
CFAST is installed in a non-standard location, you can manually specify the path
with these methods.


- From an environment variable ``CFAST``::

    export CFAST="/path/to/your/cfast/executable"  # Linux/MacOS
    set CFAST="C:\path\to\your\cfast\executable"  # Windows (cmd)
    $env:CFAST="C:\path\to\your\cfast\executable"  # Windows (PowerShell)

- From Python code when defining the CFASTModel::

    import pycfast

    # set custom CFAST executable path via environment variable
    import os
    os.environ['CFAST'] = "/path/to/your/cfast/executable"

    # Or directly when defining CFASTModel
    model = pycfast.CFASTModel(cfast_path="/path/to/your/cfast/executable")
