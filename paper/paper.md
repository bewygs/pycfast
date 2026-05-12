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
header-includes:
  - \usepackage{booktabs}
  - \usepackage{listings}
  - \usepackage{xcolor}
  - \lstset{language=Python, basicstyle=\small\ttfamily, keywordstyle=\color{blue!70}\bfseries, stringstyle=\color{red!60}, commentstyle=\color{green!50!black}\itshape, showstringspaces=false}
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
Simulator (FDS).

The same survey highlights two recurring gaps and needs expressed by practitioners.
First, respondents reported an inefficient use of fire models due to time-consuming
pre- and post-processing of inputs and outputs, and expressed a need for easier-to-use
software with improved presentation of results. Several respondents explicitly called
for a transition from spreadsheet-based workflows to Python-based environments with
richer output capabilities. Second, when asked about desired improvements to CFAST
itself, respondents specifically requested better support for the
*automation of risk assessment with multiple distributed input values*.

`PyCFAST` directly addresses these needs by exposing the CFAST fire model
as a Python interface. Users can construct simulation scenarios programmatically,
execute CFAST in batch, and analyze results within the broader Python scientific
ecosystem [@Harris2020; @reback2020pandas]. This removes the friction of using the
graphical interface, or making custom scripts that reimplement input file generation.

\begin{figure}[h!]
\centering
\begin{minipage}[c]{0.45\textwidth}
  \centering
  \includegraphics[width=\textwidth]{images/cedit-compartments-tab.png}
\end{minipage}%
\hspace{1em}
\begin{minipage}[c]{0.50\textwidth}
  \begin{lstlisting}[language=Python]
from pycfast import Compartment

room = Compartment(
    id="Comp 1",
    width=10.0,
    depth=10.0,
    height=10.0,
    ceiling_mat_id="Gypboard",
    wall_mat_id="Gypboard",
    floor_mat_id="Gypboard",
)
  \end{lstlisting}
\end{minipage}
\caption{The CFAST graphical interface (CEdit) alongside its
  \texttt{PyCFAST} equivalent for defining a compartment.}
\label{fig:cedit-vs-pycfast}
\end{figure}

Moreover, because CFAST is computationally inexpensive compared to CFD-based fire
models such as FDS [@FDS_technical], it is particularly well suited to generate data
for large parametric studies, sensitivity analyses, and machine learning applications
in fire safety engineering.

Nevertheless, users should ensure that the scenarios stay within CFAST validated
domain [@CFAST_validation; @NUREG1824_v5], as synthetic data produced outside the model
validation range may not represent real fire behavior.

# State of the field

The use of CFAST for large-scale data generation in research has grown considerably
over the past years, driven by two main application areas: probabilistic fire risk
assessment in the nuclear industry and machine-learning–based modeling of fire
phenomena (flashover prediction). The studies summarized in \autoref{tab:stateoffield}
frequently require thousands to hundreds of thousands of CFAST simulations.

To respond to this demand, two general-purpose tools currently support CFAST
automation. **CData** [@CData], the official Monte Carlo simulation utility distributed
with CFAST. It is widely adopted in the research community notably across the
*P-Flash* / *FlashNet* family of studies [@Fu2021AAAI; @WANG2021103341; @TAM2022105258;
@TAM2023119899; @FAN2023103849]. But CData is limited for input generation and CFAST
execution, not for integration into complex Python workflows such as sensitivity
analyses or optimization studies.

Another tool called **RAVEN** [@osti_1784874] is commonly used in the nuclear safety
community [@WORRELL2019128; @osti_1632319; @FARAJPOUR2026114956], it is a
domain-agnostic uncertainty quantification and machine learning framework developed at
Idaho National Laboratory. It natively supports surrogate modeling, sensitivity
analysis, and optimization but coupling RAVEN to CFAST requires writing a custom
`CodeInterface` in Python class that hardcodes the construction of the CFAST input file
by string concatenation. When neither tool fits, researchers used Python scripts that
reimplement input-file generation from scratch [@Buffington2020].

