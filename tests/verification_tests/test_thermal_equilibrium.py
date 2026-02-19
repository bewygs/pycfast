from __future__ import annotations

from pathlib import Path

from pycfast import (
    CFASTModel,
    Compartments,
    MaterialProperties,
    SimulationEnvironment,
    WallVents,
)

from .verification import (
    compare_model_to_verification_data,
    get_verification_data_dir,
)

verification_data_dir = get_verification_data_dir(
    Path(__file__).parent, "Thermal_Equilibrium"
)


def test_basic_tempequilib_simulation(tmp_path):
    """Test construction of CFASTModel for the basic_tempequilib.in file."""
    prefix = "basic_tempequilib"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=80000,
        print=10000,
        smokeview=1000,
        spreadsheet=1000,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=25,
    )

    material_properties = [
        MaterialProperties(
            id="GYPSUM",
            material="Gypsum Board (5/8 in)",
            conductivity=0.16,
            density=790,
            specific_heat=0.9,
            thickness=0.016,
            emissivity=0.9,
        ),
    ]

    compartments = [
        Compartments(
            id="Compartment 1",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="GYPSUM",
            ceiling_thickness=0.016,
            wall_mat_id="GYPSUM",
            wall_thickness=0.016,
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
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
        ceiling_floor_vents=[],
        mechanical_vents=[],
        fires=[],
        devices=[],
        cfast_exe=cfast_exe,
        extra_arguments=extra_arguments,
        file_name=str(file_name),
    )

    results = model.run()
    assert isinstance(results, dict)

    compare_model_to_verification_data(
        results, verification_data_dir, prefix=prefix, tmp_path=tmp_path
    )


def test_basic_tempequilib_window_simulation(tmp_path):
    """Test construction of CFASTModel for the basic_tempequilib_window.in file."""
    prefix = "basic_tempequilib_window"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=18000,
        print=50,
        smokeview=10,
        spreadsheet=10,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=25,
    )

    material_properties = [
        MaterialProperties(
            id="GYPSUM",
            material="Gypsum Board (5/8 in)",
            conductivity=0.16,
            density=790,
            specific_heat=0.9,
            thickness=0.016,
            emissivity=0.9,
        ),
    ]

    compartments = [
        Compartments(
            id="Compartment 1",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="GYPSUM",
            ceiling_thickness=0.016,
            wall_mat_id="GYPSUM",
            wall_thickness=0.016,
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["Compartment 1", "OUTSIDE"],
            bottom=1.5,
            height=2,
            width=1,
            face="FRONT",
            offset=2,
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
        fires=[],
        devices=[],
        cfast_exe=cfast_exe,
        extra_arguments=extra_arguments,
        file_name=str(file_name),
    )

    results = model.run()
    assert isinstance(results, dict)

    compare_model_to_verification_data(
        results, verification_data_dir, prefix=prefix, tmp_path=tmp_path
    )


def test_basic_tempequilib_window_elevation_simulation(tmp_path):
    """Test construction of CFASTModel for the basic_tempequilib_window_elevation.in file."""
    prefix = "basic_tempequilib_window_elevation"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=18000,
        print=50,
        smokeview=10,
        spreadsheet=10,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=25,
    )

    material_properties = [
        MaterialProperties(
            id="GYPSUM",
            material="Gypsum Board (5/8 in)",
            conductivity=0.16,
            density=790,
            specific_heat=0.9,
            thickness=0.016,
            emissivity=0.9,
        ),
    ]

    compartments = [
        Compartments(
            id="Compartment 1",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="GYPSUM",
            ceiling_thickness=0.016,
            wall_mat_id="GYPSUM",
            wall_thickness=0.016,
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["Compartment 1", "OUTSIDE"],
            bottom=2,
            height=1,
            width=1,
            face="FRONT",
            offset=2,
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
        fires=[],
        devices=[],
        cfast_exe=cfast_exe,
        extra_arguments=extra_arguments,
        file_name=str(file_name),
    )

    results = model.run()
    assert isinstance(results, dict)

    compare_model_to_verification_data(
        results, verification_data_dir, prefix=prefix, tmp_path=tmp_path
    )
