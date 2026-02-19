from __future__ import annotations

from pathlib import Path

from pycfast import (
    CeilingFloorVents,
    CFASTModel,
    Compartments,
    Fires,
    SimulationEnvironment,
    WallVents,
)

from .verification import (
    compare_model_to_verification_data,
    get_verification_data_dir,
)

verification_data_dir = get_verification_data_dir(Path(__file__).parent, "Mass_Balance")


def test_species_mass_1_simulation(tmp_path):
    """Test construction of CFASTModel for the species_mass_1.in file."""
    prefix = "species_mass_1"

    simulation_env = SimulationEnvironment(
        title="Default example fire for user guide",
        time_simulation=2000,
        print=120,
        smokeview=10,
        spreadsheet=30,
        init_pressure=101300,
        relative_humidity=0,
        interior_temperature=20,
        exterior_temperature=20,
    )

    compartments = [
        Compartments(
            id="Comp 1",
            depth=5,
            height=6,
            width=3,
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
            id="simple burner",
            comp_id="Comp 1",
            fire_id="simple burner_Fire",
            location=[1.5, 2.5],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0,
            data_table=[
                [0, 0, 0, 0.07069, 0, 0, 0, 0, 0],
                [30, 1, 0, 0.07069, 0, 0, 0, 0, 0],
                [330, 1, 0, 0.07069, 0, 0, 0, 0, 0],
                [360, 0, 0, 0.07069, 0, 0, 0, 0, 0],
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
        ceiling_floor_vents=[],
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


def test_species_mass_2_simulation(tmp_path):
    """Test construction of CFASTModel for the species_mass_2.in file."""
    prefix = "species_mass_2"

    simulation_env = SimulationEnvironment(
        title="Default example fire for user guide",
        time_simulation=2000,
        print=120,
        smokeview=10,
        spreadsheet=30,
        init_pressure=101300,
        relative_humidity=0,
        interior_temperature=20,
        exterior_temperature=20,
    )

    compartments = [
        Compartments(
            id="Comp 1",
            depth=5,
            height=8,
            width=2,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Comp 2",
            depth=3,
            height=8,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=5,
            origin_z=0,
        ),
    ]

    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["Comp 1", "Comp 2"],
            bottom=0,
            height=6,
            width=1,
            face="REAR",
            offset=0.5,
        ),
    ]

    fires = [
        Fires(
            id="simple burner",
            comp_id="Comp 1",
            fire_id="simple burner_Fire",
            location=[1, 2.5],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0.35,
            data_table=[
                [0, 0, 0, 0.07069, 0, 0, 0, 0, 0],
                [30, 1, 0, 0.07069, 0, 0, 0, 0, 0],
                [330, 1, 0, 0.07069, 0, 0, 0, 0, 0],
                [360, 0, 0, 0.07069, 0, 0, 0, 0, 0],
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
        wall_vents=wall_vents,
        ceiling_floor_vents=[],
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


def test_species_mass_3_simulation(tmp_path):
    """Test construction of CFASTModel for the species_mass_3.in file."""
    prefix = "species_mass_3"

    simulation_env = SimulationEnvironment(
        title="Default example fire for user guide",
        time_simulation=2000,
        print=120,
        smokeview=10,
        spreadsheet=30,
        init_pressure=101300,
        relative_humidity=0,
        interior_temperature=20,
        exterior_temperature=20,
    )

    compartments = [
        Compartments(
            id="Comp 1",
            depth=5,
            height=4,
            width=9,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Comp 2",
            depth=5,
            height=2,
            width=9,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=4,
        ),
    ]

    ceiling_floor_vents = [
        CeilingFloorVents(
            id="CeilFloorVent_1",
            comps_ids=["Comp 2", "Comp 1"],
            area=4,
            type="FLOOR",
            shape="SQUARE",
            offsets=[4.5, 2.5],
        ),
    ]

    fires = [
        Fires(
            id="simple burner",
            comp_id="Comp 1",
            fire_id="simple burner_Fire",
            location=[4.55, 2.5],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0.35,
            data_table=[
                [0, 0, 0, 0.07069, 0, 0, 0, 0, 0],
                [30, 1, 0, 0.07069, 0, 0, 0, 0, 0],
                [330, 1, 0, 0.07069, 0, 0, 0, 0, 0],
                [360, 0, 0, 0.07069, 0, 0, 0, 0, 0],
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
        ceiling_floor_vents=ceiling_floor_vents,
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


def test_species_mass_4_simulation(tmp_path):
    """Test construction of CFASTModel for the species_mass_4.in file."""
    prefix = "species_mass_4"

    simulation_env = SimulationEnvironment(
        title="Default example fire for user guide",
        time_simulation=10000,
        print=120,
        smokeview=10,
        spreadsheet=10,
        init_pressure=101300,
        relative_humidity=0,
        interior_temperature=20,
        exterior_temperature=20,
        max_time_step=0.1,
    )

    compartments = [
        Compartments(
            id="Comp 1",
            depth=4,
            height=4,
            width=4,
            shaft=True,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Comp 2",
            depth=4,
            height=4,
            width=4,
            shaft=True,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=4,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Comp 3",
            depth=4,
            height=4,
            width=4,
            shaft=True,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=4,
            origin_y=0,
            origin_z=4,
        ),
        Compartments(
            id="Comp 4",
            depth=4,
            height=4,
            width=4,
            shaft=True,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=4,
        ),
    ]

    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["Comp 1", "Comp 2"],
            bottom=0,
            height=4,
            width=4,
            face="RIGHT",
            offset=0,
            open_close_criterion="TIME",
            time=[1000, 1001],
            fraction=[0, 1],
        ),
        WallVents(
            id="WallVent_2",
            comps_ids=["Comp 3", "Comp 4"],
            bottom=0,
            height=4,
            width=4,
            face="LEFT",
            offset=0,
            open_close_criterion="TIME",
            time=[5000, 5001],
            fraction=[0, 1],
        ),
    ]

    ceiling_floor_vents = [
        CeilingFloorVents(
            id="CeilFloorVent_1",
            comps_ids=["Comp 3", "Comp 2"],
            area=16,
            type="FLOOR",
            shape="SQUARE",
            offsets=[2, 2],
            open_close_criterion="TIME",
            time=[2500, 2501],
            fraction=[0, 1],
        ),
        CeilingFloorVents(
            id="CeilFloorVent_2",
            comps_ids=["OUTSIDE", "Comp 4"],
            area=16,
            type="CEILING",
            shape="SQUARE",
            offsets=[2, 2],
            open_close_criterion="TIME",
            time=[7500, 7501],
            fraction=[0, 1],
        ),
    ]

    fires = [
        Fires(
            id="simple burner",
            comp_id="Comp 1",
            fire_id="simple burner_Fire",
            location=[2, 2],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0,
            data_table=[
                [0, 0, 0, 0.07069, 0, 0, 0, 0, 0],
                [30, 1, 0, 0.07069, 0, 0, 0, 0, 0],
                [330, 1, 0, 0.07069, 0, 0, 0, 0, 0],
                [360, 0, 0, 0.07069, 0, 0, 0, 0, 0],
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
        wall_vents=wall_vents,
        ceiling_floor_vents=ceiling_floor_vents,
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
