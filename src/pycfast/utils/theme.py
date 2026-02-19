"""
Shared HTML theme utilities for PyCFAST Jupyter/interactive HTML representations.

Provides CSS theme styles and a card builder that supports both light and dark modes,
including JupyterLab/pydata-sphinx-theme detection via ``data-jp-theme-*`` and
``data-theme`` attributes.
"""

from __future__ import annotations


def get_theme_css() -> str:
    """
    Return the shared CSS theme block for PyCFAST HTML representations.

    The CSS handles light/dark mode transitions using:
    - ``prefers-color-scheme`` media query (system preference fallback)
    - ``data-jp-theme-light`` / ``data-jp-theme-dark`` attributes (JupyterLab)
    - ``data-theme="light"`` / ``data-theme="dark"`` attributes (pydata-sphinx-theme)

    Returns
    -------
    str
        CSS ``<style>`` block string.
    """
    return """
    <style>
        /* ── PyCFAST base (light) ── */
        .pycfast-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 12px;
            background-color: #fafafa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 500px;
            margin: 5px 0;
        }
        .pycfast-card--wide {
            max-width: 600px;
            padding: 15px;
        }
        .pycfast-card-title {
            margin: 0;
            color: #333;
        }
        .pycfast-card-subtitle {
            margin: 2px 0;
            color: #666;
            font-size: 0.85em;
        }
        .pycfast-card-body {
            background-color: white;
            padding: 10px;
            border-radius: 5px;
        }
        .pycfast-card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 8px;
            font-size: 0.85em;
        }
        .pycfast-detail {
            margin: 5px 0;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            background-color: white;
        }
        .pycfast-detail summary {
            padding: 8px 12px;
            cursor: pointer;
            background-color: #f8f9fa;
            border-radius: 4px 4px 0 0;
            user-select: none;
        }
        .pycfast-detail summary:hover {
            background-color: #e9ecef;
        }
        .pycfast-detail[open] summary {
            border-radius: 4px 4px 0 0;
        }
        .pycfast-detail ul {
            background-color: white;
            padding: 8px 12px;
            margin: 0;
        }
        .pycfast-detail li {
            margin: 3px 0;
            list-style-type: none;
            padding-left: 0;
        }
        .pycfast-inline-detail {
            margin-top: 10px;
        }
        .pycfast-inline-detail summary {
            cursor: pointer;
            font-weight: bold;
            color: #555;
        }
        .pycfast-inline-detail .pycfast-detail-content {
            margin-top: 5px;
            padding: 5px 0;
            font-size: 0.8em;
            color: #666;
        }

        /* ── Light mode overrides (JupyterLab / pydata) ── */
        html[data-jp-theme-light] .pycfast-card,
        body[data-jp-theme-light] .pycfast-card,
        html[data-theme="light"] .pycfast-card,
        body[data-theme="light"] .pycfast-card {
            border-color: #ddd !important;
            background-color: #fafafa !important;
        }
        html[data-jp-theme-light] .pycfast-card-title,
        body[data-jp-theme-light] .pycfast-card-title,
        html[data-theme="light"] .pycfast-card-title,
        body[data-theme="light"] .pycfast-card-title {
            color: #333 !important;
        }
        html[data-jp-theme-light] .pycfast-card-subtitle,
        body[data-jp-theme-light] .pycfast-card-subtitle,
        html[data-theme="light"] .pycfast-card-subtitle,
        body[data-theme="light"] .pycfast-card-subtitle {
            color: #666 !important;
        }
        html[data-jp-theme-light] .pycfast-card-body,
        body[data-jp-theme-light] .pycfast-card-body,
        html[data-theme="light"] .pycfast-card-body,
        body[data-theme="light"] .pycfast-card-body {
            background-color: white !important;
        }
        html[data-jp-theme-light] .pycfast-detail,
        body[data-jp-theme-light] .pycfast-detail,
        html[data-theme="light"] .pycfast-detail,
        body[data-theme="light"] .pycfast-detail {
            border-color: #e0e0e0 !important;
            background-color: white !important;
        }
        html[data-jp-theme-light] .pycfast-detail summary,
        body[data-jp-theme-light] .pycfast-detail summary,
        html[data-theme="light"] .pycfast-detail summary,
        body[data-theme="light"] .pycfast-detail summary {
            background-color: #f8f9fa !important;
            color: #333 !important;
        }
        html[data-jp-theme-light] .pycfast-detail summary:hover,
        body[data-jp-theme-light] .pycfast-detail summary:hover,
        html[data-theme="light"] .pycfast-detail summary:hover,
        body[data-theme="light"] .pycfast-detail summary:hover {
            background-color: #e9ecef !important;
        }
        html[data-jp-theme-light] .pycfast-detail ul,
        body[data-jp-theme-light] .pycfast-detail ul,
        html[data-theme="light"] .pycfast-detail ul,
        body[data-theme="light"] .pycfast-detail ul {
            background-color: white !important;
            color: inherit !important;
        }
        html[data-jp-theme-light] .pycfast-inline-detail summary,
        body[data-jp-theme-light] .pycfast-inline-detail summary,
        html[data-theme="light"] .pycfast-inline-detail summary,
        body[data-theme="light"] .pycfast-inline-detail summary {
            color: #555 !important;
        }
        html[data-jp-theme-light] .pycfast-inline-detail .pycfast-detail-content,
        body[data-jp-theme-light] .pycfast-inline-detail .pycfast-detail-content,
        html[data-theme="light"] .pycfast-inline-detail .pycfast-detail-content,
        body[data-theme="light"] .pycfast-inline-detail .pycfast-detail-content {
            color: #666 !important;
        }

        /* ── Dark mode – system preference ── */
        @media (prefers-color-scheme: dark) {
            .pycfast-card {
                border-color: #444;
                background-color: #2b2b2b;
            }
            .pycfast-card-title {
                color: #e0e0e0;
            }
            .pycfast-card-subtitle {
                color: #aaa;
            }
            .pycfast-card-body {
                background-color: #1e1e1e;
            }
            .pycfast-card-grid {
                color: #d0d0d0;
            }
            .pycfast-detail {
                border-color: #444;
                background-color: #1e1e1e;
            }
            .pycfast-detail summary {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            .pycfast-detail summary:hover {
                background-color: #333;
            }
            .pycfast-detail ul {
                background-color: #1e1e1e;
                color: #d0d0d0;
            }
            .pycfast-inline-detail summary {
                color: #bbb;
            }
            .pycfast-inline-detail .pycfast-detail-content {
                color: #aaa;
            }
        }

        /* ── Dark mode overrides (JupyterLab / pydata) ── */
        html[data-jp-theme-dark] .pycfast-card,
        body[data-jp-theme-dark] .pycfast-card,
        html[data-theme="dark"] .pycfast-card,
        body[data-theme="dark"] .pycfast-card {
            border-color: #444 !important;
            background-color: #2b2b2b !important;
        }
        html[data-jp-theme-dark] .pycfast-card-title,
        body[data-jp-theme-dark] .pycfast-card-title,
        html[data-theme="dark"] .pycfast-card-title,
        body[data-theme="dark"] .pycfast-card-title {
            color: #e0e0e0 !important;
        }
        html[data-jp-theme-dark] .pycfast-card-subtitle,
        body[data-jp-theme-dark] .pycfast-card-subtitle,
        html[data-theme="dark"] .pycfast-card-subtitle,
        body[data-theme="dark"] .pycfast-card-subtitle {
            color: #aaa !important;
        }
        html[data-jp-theme-dark] .pycfast-card-body,
        body[data-jp-theme-dark] .pycfast-card-body,
        html[data-theme="dark"] .pycfast-card-body,
        body[data-theme="dark"] .pycfast-card-body {
            background-color: #1e1e1e !important;
        }
        html[data-jp-theme-dark] .pycfast-card-grid,
        body[data-jp-theme-dark] .pycfast-card-grid,
        html[data-theme="dark"] .pycfast-card-grid,
        body[data-theme="dark"] .pycfast-card-grid {
            color: #d0d0d0 !important;
        }
        html[data-jp-theme-dark] .pycfast-detail,
        body[data-jp-theme-dark] .pycfast-detail,
        html[data-theme="dark"] .pycfast-detail,
        body[data-theme="dark"] .pycfast-detail {
            border-color: #444 !important;
            background-color: #1e1e1e !important;
        }
        html[data-jp-theme-dark] .pycfast-detail summary,
        body[data-jp-theme-dark] .pycfast-detail summary,
        html[data-theme="dark"] .pycfast-detail summary,
        body[data-theme="dark"] .pycfast-detail summary {
            background-color: #2b2b2b !important;
            color: #e0e0e0 !important;
        }
        html[data-jp-theme-dark] .pycfast-detail summary:hover,
        body[data-jp-theme-dark] .pycfast-detail summary:hover,
        html[data-theme="dark"] .pycfast-detail summary:hover,
        body[data-theme="dark"] .pycfast-detail summary:hover {
            background-color: #333 !important;
        }
        html[data-jp-theme-dark] .pycfast-detail ul,
        body[data-jp-theme-dark] .pycfast-detail ul,
        html[data-theme="dark"] .pycfast-detail ul,
        body[data-theme="dark"] .pycfast-detail ul {
            background-color: #1e1e1e !important;
            color: #d0d0d0 !important;
        }
        html[data-jp-theme-dark] .pycfast-inline-detail summary,
        body[data-jp-theme-dark] .pycfast-inline-detail summary,
        html[data-theme="dark"] .pycfast-inline-detail summary,
        body[data-theme="dark"] .pycfast-inline-detail summary {
            color: #bbb !important;
        }
        html[data-jp-theme-dark] .pycfast-inline-detail .pycfast-detail-content,
        body[data-jp-theme-dark] .pycfast-inline-detail .pycfast-detail-content,
        html[data-theme="dark"] .pycfast-inline-detail .pycfast-detail-content,
        body[data-theme="dark"] .pycfast-inline-detail .pycfast-detail-content {
            color: #aaa !important;
        }
    </style>
    """


