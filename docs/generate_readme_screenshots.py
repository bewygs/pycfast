"""Generate HTML repr screenshots for the README.

This script creates the PyCFAST model objects from the basic usage example,
renders their HTML repr cards, and saves screenshots as PNG images.

Usage:
    python docs/generate_readme_screenshots.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure pycfast is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from pycfast import (
    CeilingFloorVents,
    CFASTModel,
    Compartments,
    Devices,
    Fires,
    MaterialProperties,
    MechanicalVents,
    SimulationEnvironment,
    SurfaceConnections,
    WallVents,
)


def build_objects():
    """Build all the example objects and the full model."""
    simulation_env = SimulationEnvironment(
        title="Simple example",
        time_simulation=7200,
        print=40,
        smokeview=10,
        spreadsheet=10,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=False,
        lower_oxygen_limit=0.1,
        max_time_step=10,
    )

    gypsum_board = MaterialProperties(
        id="Gypboard",
        material="Gypsum Board",
        conductivity=0.16,
        density=480,
        specific_heat=1,
        thickness=0.015,
        emissivity=0.9,
    )

    ground_level = Compartments(
        id="Comp 1",
        depth=10.0,
        height=10.0,
        width=10.0,
        ceiling_mat_id="Gypboard",
        ceiling_thickness=0.01,
        wall_mat_id="Gypboard",
        wall_thickness=0.01,
        floor_mat_id="Gypboard",
        floor_thickness=0.01,
        origin_x=0,
        origin_y=0,
        origin_z=0,
    )

    upper_level = Compartments(
        id="Comp 2",
        depth=10.0,
        height=10.0,
        width=10.0,
        ceiling_mat_id="Gypboard",
        ceiling_thickness=0.01,
        wall_mat_id="Gypboard",
        wall_thickness=0.01,
        floor_mat_id="Gypboard",
        floor_thickness=0.01,
        origin_x=0,
        origin_y=0,
        origin_z=10,
    )

    wall_vent = WallVents(
        id="WallVent_1",
        comps_ids=["Comp 1", "OUTSIDE"],
        bottom=0.02,
        height=0.3,
        width=0.2,
        face="FRONT",
        offset=0.47,
    )

    ceiling_floor_vents = CeilingFloorVents(
        id="CeilFloorVent_1",
        comps_ids=["Comp 2", "Comp 1"],
        area=0.01,
        shape="SQUARE",
        width=None,
        offsets=[0.84, 0.86],
    )

    mechanical_vents = MechanicalVents(
        id="mech",
        comps_ids=["OUTSIDE", "Comp 1"],
        area=[1.2, 10],
        heights=[1, 1],
        orientations=["HORIZONTAL", "HORIZONTAL"],
        flow=1,
        cutoffs=[250, 300],
        offsets=[0, 0.6],
        filter_time=1.2,
        filter_efficiency=5,
    )

    propane_fire = Fires(
        id="Propane",
        comp_id="Comp 1",
        fire_id="Propane_Fire",
        location=[0.3, 0.3],
        carbon=5,
        chlorine=2,
        hydrogen=8,
        nitrogen=1,
        oxygen=0,
        heat_of_combustion=100,
        radiative_fraction=0.3,
        data_table=[
            [0, 0, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [30, 10, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [60, 40, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [90, 90, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [120, 160, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [150, 250, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [180, 360, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [210, 490, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [240, 640, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [270, 810, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [300, 999.9999, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [600, 1000, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [601, 810, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [602, 640, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [603, 490, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [604, 360, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [605, 250, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [606, 160, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [607, 90, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [608, 40, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [609, 10, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [610, 0, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
            [620, 0, 0, 0.3, 0.008021683, 0.02, 0, 0, 0],
        ],
    )

    target = Devices.create_target(
        id="Target_1",
        comp_id="Comp 1",
        location=[0.5, 0.5, 0],
        type="CYLINDER",
        material_id="Gypboard",
        surface_orientation="HORIZONTAL",
        thickness=0.01,
        temperature_depth=0.01,
        depth_units="M",
    )

    ceiling_floor_connection = SurfaceConnections.ceiling_floor_connection(
        comp_id="Comp 1",
        comp_ids="Comp 2",
    )

    model = CFASTModel(
        simulation_environment=simulation_env,
        material_properties=[gypsum_board],
        compartments=[ground_level, upper_level],
        wall_vents=[wall_vent],
        ceiling_floor_vents=[ceiling_floor_vents],
        mechanical_vents=[mechanical_vents],
        fires=[propane_fire],
        devices=[target],
        surface_connections=[ceiling_floor_connection],
        file_name="example_simulation.in",
        cfast_exe="cfast",
        extra_arguments=["-f"],
    )

    return {
        "model": model,
        "simulation_env": simulation_env,
        "compartment": ground_level,
        "fire": propane_fire,
        "wall_vent": wall_vent,
        "device": target,
        "material": gypsum_board,
    }


def wrap_html(card_html: str, bg_color: str = "#ffffff") -> str:
    """Wrap an HTML card in a full HTML document for screenshot rendering."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background-color: {bg_color};
            display: inline-block;
        }}
    </style>
