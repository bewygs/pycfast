from __future__ import annotations

from pathlib import Path

from pycfast import (
    CeilingFloorVents,
    CFASTModel,
    Compartments,
    Fires,
    MechanicalVents,
    SimulationEnvironment,
    WallVents,
)

from .verification import (
    compare_model_to_verification_data,
    get_verification_data_dir,
)

verification_data_dir = get_verification_data_dir(Path(__file__).parent, "Ventilation")


def test_ventilation_1_simulation(tmp_path):
    """Test construction of CFASTModel for the ventilation_1.in file."""
    prefix = "ventilation_1"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=108000,
        print=100,
        smokeview=100,
        spreadsheet=100,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
    )

    compartments = [
        Compartments(
            id="Comp 1",
            depth=5,
            height=3,
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
            bottom=1.495,
            height=0.00999999999999979,
            width=0.01,
            face="RIGHT",
            offset=2.5,
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["OUTSIDE", "Comp 1"],
            area=[1, 1],
            heights=[1.5, 1.5],
            flow=0.01,
            cutoffs=[1000000, 1100000],
            offsets=[0, 2.5],
            filter_time=0,
            filter_efficiency=0,
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
        mechanical_vents=mechanical_vents,
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


def test_leakage_1_simulation(tmp_path):
    """Test construction of CFASTModel for the Leakage_1.in file."""
    prefix = "Leakage_1"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=3600,
        print=60,
        smokeview=15,
        spreadsheet=15,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=True,
    )

    compartments = [
        Compartments(
            id="Comp 1",
            depth=1,
            height=1,
            width=1,
            shaft=True,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
            leak_area_ratio=[0.01, 0],
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["OUTSIDE", "Comp 1"],
            area=[0.1, 0.1],
            heights=[0.5, 0.5],
            flow=0.01,
            offsets=[0, 0.5],
            open_close_criterion="TIME",
            time=[0, 1],
            fraction=[0, 1],
            filter_time=0,
            filter_efficiency=0,
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
        mechanical_vents=mechanical_vents,
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


def test_leakage_2_simulation(tmp_path):
    """Test construction of CFASTModel for the Leakage_2.in file."""
    prefix = "Leakage_2"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=3600,
        print=60,
        smokeview=15,
        spreadsheet=15,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=True,
    )

    compartments = [
        Compartments(
            id="Comp 1",
            depth=1,
            height=1,
            width=1,
            shaft=True,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
            leak_area_ratio=[0, 0.01],
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["OUTSIDE", "Comp 1"],
            area=[0.1, 0.1],
            heights=[0.5, 0.5],
            flow=0.01,
            offsets=[0, 0.5],
            open_close_criterion="TIME",
            time=[0, 1],
            fraction=[0, 1],
            filter_time=0,
            filter_efficiency=0,
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
        mechanical_vents=mechanical_vents,
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


def test_surface_opened_fraction_1_simulation(tmp_path):
    """Test construction of CFASTModel for the surface_opened_fraction_1.in file."""
    prefix = "surface_opened_fraction_1"

    simulation_env = SimulationEnvironment(
        title="surface_opened_fraction",
        time_simulation=1,
        print=1,
        smokeview=1,
        spreadsheet=1,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=26.85,
        exterior_temperature=26.85,
        extra_custom="&DIAG UPPER_LAYER_THICKNESS = 1 VERIFICATION_TIME_STEP = 0.5/",
    )
    compartments = [
        Compartments(
            id="Comp 1",
            depth=4,
            height=3,
            width=5,
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
            height=5,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=3,
        ),
        Compartments(
            id="Comp 3",
            depth=4,
            height=6,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=5,
            origin_y=0,
            origin_z=1,
        ),
    ]

    wall_vents = [
        WallVents(
            id="HVENT 1",
            comps_ids=["Comp 1", "OUTSIDE"],
            bottom=2.5,
            height=0.5,
            width=1,
            face="FRONT",
            offset=2,
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
        ),
        WallVents(
            id="HVENT 2",
            comps_ids=["Comp 1", "OUTSIDE"],
            bottom=0,
            height=0.5,
            width=1,
            face="FRONT",
            offset=2,
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
        ),
        WallVents(
            id="HVENT 3",
            comps_ids=["Comp 1", "OUTSIDE"],
            bottom=0,
            height=1,
            width=0.75,
            face="RIGHT",
            offset=0.5,
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
        ),
        WallVents(
            id="HVENT 4",
            comps_ids=["Comp 1", "Comp 3"],
            bottom=1,
            height=1.5,
            width=0.75,
            face="RIGHT",
            offset=0.5,
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
        ),
        WallVents(
            id="HVENT 5",
            comps_ids=["Comp 1", "OUTSIDE"],
            bottom=0.5,
            height=2.5,
            width=1,
            face="LEFT",
            offset=1,
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
        ),
        WallVents(
            id="HVENT 6",
            comps_ids=["Comp 2", "Comp 3"],
            bottom=0,
            height=4,
            width=0.75,
            face="RIGHT",
            offset=0.5,
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
        ),
        WallVents(
            id="HVENT 7",
            comps_ids=["Comp 2", "OUTSIDE"],
            bottom=4,
            height=0.5,
            width=0.75,
            face="RIGHT",
            offset=0.5,
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
        ),
        WallVents(
            id="HVENT 8",
            comps_ids=["Comp 2", "OUTSIDE"],
            bottom=0.5,
            height=4.5,
            width=1,
            face="LEFT",
            offset=1,
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
        ),
    ]

    ceiling_floor_vents = [
        CeilingFloorVents(
            id="VVENT 1",
            comps_ids=["Comp 2", "Comp 1"],
            area=1,
            type="FLOOR",
            shape="SQUARE",
            offsets=[2, 2],
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
        ),
        CeilingFloorVents(
            id="VVENT 2",
            comps_ids=["Comp 1", "OUTSIDE"],
            area=1,
            type="FLOOR",
            shape="ROUND",
            offsets=[2.5, 2],
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
        ),
        CeilingFloorVents(
            id="VVENT 3",
            comps_ids=["OUTSIDE", "Comp 3"],
            area=1,
            type="CEILING",
            shape="SQUARE",
            offsets=[2.5, 2.5],
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MVENT 1",
            comps_ids=["Comp 1", "OUTSIDE"],
            area=[1, 1],
            heights=[2, 2],
            flow=0.2,
            offsets=[2.5, 4],
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MVENT 2",
            comps_ids=["Comp 1", "Comp 2"],
            area=[1, 1],
            heights=[3, 3],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.2,
            offsets=[1, 1],
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MVENT 3",
            comps_ids=["Comp 1", "Comp 3"],
            area=[0.25, 0.25],
            heights=[2.75, 2.75],
            flow=0.2,
            offsets=[5, 3],
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MVENT 4",
            comps_ids=["Comp 2", "Comp 3"],
            area=[0.25, 0.25],
            heights=[0.25, 0.25],
            flow=0.2,
            offsets=[5, 3],
            open_close_criterion="TIME",
            time=[0, 0.5, 1],
            fraction=[0, 0.5, 1],
            filter_time=0,
            filter_efficiency=0,
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
        mechanical_vents=mechanical_vents,
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


def test_ventilation_2_simulation(tmp_path):
    """Test construction of CFASTModel for the ventilation_2.in file."""
    prefix = "ventilation_2"

    simulation_env = SimulationEnvironment(
        title="Default example fire for user guide",
        time_simulation=3000,
        print=120,
        smokeview=10,
        spreadsheet=30,
        init_pressure=101300,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
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
            bottom=1.5,
            height=1,
            width=1,
            face="RIGHT",
            offset=1.5,
        ),
        WallVents(
            id="WallVent_2",
            comps_ids=["Comp 3", "Comp 4"],
            bottom=1.5,
            height=1,
            width=1,
            face="LEFT",
            offset=1.5,
        ),
    ]

    ceiling_floor_vents = [
        CeilingFloorVents(
            id="CeilFloorVent_1",
            comps_ids=["Comp 3", "Comp 2"],
            area=1,
            type="FLOOR",
            shape="SQUARE",
            offsets=[2, 2],
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["OUTSIDE", "Comp 1"],
            area=[1, 1],
            heights=[2, 2],
            flow=1,
            cutoffs=[999999, 1000000],
            offsets=[0, 2],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_2",
            comps_ids=["Comp 4", "OUTSIDE"],
            area=[1, 1],
            heights=[2, 2],
            flow=1,
            offsets=[0, 2],
            filter_time=0,
            filter_efficiency=0,
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
        mechanical_vents=mechanical_vents,
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


def test_ventilation_3_simulation(tmp_path):
    """Test construction of CFASTModel for the ventilation_3.in file."""
    prefix = "ventilation_3"

    simulation_env = SimulationEnvironment(
        title="Default example fire for user guide",
        time_simulation=1500,
        print=120,
        smokeview=10,
        spreadsheet=10,
        init_pressure=101300,
        relative_humidity=50,
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
            height=2,
            width=1,
            face="RIGHT",
            offset=0,
            open_close_criterion="TIME",
            time=[200, 201],
            fraction=[0, 1],
        ),
        WallVents(
            id="WallVent_2",
            comps_ids=["Comp 3", "Comp 4"],
            bottom=0,
            height=3,
            width=1,
            face="LEFT",
            offset=1,
            open_close_criterion="TIME",
            time=[700, 701],
            fraction=[0, 1],
        ),
    ]

    ceiling_floor_vents = [
        CeilingFloorVents(
            id="CeilFloorVent_1",
            comps_ids=["Comp 3", "Comp 2"],
            area=3,
            type="FLOOR",
            shape="ROUND",
            offsets=[2, 2],
            open_close_criterion="TIME",
            time=[500, 501],
            fraction=[0, 1],
        ),
        CeilingFloorVents(
            id="CeilFloorVent_2",
            comps_ids=["OUTSIDE", "Comp 4"],
            area=4,
            type="CEILING",
            shape="ROUND",
            offsets=[2, 2],
            open_close_criterion="TIME",
            time=[1000, 1001],
            fraction=[0, 1],
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["OUTSIDE", "Comp 1"],
            area=[1, 1],
            heights=[2, 2],
            flow=1,
            cutoffs=[999999, 1000000],
            offsets=[0, 2],
            open_close_criterion="TIME",
            time=[15, 16],
            fraction=[1, 0],
            filter_time=0,
            filter_efficiency=0,
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
        mechanical_vents=mechanical_vents,
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


def test_ventilation_4_simulation(tmp_path):
    """Test construction of CFASTModel for the ventilation_4.in file."""
    prefix = "ventilation_4"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=5000,
        print=50,
        smokeview=10,
        spreadsheet=50,
        init_pressure=101325,
        relative_humidity=0,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=True,
    )

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
            height=4,
            width=1.5,
            face="RIGHT",
            offset=1,
        ),
    ]

    fires = [
        Fires(
            id="simple",
            comp_id="Comp 1",
            fire_id="simple_Fire",
            location=[2.5, 2.5],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0.33,
            data_table=[
                [0, 0, 0, 0.071, 0, 0, 0, 0, 0],
                [30, 200, 0, 0.071, 0, 0, 0, 0, 0],
                [330, 200, 0, 0.071, 0, 0, 0, 0, 0],
                [360, 200, 0, 0.071, 0, 0, 0, 0, 0],
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


def test_vvent_tests_simulation(tmp_path):
    """Test construction of CFASTModel for the VVent_Tests.in file."""
    prefix = "VVent_Tests"

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
    )

    compartments = [
        Compartments(
            id="Comp 1 Up",
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
        Compartments(
            id="Comp 2 Up",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=5,
        ),
        Compartments(
            id="Comp 3 Up",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=10,
        ),
        Compartments(
            id="Comp 1 Down",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=7,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Comp 2 Down",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=7,
            origin_y=0,
            origin_z=5,
        ),
        Compartments(
            id="Comp 3 Down",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=7,
            origin_y=0,
            origin_z=10,
        ),
        Compartments(
            id="Comp 1 Both",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=14,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Comp 2 Both",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=14,
            origin_y=0,
            origin_z=5,
        ),
        Compartments(
            id="Comp 3 Both",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=14,
            origin_y=0,
            origin_z=10,
        ),
        Compartments(
            id="Comp 1 All Vents",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=21,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Comp 2 All Vents",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=21,
            origin_y=0,
            origin_z=5,
        ),
        Compartments(
            id="Comp 3 All Vents",
            depth=5,
            height=5,
            width=5,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=21,
            origin_y=0,
            origin_z=10,
        ),
    ]

    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["Comp 3 All Vents", "OUTSIDE"],
            bottom=2.25,
            height=0.5,
            width=0.5,
            face="FRONT",
            offset=2.25,
            open_close_criterion="TIME",
            time=[0, 0],
            fraction=[1, 1],
        ),
    ]

    ceiling_floor_vents = [
        CeilingFloorVents(
            id="CeilFloorVent_1",
            comps_ids=["OUTSIDE", "Comp 3 Up"],
            area=0.25,
            type="CEILING",
            shape="ROUND",
            offsets=[2.5, 2.5],
        ),
        CeilingFloorVents(
            id="CeilFloorVent_2",
            comps_ids=["Comp 3 Up", "Comp 2 Up"],
            area=0.25,
            type="FLOOR",
            shape="ROUND",
            offsets=[2.5, 2.5],
        ),
        CeilingFloorVents(
            id="CeilFloorVent_3",
            comps_ids=["Comp 2 Up", "Comp 1 Up"],
            area=0.25,
            type="FLOOR",
            shape="ROUND",
            offsets=[2.5, 2.5],
        ),
        CeilingFloorVents(
            id="CeilFloorVent_4",
            comps_ids=["Comp 3 Down", "Comp 2 Down"],
            area=0.25,
            type="FLOOR",
            shape="ROUND",
            offsets=[2.5, 2.5],
        ),
        CeilingFloorVents(
            id="CeilFloorVent_5",
            comps_ids=["Comp 2 Down", "Comp 1 Down"],
            area=0.25,
            type="FLOOR",
            shape="ROUND",
            offsets=[2.5, 2.5],
        ),
        CeilingFloorVents(
            id="CeilFloorVent_6",
            comps_ids=["Comp 1 Down", "OUTSIDE"],
            area=0.25,
            type="FLOOR",
            shape="ROUND",
            offsets=[2.5, 2.5],
        ),
        CeilingFloorVents(
            id="CeilFloorVent_7",
            comps_ids=["OUTSIDE", "Comp 3 Both"],
            area=0.25,
            type="CEILING",
            shape="ROUND",
            offsets=[2.5, 2.5],
        ),
        CeilingFloorVents(
            id="CeilFloorVent_8",
            comps_ids=["Comp 3 Both", "Comp 2 Both"],
            area=0.25,
            type="FLOOR",
            shape="ROUND",
            offsets=[2.5, 2.5],
        ),
        CeilingFloorVents(
            id="CeilFloorVent_9",
            comps_ids=["Comp 2 Both", "Comp 1 Both"],
            area=0.25,
            type="FLOOR",
            shape="ROUND",
            offsets=[2.5, 2.5],
        ),
        CeilingFloorVents(
            id="CeilFloorVent_10",
            comps_ids=["Comp 1 Both", "OUTSIDE"],
            area=0.25,
            type="FLOOR",
            shape="ROUND",
            offsets=[2.5, 2.5],
        ),
        CeilingFloorVents(
            id="CeilFloorVent_11",
            comps_ids=["Comp 3 All Vents", "Comp 2 All Vents"],
            area=0.25,
            type="FLOOR",
            shape="ROUND",
            offsets=[2.5, 2.5],
        ),
        CeilingFloorVents(
            id="CeilFloorVent_12",
            comps_ids=["Comp 2 All Vents", "Comp 1 All Vents"],
            area=0.25,
            type="FLOOR",
            shape="ROUND",
            offsets=[2.5, 2.5],
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["OUTSIDE", "Comp 1 Up"],
            area=[0.25, 0.25],
            heights=[2.5, 2.5],
            flow=0.1,
            offsets=[0, 2.5],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_2",
            comps_ids=["OUTSIDE", "Comp 3 Down"],
            area=[0.25, 0.25],
            heights=[12.5, 2.5],
            flow=0.1,
            offsets=[2.5, 0],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_3",
            comps_ids=["OUTSIDE", "Comp 2 Both"],
            area=[0.25, 0.25],
            heights=[7.5, 2.5],
            flow=0.1,
            offsets=[2.5, 0],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_4",
            comps_ids=["OUTSIDE", "Comp 1 All Vents"],
            area=[0.25, 0.25],
            heights=[2.5, 2.5],
            flow=0.1,
            offsets=[2.5, 0],
            filter_time=0,
            filter_efficiency=0,
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
        mechanical_vents=mechanical_vents,
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
