Installation
============

PyCFAST requires **Python 3.10 or later** *and* a working installation of `CFAST <https://pages.nist.gov/cfast/>`_
itself. It is tested against CFAST **7.7.0** through **7.7.7**. Versions below **7.7.0** might work but are not
guaranteed to be fully compatible.

1. Install CFAST
----------------

CFAST is developed and distributed by NIST, independently of PyCFAST. Install it for your platform below,
then make sure ``cfast`` is available in your PATH.

.. tab-set::

   .. tab-item:: Windows
      :sync: windows

      Download and run the official installer from the
      `NIST CFAST downloads page <https://pages.nist.gov/cfast/downloads.html>`_ — older
      versions are available as ``.exe`` assets on the
      `CFAST releases page <https://github.com/firemodels/cfast/releases>`_.
      Open a command prompt and run ``cfast`` to verify that it is on your PATH.
      You should see the CFAST version information.

      .. image:: _static/images/cfast-cmd-win.png
         :alt: CFAST command prompt on Windows
         :align: center

   .. tab-item:: Linux
      :sync: linux

      NIST does not publish pre-built Linux binaries, so CFAST must be compiled from source with ``gfortran``.
      See the `Compiling CFAST wiki page <https://github.com/firemodels/cfast/wiki/Compiling-CFAST>`_ for full
      details:

      .. code-block:: bash

         # 1. Install a Fortran compiler
         sudo apt-get install gfortran        # Debian/Ubuntu
         # sudo dnf install gcc-gfortran      # Fedora/RHEL

         # 2. Clone the CFAST source, pinned to the release tag you want (e.g. CFAST-7.7.7)
         git clone --depth 1 --branch <CFAST_TAG> https://github.com/firemodels/cfast.git
         cd cfast/Build/CFAST/gnu_linux

         # 3. Build the executable
         chmod +x make_cfast.sh
         ./make_cfast.sh

         # 4. Install it on your PATH
         sudo cp cfast7_linux /usr/local/bin/cfast
         sudo chmod +x /usr/local/bin/cfast

      Note that CFAST 7.7.5 or later is required on Linux. If the build fails, the compiler and
      flags for each platform target are defined in ``Build/CFAST/makefile``. Adjust them there to
      match your machine.

   .. tab-item:: macOS
      :sync: macos

      NIST does not publish pre-built macOS binaries, so CFAST must be compiled from source with ``gfortran``.
      See the `Compiling CFAST wiki page <https://github.com/firemodels/cfast/wiki/Compiling-CFAST>`_ for full details:

      .. code-block:: bash

         # 1. Install a Fortran compiler
         brew install gcc

         # 2. Clone the CFAST source, pinned to the release tag you want (e.g. CFAST-7.7.7)
         git clone --depth 1 --branch <CFAST_TAG> https://github.com/firemodels/cfast.git
         cd cfast/Build/CFAST/gnu_osx

         # 3. Build the executable
         chmod +x make_cfast.sh
         ./make_cfast.sh

         # 4. Install it on your PATH
         sudo cp cfast7_osx /usr/local/bin/cfast
         sudo chmod +x /usr/local/bin/cfast

      Note that CFAST 7.7.6 or later is required on macOS. If the build fails, the compiler and
      flags for each platform target are defined in ``Build/CFAST/makefile``. Adjust them there to
      match your machine.

2. Set up a Python environment
------------------------------

It is recommended to install PyCFAST inside a virtual environment. Create one with ``venv`` or ``conda``:

.. tab-set::

   .. tab-item:: venv (Linux/macOS)
      :sync: venv-unix

      Python 3 is usually installed by default on Linux. On macOS install it with
      ``brew install python`` or from the
      `official website <https://www.python.org/downloads/macos/>`__. Then create a
      virtual environment from the terminal and activate it:

      .. code-block:: bash

         python -m venv .venv
         source .venv/bin/activate

   .. tab-item:: venv (Windows)
      :sync: venv-win

      Install the 64-bit version of Python 3 from the
      `official website <https://www.python.org/downloads/windows/>`__. Then create a
      virtual environment from the command prompt and activate it:

      .. code-block:: bat

         python -m venv .venv
         .venv\Scripts\activate

   .. tab-item:: conda
      :sync: conda

      `Miniforge <https://conda-forge.org/download/>`_ is the recommended way to install
      ``conda``. Then open the terminal and create a new environment and activate it:

      .. code-block:: bash

         conda create -n pycfast python=3.14
         conda activate pycfast

3. Install PyCFAST
------------------

With the environment activated, install PyCFAST from PyPI or conda-forge:

.. tab-set::

   .. tab-item:: pip
      :sync: pip

      PyCFAST is available on `PyPI <https://pypi.org/project/pycfast>`_:

      .. code-block:: bash

         pip install pycfast

   .. tab-item:: conda
      :sync: conda

      PyCFAST is available on the `conda-forge <https://anaconda.org/conda-forge/pycfast>`_ channel:

      .. code-block:: bash

         conda install -c conda-forge pycfast

   .. tab-item:: source
      :sync: source

      To install the latest development version, clone the repository and install it:

      .. code-block:: bash

         git clone https://github.com/bewygs/pycfast.git
         cd pycfast
         python -m pip install .

4. Configure the CFAST executable
----------------------------------

If CFAST is installed in a non-standard location, you can specify its path in three ways:

**1. Environment variable (shell)**

.. tab-set::

   .. tab-item:: Linux/macOS
      :sync: linux

      .. code-block:: bash

         export CFAST="/path/to/your/cfast/executable"

   .. tab-item:: Windows (cmd)
      :sync: windows-cmd

      .. code-block:: bat

         set CFAST="C:\path\to\your\cfast\executable"

   .. tab-item:: Windows (PowerShell)
      :sync: windows-ps

      .. code-block:: powershell

         $env:CFAST = "C:\path\to\your\cfast\executable"


**2. Environment variable (Python)**

.. code-block:: python

    import os

    os.environ['CFAST'] = "/path/to/your/cfast/executable"

**3. Directly when defining the** :class:`~pycfast.CFASTModel`

.. code-block:: python
    
    from pycfast import CFASTModel

    model = CFASTModel(
        ...,
        cfast_exe="/path/to/your/cfast/executable"
    )
