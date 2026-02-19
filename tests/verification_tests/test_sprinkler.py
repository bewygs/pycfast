from __future__ import annotations

from pathlib import Path

from pycfast import (
    CFASTModel,
    Compartments,
    Devices,
    Fires,
    SimulationEnvironment,
)

from .verification import (
    compare_model_to_verification_data,
    get_verification_data_dir,
)

verification_data_dir = get_verification_data_dir(Path(__file__).parent, "Sprinkler")


def test_sprinkler_1_simulation(tmp_path):
    """Test construction of CFASTModel for the sprinkler_1.in file."""
    prefix = "sprinkler_1"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=5000,
        print=50,
        smokeview=10,
        spreadsheet=1,
        init_pressure=101325,
        relative_humidity=0,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=True,
    )

    compartments = [
        Compartments(
            id="Comp 1",
            depth=4,
            height=4,
            width=4,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    fire_hrr_data = [
        [0, 10, 0, 0.09, 0, 0, 0, 0, 0],
        [5000, 10, 0, 0.09, 0, 0, 0, 0, 0],
    ]

    fires = [
        Fires(
            id="New Fire",
            comp_id="Comp 1",
            fire_id="New Fire_Fire",
            location=[2, 2],
            carbon=1,
            hydrogen=4,
            oxygen=0,
            nitrogen=0,
            chlorine=0,
            heat_of_combustion=50000,
            radiative_fraction=0.5,
            data_table=fire_hrr_data,
        ),
    ]

    devices = [
        Devices.create_sprinkler(
            id="Sprinkler_1",
            comp_id="Comp 1",
            location=[2, 2, 3.96],
            setpoint=40,
            rti=100,
            spray_density=7e-05,
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
