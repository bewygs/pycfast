from __future__ import annotations

from pathlib import Path

from pycfast import (
    CFASTModel,
    Compartments,
    Devices,
    Fires,
    MaterialProperties,
    SimulationEnvironment,
    WallVents,
)

from .verification import (
    compare_model_to_verification_data,
    get_verification_data_dir,
)

verification_data_dir = get_verification_data_dir(Path(__file__).parent, "Fires")


def test_ignition_test_simulation(tmp_path):
    """Test construction of CFASTModel for the Ignition_Test.in file."""
    prefix = "Ignition_Test"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=700,
        print=1,
        smokeview=10,
        spreadsheet=1,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
    )

    material_properties = [
        MaterialProperties(
            id="HARDWOOD",
            material="Wood, Hardwoods (oak, maple) (3/4 in)",
            conductivity=0.16,
            density=720,
            specific_heat=1.255,
            thickness=0.019,
            emissivity=0.9,
        ),
    ]

    compartments = [
        Compartments(
            id="Comp 1",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["Comp 1", "OUTSIDE"],
            bottom=0,
            height=2,
            width=1,
            face="FRONT",
            offset=2,
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ F2",
            comp_id="Comp 1",
            location=[2.5, 3.5, 1],
            type="PLATE",
            material_id="HARDWOOD",
            surface_orientation="LEFT WALL",
            temperature_depth=0.0095,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ F3",
            comp_id="Comp 1",
            location=[2.5, 4.5, 1],
            type="PLATE",
            material_id="HARDWOOD",
            surface_orientation="LEFT WALL",
            temperature_depth=0.0095,
            depth_units="M",
        ),
    ]

    fires = [
        Fires(
            id="Initial Fire",
            comp_id="Comp 1",
            fire_id="Initial Fire_Fire",
            location=[2.5, 2.5],
            carbon=6,
            chlorine=0,
            hydrogen=10,
            nitrogen=0,
            oxygen=5,
            heat_of_combustion=14000,
            radiative_fraction=0.35,
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
        ),
        Fires(
            id="Second Fire",
            comp_id="Comp 1",
            fire_id="Second Fire_Fire",
            location=[2.5, 3.5],
            ignition_criterion="FLUX",
            device_id="Targ F2",
            set_point=6,
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0.35,
            data_table=[
                [0, 0, 0, 0.09, 0.004747221, 0.01, 0, 0, 0],
                [100, 2, 0, 0.09, 0.004747221, 0.01, 0, 0, 0],
            ],
        ),
        Fires(
            id="Third Fire",
            comp_id="Comp 1",
            fire_id="Third Fire_Fire",
            location=[2.5, 3.5],
            ignition_criterion="TEMPERATURE",
            device_id="Targ F3",
            set_point=200,
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0.35,
            data_table=[
                [0, 0, 0, 0.09, 0.004747221, 0.01, 0, 0, 0],
                [100, 2, 0, 0.09, 0.004747221, 0.01, 0, 0, 0],
            ],
        ),
    ]

    file_name = tmp_path / f"{prefix}.in"
    cfast_exe = "cfast"
    extra_arguments = ["-f"]
    model = CFASTModel(
        simulation_environment=simulation_env,
        material_properties=material_properties,
        compartments=compartments,
        wall_vents=wall_vents,
        ceiling_floor_vents=[],
        mechanical_vents=[],
        fires=fires,
        devices=devices,
        cfast_exe=cfast_exe,
        extra_arguments=extra_arguments,
        file_name=str(file_name),
    )

    results = model.run()
    assert isinstance(results, dict)

    compare_model_to_verification_data(
        results, verification_data_dir, prefix=prefix, tmp_path=tmp_path
    )
