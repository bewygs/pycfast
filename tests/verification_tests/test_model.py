from __future__ import annotations

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


def test_run_returns_results(tmp_path):
    """Test that CFASTModel.run() returns results with expected structure."""
    simulation_env = SimulationEnvironment(
        title="Test Simulation",
        time_simulation=7200,
        print=40,
        smokeview=10,
        spreadsheet=40,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=False,
        lower_oxygen_limit=0.1,
        max_time_step=10,
    )
    material_properties = [
        MaterialProperties(
            id="Gypboard",
            material="Gypsum Board",
            conductivity=0.16,
            density=480,
            specific_heat=1,
            thickness=0.015875,
            emissivity=0.9,
        )
    ]
    compartments = [
        Compartments(
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
        ),
        Compartments(
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
        ),
    ]
    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["Comp 1", "OUTSIDE"],
            bottom=0.02,
            height=0.3,
            width=0.2,
            face="FRONT",
            offset=0.47,
        )
    ]
    ceiling_floor_vents = [
        CeilingFloorVents(
            id="CeilFloorVent_1",
            comps_ids=["Comp 2", "Comp 1"],
            area=0.01,
            type="FLOOR",
            shape="SQUARE",
            width=None,
            offsets=[0.84, 0.86],
        )
    ]
    mechanical_vents = [
        MechanicalVents(
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
    ]
    fires = [
        Fires(
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
                [0, 0, 0.05, 0.01, 0, 0.01, 0, 0, 0],
            ],
        )
    ]

    devices = [
        Devices.create_target(
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
    ]

    surface_connections = [
        SurfaceConnections.ceiling_floor_connection(
            comp_id="Comp 1",
            comp_ids="Comp 2",
        )
    ]

    file_name = tmp_path / "test.in"
    cfast_exe = "cfast"
    extra_arguments = ["-f"]

    model = CFASTModel(
        simulation_environment=simulation_env,
        material_properties=material_properties,
        compartments=compartments,
        wall_vents=wall_vents,
        ceiling_floor_vents=ceiling_floor_vents,
        mechanical_vents=mechanical_vents,
        fires=fires,
        devices=devices,
        surface_connections=surface_connections,
        file_name=str(file_name),
        cfast_exe=cfast_exe,
        extra_arguments=extra_arguments,
    )

    results = model.run()

    assert isinstance(results, dict)

    suffixes = [
        "compartments",
        "devices",
        "masses",
        "vents",
        "walls",
        "zone",
    ]

    for suffix in suffixes:
        assert any(f"{suffix}" in key for key in results.keys())