</head>
<body>
{card_html}
</body>
</html>"""


def wrap_multi_cards_html(cards_html: list[str], bg_color: str = "#ffffff") -> str:
    """Wrap multiple HTML cards in a full HTML document with grid layout."""
    cards_joined = "\n".join(cards_html)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background-color: {bg_color};
            display: inline-block;
        }}
        .cards-row {{
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            align-items: flex-start;
        }}
    </style>
</head>
<body>
<div class="cards-row">
{cards_joined}
</div>
</body>
</html>"""


def generate_screenshots():
    """Generate all screenshots for the README."""
    from playwright.sync_api import sync_playwright

    output_dir = Path(__file__).resolve().parent / "source" / "_static" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    objects = build_objects()

    # Define screenshots to generate
    screenshots = {
        # Model card (light) - with details expanded
        "pycfast-model-card-light": {
            "html": wrap_html(objects["model"]._repr_html_(), bg_color="#ffffff"),
            "expand_details": True,
        },
        # Model card (dark) - with details expanded
        "pycfast-model-card-dark": {
            "html": wrap_html(objects["model"]._repr_html_(), bg_color="#1a1a2e"),
            "expand_details": True,
        },
        # Multi-card showcase (light)
        "pycfast-cards-showcase-light": {
            "html": wrap_multi_cards_html(
                [
                    objects["compartment"]._repr_html_(),
                    objects["fire"]._repr_html_(),
                    objects["wall_vent"]._repr_html_(),
                ],
                bg_color="#ffffff",
            ),
            "expand_details": False,
        },
        # Multi-card showcase (dark)
        "pycfast-cards-showcase-dark": {
            "html": wrap_multi_cards_html(
                [
                    objects["compartment"]._repr_html_(),
                    objects["fire"]._repr_html_(),
                    objects["wall_vent"]._repr_html_(),
                ],
                bg_color="#1a1a2e",
            ),
            "expand_details": False,
        },
        # All cards grid (light) - simulation, material, compartment, fire, vents, device
        "pycfast-all-cards-light": {
            "html": wrap_multi_cards_html(
                [
                    objects["simulation_env"]._repr_html_(),
                    objects["material"]._repr_html_(),
                    objects["compartment"]._repr_html_(),
                    objects["fire"]._repr_html_(),
                    objects["wall_vent"]._repr_html_(),
                    objects["device"]._repr_html_(),
                ],
                bg_color="#ffffff",
            ),
            "expand_details": False,
        },
        # All cards grid (dark)
        "pycfast-all-cards-dark": {
            "html": wrap_multi_cards_html(
                [
                    objects["simulation_env"]._repr_html_(),
                    objects["material"]._repr_html_(),
                    objects["compartment"]._repr_html_(),
                    objects["fire"]._repr_html_(),
                    objects["wall_vent"]._repr_html_(),
                    objects["device"]._repr_html_(),
                ],
                bg_color="#1a1a2e",
            ),
            "expand_details": False,
        },
    }

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for name, config in screenshots.items():
            page = browser.new_page(device_scale_factor=2)  # 2x for retina quality

            html_content = config["html"]

            # Set content with dark theme attribute if needed
            if "dark" in name:
                html_content = html_content.replace(
                    "<html lang=\"en\">",
                    '<html lang="en" data-theme="dark">',
                )

            page.set_content(html_content)
            page.wait_for_timeout(500)  # Let CSS render

            # Expand all <details> elements if requested
            if config.get("expand_details"):
                page.evaluate("() => document.querySelectorAll('details').forEach(d => d.open = true)")
                page.wait_for_timeout(200)

            # Auto-size to content
            body = page.query_selector("body")
            bbox = body.bounding_box()

            output_path = output_dir / f"{name}.png"
            page.screenshot(
                path=str(output_path),
                clip={
                    "x": 0,
                    "y": 0,
                    "width": bbox["width"],
                    "height": bbox["height"],
                },
            )
            print(f"  ✓ Generated: {output_path.name} ({bbox['width']:.0f}×{bbox['height']:.0f}px)")
            page.close()

        browser.close()

    print(f"\nAll screenshots saved to: {output_dir}")


if __name__ == "__main__":
    generate_screenshots()
