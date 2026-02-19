from __future__ import annotations

from pathlib import Path

from pycfast import (
    CFASTModel,
    Compartments,
    Fires,
    SimulationEnvironment,
)

from .verification import (
    compare_model_to_verification_data,
    get_verification_data_dir,
)

verification_data_dir = get_verification_data_dir(
    Path(__file__).parent, "Energy_Balance"
)


def test_sealed_test_simulation(tmp_path):
    """Test construction of CFASTModel for the sealed_test.in file."""
    prefix = "sealed_test"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=900,
        print=50,
        smokeview=10,
        spreadsheet=10,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=True,
    )

    compartments = [
        Compartments(
            id="Compartment 1",
            depth=5,
            height=5,
            width=5,
            shaft=True,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    fires = [
        Fires(
            id="100 kW",
            comp_id="Compartment 1",
            fire_id="100 kW_Fire",
            location=[2.5, 2.5],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0.35,
            data_table=[
                [0, 100, 0, 0.3, 0, 0, 0, 0, 0],
                [1800, 100, 0, 0.3, 0, 0, 0, 0, 0],
            ],
        ),
    ]

    file_name = tmp_path / f"{prefix}.in"
    cfast_exe = "cfast"
    extra_arguments = ["-f"]
    model = CFASTModel(
        simulation_environment=simulation_env,
        material_properties=[],
        compartments=compartments,
        wall_vents=[],
        mechanical_vents=[],
        fires=fires,
        cfast_exe=cfast_exe,
        extra_arguments=extra_arguments,
        file_name=str(file_name),
    )

    results = model.run()
    assert isinstance(results, dict)

    compare_model_to_verification_data(
        results, verification_data_dir, prefix=prefix, tmp_path=tmp_path
    )


def test_sealed_test_2_layers_simulation(tmp_path):
    """Test construction of CFASTModel for the sealed_test_2_layers.in file."""
    prefix = "sealed_test_2_layers"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=900,
        print=50,
        smokeview=10,
        spreadsheet=10,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=True,
    )

    compartments = [
        Compartments(
            id="Compartment 1",
            depth=5,
            height=5,
            width=5,
            shaft=False,  # No SHAFT = .TRUE. for this file
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    fires = [
        Fires(
            id="100 kW",
            comp_id="Compartment 1",
            fire_id="100 kW_Fire",
            location=[2.5, 2.5],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0.35,
            data_table=[
                [0, 100, 0, 0.3, 0, 0, 0, 0, 0],
                [1800, 100, 0, 0.3, 0, 0, 0, 0, 0],
            ],
        ),
    ]

    file_name = tmp_path / f"{prefix}.in"
    cfast_exe = "cfast"
    extra_arguments = ["-f"]
    model = CFASTModel(
        simulation_environment=simulation_env,
        material_properties=[],
        compartments=compartments,
        wall_vents=[],
        mechanical_vents=[],
        fires=fires,
        cfast_exe=cfast_exe,
        extra_arguments=extra_arguments,
        file_name=str(file_name),
    )

    results = model.run()
    assert isinstance(results, dict)

    compare_model_to_verification_data(
        results, verification_data_dir, prefix=prefix, tmp_path=tmp_path
    )