Below is a summary of the literature that used CFAST to generate large-scale data, categorized by task, number of simulations, and coupling tool used.

| Date | Authors | Task | Simulations | Coupling tool |
|--------|----------------|------------------------|:------:|:--------------:|
| 2019 | Worrell et al. [-@WORRELL2019128] | Regression | 675k | RAVEN |
| 2020 | Biersdorf et al. [-@osti_1632319] | Sensitivity analysis | Morris EE + MC | RAVEN |
| 2020 | Buffington et al. [-@Buffington2020] | Regression | 20k | Custom Python |
| 2021 | Fang et al. [-@FANG2021103469] | Classification | 6k | — |
| 2021–2022 | Kou et al. [-@KOU2021103310; -@KOU2022105310] | Classification + Regression | 970–2.5k | — |
| 2021–2023 | Tam, Fu et al. [-@Fu2021AAAI; -@WANG2021103341; -@TAM2022105258; -@Tam2023_synthetic; -@TAM2023119899; -@FAN2023103849] | Classification + Regression | 5k–110k | CData |
| 2024 | Yang et al. [-@fire7020053] | Classification | 4.8k | CData |
| 2024 | Singh, Jang et al. [-@SINGH20243717; -@JANG20241256] | Regression + Sensitivity analysis | 11k–12k | — |
| 2024 | Sakurahara et al. [-@Sakurahara2024_probabilistic] | Sensitivity analysis + Uncertainty Quantification | ~25k | RAVEN |
| 2025 | Alkhatib, Sakurahara et al. [-@ALKHATIB2025111237] | Sensitivity analysis + Regression | 230k | — |
| 2026 | Zhang, Heo et al. [-@ZHANG2026104006; -@HEO2026103862] | Regression | 6k | — |
| 2026 | Chen, Sakurahara [-@CHEN2026111869] | Regression | 20k | — |
| 2026 | Farajpour et al. [-@FARAJPOUR2026114956] | Uncertainty Quantification | 10k | RAVEN |
| 2026 | Batikh et al. [-@BATIKH2026112333] | Generative modeling | 11k | — |

: Selected studies using CFAST for large-scale data generation. \label{tab:stateoffield}

Note that a more detailed literature review is available at https://github.com/bewygs/pycfast/tree/main/paper/literature_review.md.

This reflects a broader trend in the scientific community where Python has become the
dominant language for data processing, machine learning, and scientific analysis.
Frameworks such as PyTorch, TensorFlow, SALib, and pandas are commonly used across the
reviewed studies for surrogate modeling, sensitivity analysis, and post-processing
CFAST results. By providing a Python interface to CFAST, `PyCFAST` allows researchers
and engineers to integrate CFAST simulations directly into their workflows, without the
need to create custom code or external tools for input generation and execution.


# Software design

# Research impact statement

As mentioned in \autoref{tab:stateoffield}, the fire research community around CFAST
has demonstrated the need for CFAST automation, yet no dedicated Python interface
existed prior to `PyCFAST`. Moreover, `PyCFAST` comes with a verification suite that
reproduces NIST reference results [@CFAST_validation], to validate the reliability of
the library. It also includes reproducible examples covering the most common workflows
in the literature: data generation, sensitivity analysis, surrogate modeling, and
parallel execution, available at https://pycfast.org/examples.

# AI usage disclosure

AI tools (Claude Code and GitHub Copilot) were used for writing documentation draft and
was reviewed and edited by the author, as AI-generated text tended to be overly
verbose. Unit tests and verification tests were developed with AI support to reduce
repetitive manual effort. Finally, AI was used to identify relevant article
that may have been missed after an initial bibliography that was compiled manually by
the author. All references were carefully read and selected by the author before
inclusion.

# Acknowledgements

`PyCFAST` was developed with the support of Orano, France. The author acknowledges the
CFAST development team at the National Institute of Standards and Technology (NIST) for
their ongoing efforts in maintaining and improving the CFAST fire modeling software.

# References