def build_card(
    icon: str,
    gradient: str,
    title: str,
    subtitle: str,
    accent_color: str,
    body_html: str,
    *,
    wide: bool = False,
) -> str:
    """
    Build a themed HTML card for Jupyter ``_repr_html_`` output.

    Parameters
    ----------
    icon : str
        Emoji icon displayed in the header badge.
    gradient : str
        CSS ``linear-gradient(...)`` value for the badge background.
    title : str
        Card header title text (rendered as ``<h4>``).
    subtitle : str
        Card header subtitle text (rendered as ``<p>``).
    accent_color : str
        CSS color for the left-border accent bar.
    body_html : str
        Inner HTML for the card body (grid items, details sections, etc.).
    wide : bool, optional
        If True, uses a wider card layout (600 px). Default is False (500 px).

    Returns
    -------
    str
        Complete themed HTML string including the shared ``<style>`` block.
    """
    wide_class = " pycfast-card--wide" if wide else ""

    return f"""
    <div class="pycfast-card{wide_class}">
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <div style="width: 35px; height: 35px; background: {gradient};
                       border-radius: 50%; display: flex; align-items: center;
                       justify-content: center; margin-right: 10px;">
                <span style="color: white; font-weight: bold; font-size: 16px;">{icon}</span>
            </div>
            <div>
                <h4 class="pycfast-card-title">{title}</h4>
                <p class="pycfast-card-subtitle">{subtitle}</p>
            </div>
        </div>

        <div class="pycfast-card-body" style="border-left: 4px solid {accent_color};">
            {body_html}
        </div>
    </div>
    {get_theme_css()}
    """
