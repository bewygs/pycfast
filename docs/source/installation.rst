Installation
============

PyCFAST requires **Python 3.10 or later**. It fully supports CFAST version from **7.7.0**
to version **7.7.5**.

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

Download and install CFAST from the `NIST CFAST downloads page <https://pages.nist.gov/cfast/downloads.html/>`_ or
the `CFAST GitHub repository <https://github.com/firemodels/cfast/releases>`_. Follow the installation
instructions for your operating system and ensure ``cfast`` is available in your PATH. On Windows go into
command prompt and type ``cfast`` to check if it is recognized as a command. You should see the CFAST version information.

.. image:: _static/images/cfast-cmd-win.png
   :alt: CFAST command prompt on Windows
   :align: center

If CFAST is installed in a non-standard location, you can manually specify the path
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
