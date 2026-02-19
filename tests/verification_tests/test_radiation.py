from __future__ import annotations

from pathlib import Path

from pycfast import (
    CeilingFloorVents,
    CFASTModel,
    Compartments,
    Devices,
    Fires,
    MaterialProperties,
    SimulationEnvironment,
)

from .verification import (
    compare_model_to_verification_data,
    get_verification_data_dir,
)

verification_data_dir = get_verification_data_dir(Path(__file__).parent, "Radiation")


def test_radiation_1_simulation(tmp_path):
    """Test construction of CFASTModel for the radiation_1.in file."""
    prefix = "radiation_1"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=10000,
        print=50,
        smokeview=10,
        spreadsheet=10,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
    )

    material_properties = [
        MaterialProperties(
            id="STEELSHT",
            material="Steel, Plain Carbon (1/16 in)",
            conductivity=48,
            density=7854,
            specific_heat=0.559,
            thickness=0.0015,
            emissivity=0.9,
        ),
    ]

    compartments = [
        Compartments(
            id="Comp 1",
            depth=99,
            height=99,
            width=99,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    ceiling_floor_vents = [
        CeilingFloorVents(
            id="CeilFloorVent_1",
            comps_ids=["OUTSIDE", "Comp 1"],
            area=20,
            type="CEILING",
            shape="SQUARE",
            offsets=[49.5, 49.5],
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1",
            comp_id="Comp 1",
            location=[9.5, 7.5, 0],
            type="PLATE",
            material_id="STEELSHT",
            surface_orientation="BACK WALL",
            temperature_depth=0.00075,
            depth_units="M",
        ),
    ]

    fires = [
        Fires(
            id="New Fire",
            comp_id="Comp 1",
            fire_id="New Fire_Fire",
            location=[7.5, 7.5],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0.35,
            data_table=[
                [0, 10, 0, 0.09, 0, 0, 0, 0, 0],
                [5000, 10, 0, 0.09, 0, 0, 0, 0, 0],
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
        wall_vents=[],
        ceiling_floor_vents=ceiling_floor_vents,
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


def test_radiation_2_simulation(tmp_path):
    """Test construction of CFASTModel for the radiation_2.in file."""
    prefix = "radiation_2"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=10000,
        print=50,
        smokeview=10,
        spreadsheet=10,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=True,
        extra_custom=("&DIAG T = 0, 10000 F = 500., 500. /"),
        # since this section is never used in typical CFAST scenarios it's
        # directly hard coded
    )

    material_properties = [
        MaterialProperties(
            id="STEELROD",
            material="Steel Rod, 2.5 cm diameter",
            conductivity=54,
            density=7833,
            specific_heat=0.465,
            thickness=0.025,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="STEELTHCK",
            material="Thick Steel (1 in)",
            conductivity=54,
            density=7833,
            specific_heat=0.465,
            thickness=0.025,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="STEELSHT",
            material="Thin Steel (1/16 in)",
            conductivity=54,
            density=7833,
            specific_heat=0.465,
            thickness=0.0015,
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

    devices = [
        Devices.create_target(
            id="Targ 1",
            comp_id="Comp 1",
            location=[2.5, 2.5, 0.01],
            type="CYLINDER",
            material_id="STEELROD",
            surface_orientation="FRONT WALL",
            temperature_depth=0.0125,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2",
            comp_id="Comp 1",
            location=[1.5, 2.5, 0.01],
            type="PLATE",
            material_id="STEELTHCK",
            surface_orientation="FRONT WALL",
            temperature_depth=0.0125,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 3",
            comp_id="Comp 1",
            location=[3.5, 2.5, 0.01],
            type="PLATE",
            material_id="STEELSHT",
            surface_orientation="BACK WALL",
            temperature_depth=0.00075,
            depth_units="M",
        ),
    ]

    fires = []

    file_name = tmp_path / f"{prefix}.in"
    cfast_exe = "cfast"
    extra_arguments = ["-f"]
    model = CFASTModel(
        simulation_environment=simulation_env,
        material_properties=material_properties,
        compartments=compartments,
        wall_vents=[],
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


def test_radiation_3_simulation(tmp_path):
    """Test construction of CFASTModel for the radiation_3.in file."""
    prefix = "radiation_3"

    simulation_env = SimulationEnvironment(
        title="radiation_3",
        time_simulation=1,
        print=1,
        smokeview=1,
        spreadsheet=1,
        init_pressure=101325,
        relative_humidity=100,
        interior_temperature=726.85,
        exterior_temperature=726.85,
        extra_custom=(
            "&DIAG GAS_TEMPERATURE = 726.85 "
            "PARTIAL_PRESSURE_H2O = 101325 "
            "PARTIAL_PRESSURE_CO2 = 0 /"
        ),
    )

    material_properties = [
        MaterialProperties(
            id="CONCRETE",
            material="CONCRETE",
            conductivity=1.75,
            density=2200,
            specific_heat=1,
            thickness=0.15,
            emissivity=1,
        ),
    ]

    compartments = [
        Compartments(
            id="Comp 1",
            depth=2,
            height=4,
            width=2,
            shaft=True,
            ceiling_mat_id="CONCRETE",
            ceiling_thickness=0.15,
            wall_mat_id="CONCRETE",
            wall_thickness=0.15,
            floor_mat_id="CONCRETE",
            floor_thickness=0.15,
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1top",
            comp_id="Comp 1",
            location=[0.0909, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2top",
            comp_id="Comp 1",
            location=[0.2727, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 3top",
            comp_id="Comp 1",
            location=[0.4545, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 4top",
            comp_id="Comp 1",
            location=[0.6363, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 5top",
            comp_id="Comp 1",
            location=[0.8181, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 6top",
            comp_id="Comp 1",
            location=[1, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 7top",
            comp_id="Comp 1",
            location=[1.1817, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 8top",
            comp_id="Comp 1",
            location=[1.3635, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 9top",
            comp_id="Comp 1",
            location=[1.5453, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 10top",
            comp_id="Comp 1",
            location=[1.7271, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 11top",
            comp_id="Comp 1",
            location=[1.9089, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 1side",
            comp_id="Comp 1",
            location=[2, 1, 0.125],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2side",
            comp_id="Comp 1",
            location=[2, 1, 0.375],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 3side",
            comp_id="Comp 1",
            location=[2, 1, 0.625],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 4side",
            comp_id="Comp 1",
            location=[2, 1, 0.875],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 5side",
            comp_id="Comp 1",
            location=[2, 1, 1.125],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 6side",
            comp_id="Comp 1",
            location=[2, 1, 1.375],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 7side",
            comp_id="Comp 1",
            location=[2, 1, 1.625],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 8side",
            comp_id="Comp 1",
            location=[2, 1, 1.875],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 9side",
            comp_id="Comp 1",
            location=[2, 1, 2.125],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 10side",
            comp_id="Comp 1",
            location=[2, 1, 2.375],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 11side",
            comp_id="Comp 1",
            location=[2, 1, 2.625],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 12side",
            comp_id="Comp 1",
            location=[2, 1, 2.875],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 13side",
            comp_id="Comp 1",
            location=[2, 1, 3.125],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 14side",
            comp_id="Comp 1",
            location=[2, 1, 3.375],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 15side",
            comp_id="Comp 1",
            location=[2, 1, 3.625],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 16side",
            comp_id="Comp 1",
            location=[2, 1, 3.875],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
    ]

    fires = []

    file_name = tmp_path / f"{prefix}.in"
    cfast_exe = "cfast"
    extra_arguments = ["-f"]
    model = CFASTModel(
        simulation_environment=simulation_env,
        material_properties=material_properties,
        compartments=compartments,
        wall_vents=[],
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


def test_radiation_4_simulation(tmp_path):
    """Test construction of CFASTModel for the radiation_4.in file."""
    prefix = "radiation_4"

    simulation_env = SimulationEnvironment(
        title="radiation_4",
        time_simulation=1,
        print=1,
        smokeview=1,
        spreadsheet=1,
        init_pressure=101325,
        relative_humidity=100,
        interior_temperature=226.85,
        exterior_temperature=726.85,
        extra_custom=(
            "&DIAG GAS_TEMPERATURE = 726.85 "
            "PARTIAL_PRESSURE_H2O = 101325 "
            "PARTIAL_PRESSURE_CO2 = 0 /"
        ),
    )

    material_properties = [
        MaterialProperties(
            id="CONCRETE",
            material="CONCRETE",
            conductivity=1.75,
            density=2200,
            specific_heat=1,
            thickness=0.15,
            emissivity=1,
        ),
    ]

    compartments = [
        Compartments(
            id="Comp 1",
            depth=2,
            height=4,
            width=2,
            shaft=True,
            ceiling_mat_id="CONCRETE",
            ceiling_thickness=0.15,
            wall_mat_id="CONCRETE",
            wall_thickness=0.15,
            floor_mat_id="CONCRETE",
            floor_thickness=0.15,
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1top",
            comp_id="Comp 1",
            location=[0.0909, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2top",
            comp_id="Comp 1",
            location=[0.2727, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 3top",
            comp_id="Comp 1",
            location=[0.4545, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 4top",
            comp_id="Comp 1",
            location=[0.6363, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 5top",
            comp_id="Comp 1",
            location=[0.8181, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 6top",
            comp_id="Comp 1",
            location=[1, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 7top",
            comp_id="Comp 1",
            location=[1.1817, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 8top",
            comp_id="Comp 1",
            location=[1.3635, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 9top",
            comp_id="Comp 1",
            location=[1.5453, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 10top",
            comp_id="Comp 1",
            location=[1.7271, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 11top",
            comp_id="Comp 1",
            location=[1.9089, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 1side",
            comp_id="Comp 1",
            location=[2, 1, 0.125],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2side",
            comp_id="Comp 1",
            location=[2, 1, 0.375],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 3side",
            comp_id="Comp 1",
            location=[2, 1, 0.625],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 4side",
            comp_id="Comp 1",
            location=[2, 1, 0.875],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 5side",
            comp_id="Comp 1",
            location=[2, 1, 1.125],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 6side",
            comp_id="Comp 1",
            location=[2, 1, 1.375],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 7side",
            comp_id="Comp 1",
            location=[2, 1, 1.625],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 8side",
            comp_id="Comp 1",
            location=[2, 1, 1.875],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 9side",
            comp_id="Comp 1",
            location=[2, 1, 2.125],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 10side",
            comp_id="Comp 1",
            location=[2, 1, 2.375],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 11side",
            comp_id="Comp 1",
            location=[2, 1, 2.625],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 12side",
            comp_id="Comp 1",
            location=[2, 1, 2.875],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 13side",
            comp_id="Comp 1",
            location=[2, 1, 3.125],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 14side",
            comp_id="Comp 1",
            location=[2, 1, 3.375],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 15side",
            comp_id="Comp 1",
            location=[2, 1, 3.625],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 16side",
            comp_id="Comp 1",
            location=[2, 1, 3.875],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
    ]

    fires = []

    file_name = tmp_path / f"{prefix}.in"
    cfast_exe = "cfast"
    extra_arguments = ["-f"]
    model = CFASTModel(
        simulation_environment=simulation_env,
        material_properties=material_properties,
        compartments=compartments,
        wall_vents=[],
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


def test_radiation_5_simulation(tmp_path):
    """Test construction of CFASTModel for the radiation_5.in file."""
    prefix = "radiation_5"

    simulation_env = SimulationEnvironment(
        title="radiation_4",
        # Note: the input file has title="radiation_4" but this is radiation_5
        time_simulation=1,
        print=1,
        smokeview=1,
        spreadsheet=1,
        init_pressure=101325,
        relative_humidity=100,
        interior_temperature=1226.85,
        exterior_temperature=726.85,
        extra_custom=(
            "&DIAG GAS_TEMPERATURE = 726.85 "
            "PARTIAL_PRESSURE_H2O = 101325 "
            "PARTIAL_PRESSURE_CO2 = 0 /"
        ),
    )

    material_properties = [
        MaterialProperties(
            id="CONCRETE",
            material="CONCRETE",
            conductivity=1.75,
            density=2200,
            specific_heat=1,
            thickness=0.15,
            emissivity=1,
        ),
    ]

    compartments = [
        Compartments(
            id="Comp 1",
            depth=2,
            height=4,
            width=2,
            shaft=True,
            ceiling_mat_id="CONCRETE",
            ceiling_thickness=0.15,
            wall_mat_id="CONCRETE",
            wall_thickness=0.15,
            floor_mat_id="CONCRETE",
            floor_thickness=0.15,
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1top",
            comp_id="Comp 1",
            location=[0.0909, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2top",
            comp_id="Comp 1",
            location=[0.2727, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 3top",
            comp_id="Comp 1",
            location=[0.4545, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 4top",
            comp_id="Comp 1",
            location=[0.6363, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 5top",
            comp_id="Comp 1",
            location=[0.8181, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 6top",
            comp_id="Comp 1",
            location=[1, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 7top",
            comp_id="Comp 1",
            location=[1.1817, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 8top",
            comp_id="Comp 1",
            location=[1.3635, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 9top",
            comp_id="Comp 1",
            location=[1.5453, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 10top",
            comp_id="Comp 1",
            location=[1.7271, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 11top",
            comp_id="Comp 1",
            location=[1.9089, 1, 4],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="FLOOR",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 1side",
            comp_id="Comp 1",
            location=[2, 1, 0.125],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2side",
            comp_id="Comp 1",
            location=[2, 1, 0.375],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 3side",
            comp_id="Comp 1",
            location=[2, 1, 0.625],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 4side",
            comp_id="Comp 1",
            location=[2, 1, 0.875],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 5side",
            comp_id="Comp 1",
            location=[2, 1, 1.125],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 6side",
            comp_id="Comp 1",
            location=[2, 1, 1.375],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 7side",
            comp_id="Comp 1",
            location=[2, 1, 1.625],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 8side",
            comp_id="Comp 1",
            location=[2, 1, 1.875],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 9side",
            comp_id="Comp 1",
            location=[2, 1, 2.125],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 10side",
            comp_id="Comp 1",
            location=[2, 1, 2.375],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 11side",
            comp_id="Comp 1",
            location=[2, 1, 2.625],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 12side",
            comp_id="Comp 1",
            location=[2, 1, 2.875],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 13side",
            comp_id="Comp 1",
            location=[2, 1, 3.125],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 14side",
            comp_id="Comp 1",
            location=[2, 1, 3.375],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 15side",
            comp_id="Comp 1",
            location=[2, 1, 3.625],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 16side",
            comp_id="Comp 1",
            location=[2, 1, 3.875],
            type="PLATE",
            material_id="CONCRETE",
            surface_orientation="BACK WALL",
            temperature_depth=0.075,
            depth_units="M",
        ),
    ]

    fires = []

    file_name = tmp_path / f"{prefix}.in"
    cfast_exe = "cfast"
    extra_arguments = ["-f"]
    model = CFASTModel(
        simulation_environment=simulation_env,
        material_properties=material_properties,
        compartments=compartments,
        wall_vents=[],
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
