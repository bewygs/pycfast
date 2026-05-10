---
title: 'PyCFAST: a Python interface for the CFAST fire simulation software'
tags:
  - Python
  - fire simulation
  - fire safety engineering
  - CFAST
  - parametric study
authors:
  - name: Benoît Wygas
    orcid: 0009-0009-0570-4641
    corresponding: true
    affiliation: 1
affiliations:
  - name: Orano, France
    index: 1
date: XX MM 2026
bibliography: paper.bib
---

# Summary

The Consolidated Fire and Smoke Transport (CFAST) [@CFAST_technical] is a two-zone fire
model capable of predicting the environment in a multi-compartment structure subjected
to a fire. It calculates the time evolving distribution of smoke and fire gases and the
temperature throughout a building during a user-prescribed fire. CFAST is developed by
the National Institute of Standards and Technology (NIST) and is one of the most widely
used fire models in the fire safety engineering community. CFAST is a long-established
fire modeling software written in Fortran and traditionally run through its graphical
interface (CEdit) [@CFAST_users]. This reliance on a GUI can make large parametric
studies, automation, and reproducibility cumbersome.

`PyCFAST` is a Python interface to CFAST, providing an easy-to-use Python programming
interface for building and running fire scenarios without relying on its graphical
interface. It allows researchers and engineers to automate CFAST runs, build and modify
input files programmatically, execute simulations, and analyze results using the broader
Python ecosystem.

# Statement of need

A 2021 survey of fire engineering practitioners conducted by the SFPE Foundation
[@wade2021fire] identified CFAST as one of the most widely used fire modeling tools in
the field, ranking among the top ten software programs reported by respondents. Among
the tools dedicated specifically to fire, CFAST ranks second behind Fire Dynamics
Simulator (FDS) [@FDS_technical].

The same survey highlights two recurring gaps and needs expressed by practitioners.
First, respondents reported an inefficient use of fire models due to time-consuming
pre- and post-processing of inputs and outputs, and expressed a need for easier-to-use
software with improved presentation of results. Several respondents explicitly called
for a transition from spreadsheet-based workflows to Python-based environments with richer output capabilities. Second, when asked about desired improvements to CFAST itself, respondents specifically requested better support for the
*automation of risk assessment with multiple distributed input values*.

`PyCFAST` directly addresses these needs by exposing the CFAST fire model
as a Python interface. Users can construct simulation scenarios programmatically,
execute CFAST in batch, and analyze results within the broader Python scientific
ecosystem [@Harris2020; @reback2020pandas]. This removes the friction of using the
graphical interface, or making custom scripts that reimplement input file generation.

Because CFAST is computationally inexpensive compared to CFD-based fire models such as
FDS, it is particularly well suited to large parametric studies, sensitivity analyses,and machine learning applications in fire safety engineering.

Nevertheless, users should ensure that the scenarios stay within CFAST
validated domain [@CFAST_technical], as synthetic data produced outside the model
validation range may not represent real fire behavior.

# State of the field

# Software design

# Research impact statement

# AI usage disclosure

# Acknowledgements

# References
