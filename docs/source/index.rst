.. PyCFAST documentation master file, created by
   sphinx-quickstart on Sat Aug  2 15:23:05 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the PyCFAST documentation
====================================

**PyCFAST** is a Python interface for the |CFAST Page|_ fire simulation software,
providing an easy-to-use Python programming interface for building and running fire
scenarios. It allows researchers and engineers to automate, customize, create CFAST
input files, execute simulations, and analyze results using the versatility and
extensive ecosystem of Python.

.. |CFAST Page| replace:: **Consolidated Fire and Smoke Transport (CFAST)**
.. _CFAST Page: https://pages.nist.gov/cfast/


Motivation
==========

CFAST is a long-established fire modeling software written in Fortran and traditionally
run through its graphical interface (CEdit). This reliance on a GUI can make large
parametric studies, automation, and reproducibility cumbersome.

With the release of |CData-release|_, a new tool called CData was introduced to
support Monte Carlo simulations. While useful for some workflows, CData has certain
limitations: several parameters (e.g., `radiative fraction`, `fire chemistry`) are not
properly handled, it is not highly customizable, and it can be prone to bugs.
To address these limitations, this library was initially developed internally at
`Orano <https://www.orano.group/>`_ to connect CFAST with the Python scientific ecosystem
(notably for the |scipy.optimize|_ module). Over time, it evolved into a general-purpose
programming interface and now, can be used as an alternative to CData for automation,
reproducibility, and advanced analyses.

.. |scipy.optimize| replace:: ``scipy.optimize``
.. _scipy.optimize: https://docs.scipy.org/doc/scipy/reference/optimize.html


.. |CData-release| replace:: **version 7.7.0 of CFAST**
.. _CData-release: https://www.nist.gov/publications/cfast-consolidated-fire-and-smoke-transport-version-7-volume-5-cfast-fire-data

.. toctree::
   :maxdepth: 1
   :caption: User Guide

   Installation <installation>
   Getting Started <getting_started>
   Examples <examples>

.. toctree::
   :maxdepth: 2
   :caption: Reference

   API <api/index>

.. toctree::
   :maxdepth: 1
   :caption: Development

   Contributing Guide <contributing>
   Changelog <changelog>

.. toctree::
   :maxdepth: 1
   :caption: Other

   Acknowledgments <acknowledgments>
   Licence <licence>
   Citation <citation>