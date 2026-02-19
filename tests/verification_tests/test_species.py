from __future__ import annotations

from pathlib import Path

from pycfast import (
    CFASTModel,
    Compartments,
    Devices,
    Fires,
    MaterialProperties,
    MechanicalVents,
    SimulationEnvironment,
)

from .verification import (
    compare_model_to_verification_data,
    get_verification_data_dir,
)

verification_data_dir = get_verification_data_dir(Path(__file__).parent, "Species")


def test_species_test_simulation(tmp_path):
    """Test construction of CFASTModel for the species_test.in file."""
    prefix = "species_test"

    simulation_env = SimulationEnvironment(
        title="Species Verification Test",
        time_simulation=200,
        print=200,
        smokeview=0,
        spreadsheet=1,
        init_pressure=101325,
        relative_humidity=0,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=True,
        max_time_step=0.001,
    )

    compartments = [
        Compartments(
            id="Room_1",
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
            id="Methane_Fire",
            comp_id="Room_1",
            fire_id="Species_Fire",
            location=[0.5, 0.5],
            carbon=12,
            chlorine=1,
            hydrogen=9,
            nitrogen=2,
            oxygen=3,
            heat_of_combustion=10000,
            radiative_fraction=0.35,
            data_table=[
                [0, 5, 0, 0.09, 0.063, 0.186, 0.05, 0, 0],
                [1, 5, 0, 0.09, 0.063, 0.186, 0.05, 0, 0],
                [99.999, 5, 0, 0.09, 0.063, 0.186, 0.05, 0, 0],
                [100.001, 0, 0, 0.09, 0.063, 0.186, 0.05, 0, 0],
                [200, 0, 0, 0.09, 0.063, 0.186, 0.05, 0, 0],
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


def test_methane_flame_simple_simulation(tmp_path):
    """Test construction of CFASTModel for the methane_flame_simple.in file."""
    prefix = "methane_flame_simple"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=200,
        print=200,
        smokeview=0,
        spreadsheet=1,
        init_pressure=101325,
        relative_humidity=0,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=True,
        max_time_step=0.001,
    )

    compartments = [
        Compartments(
            id="Room_1",
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
            id="Methane_Fire",
            comp_id="Room_1",
            fire_id="Methane_Fire",
            location=[0.5, 0.5],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0.35,
            data_table=[
                [0, 0, 0, 0.09, 0, 0, 0, 0, 0],
                [1, 5, 0, 0.09, 0, 0, 0, 0, 0],
                [100, 5, 0, 0.09, 0, 0, 0, 0, 0],
                [101, 0, 0, 0.09, 0, 0, 0, 0, 0],
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


def test_gas_tenability_simulation(tmp_path):
    """Test construction of CFASTModel for the gas_tenability.in file."""
    prefix = "gas_tenability"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=900,
        print=60,
        smokeview=15,
        spreadsheet=1,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
        max_time_step=1.9,
    )

    material_properties = [
        MaterialProperties(
            id="Steel",
            material="Steel",
            conductivity=54,
            density=7850,
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
            shaft=True,
            ceiling_mat_id="Steel",
            ceiling_thickness=0.0015,
            wall_mat_id="Steel",
            wall_thickness=0.0015,
            floor_mat_id="Steel",
            floor_thickness=0.0015,
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    fires = [
        Fires(
            id="CO",
            comp_id="Comp 1",
            fire_id="CO_Fire",
            location=[2.5, 2.5],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0.35,
            data_table=[
                [0, 0, 0, 0.36, 0.1, 0, 0, 0, 0],
                [1, 10, 0, 0.36, 0.1, 0, 0, 0, 0],
                [100, 10, 0, 0.36, 0.1, 0, 0, 0, 0],
                [101, 0, 0, 0.36, 0.1, 0, 0, 0, 0],
            ],
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1",
            comp_id="Comp 1",
            location=[2.5, 2.5, 4.9],
            type="PLATE",
            material_id="Steel",
            surface_orientation="CEILING",
            temperature_depth=0.00075,
            depth_units="M",
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


def test_heat_tenability_simulation(tmp_path):
    """Test construction of CFASTModel for the heat_tenability.in file."""
    prefix = "heat_tenability"

    simulation_env = SimulationEnvironment(
        title="Heat Tenability Verification Test",
        time_simulation=900,
        print=1,
        smokeview=15,
        spreadsheet=1,
        init_pressure=101325,
        relative_humidity=0,
        interior_temperature=100,
        exterior_temperature=20,
        adiabatic=True,
        max_time_step=1.9,
    )

    material_properties = [
        MaterialProperties(
            id="Steel",
            material="Steel",
            conductivity=54,
            density=7850,
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
            shaft=True,
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
            location=[2.5, 2.5, 2.5],
            type="PLATE",
            material_id="Steel",
            surface_orientation="FLOOR",
            temperature_depth=0.00075,
            depth_units="M",
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


def test_trace_species_1_simulation(tmp_path):
    """Test construction of CFASTModel for the Trace_Species_1.in file."""
    prefix = "Trace_Species_1"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=200,
        print=200,
        smokeview=0,
        spreadsheet=1,
        init_pressure=101325,
        relative_humidity=0,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=True,
        max_time_step=0.001,
    )

    compartments = [
        Compartments(
            id="Room_1",
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
            id="Methane_Fire",
            comp_id="Room_1",
            fire_id="Methane_Fire",
            location=[0.5, 0.5],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0.35,
            data_table=[
                [0, 0, 0, 0.09, 0.1, 0, 0, 0, 0.001],
                [1, 5, 0, 0.09, 0.1, 0, 0, 0, 0.001],
                [100, 5, 0, 0.09, 0.1, 0, 0, 0, 0.001],
                [101, 0, 0, 0.09, 0.1, 0, 0, 0, 0.001],
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


def test_trace_species_2_simulation(tmp_path):
    """Test construction of CFASTModel for the Trace_Species_2.in file."""
    prefix = "Trace_Species_2"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=80000,
        print=80000,
        smokeview=0,
        spreadsheet=100,
        init_pressure=101325,
        relative_humidity=0,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=True,
        max_time_step=1.9,
    )

    compartments = [
        Compartments(
            id="Room_1",
            depth=10,
            height=2,
            width=10,
            shaft=True,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Room_2",
            depth=10,
            height=2,
            width=10,
            shaft=True,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=10,
            origin_y=0,
            origin_z=0,
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["Room_1", "Room_2"],
            area=[1, 1],
            heights=[1, 1],
            flow=0.01,
            offsets=[0, 5],
            open_close_criterion="TIME",
            time=[100, 101],
            fraction=[0, 1],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_2",
            comps_ids=["Room_2", "Room_1"],
            area=[1, 1],
            heights=[1, 1],
            flow=0.01,
            offsets=[0, 5],
            open_close_criterion="TIME",
            time=[100, 101],
            fraction=[0, 1],
            filter_time=0,
            filter_efficiency=0,
        ),
    ]

    fires = [
        Fires(
            id="Methane_Fire",
            comp_id="Room_1",
            fire_id="Methane_Fire",
            location=[5, 5],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0.35,
            data_table=[
                [0, 0, 0, 0.09, 0, 0, 0, 0, 0.001],
                [1, 5, 0, 0.09, 0, 0, 0, 0, 0.001],
                [100, 5, 0, 0.09, 0, 0, 0, 0, 0.001],
                [101, 0, 0, 0.09, 0, 0, 0, 0, 0.001],
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
        mechanical_vents=mechanical_vents,
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


def test_trace_species_3_simulation(tmp_path):
    """Test construction of CFASTModel for the Trace_Species_3.in file."""
    prefix = "Trace_Species_3"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=84000,
        print=84000,
        smokeview=0,
        spreadsheet=100,
        init_pressure=101325,
        relative_humidity=0,
        interior_temperature=20,
        exterior_temperature=20,
        adiabatic=True,
        max_time_step=1.9,
    )

    compartments = [
        Compartments(
            id="Room_1",
            depth=10,
            height=2,
            width=10,
            shaft=True,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Room_2",
            depth=10,
            height=2,
            width=10,
            shaft=True,
            ceiling_mat_id="OFF",
            wall_mat_id="OFF",
            floor_mat_id="OFF",
            origin_x=10,
            origin_y=0,
            origin_z=0,
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["Room_1", "Room_2"],
            area=[1, 1],
            heights=[1, 1],
            flow=0.01,
            offsets=[0, 5],
            open_close_criterion="TIME",
            time=[100, 101],
            fraction=[0, 1],
            filter_time=0,
            filter_efficiency=100,
        ),
        MechanicalVents(
            id="MechanicalVent_2",
            comps_ids=["Room_2", "Room_1"],
            area=[1, 1],
            heights=[1, 1],
            flow=0.01,
            offsets=[0, 5],
            open_close_criterion="TIME",
            time=[100, 101],
            fraction=[0, 1],
            filter_time=0,
            filter_efficiency=100,
        ),
    ]

    fires = [
        Fires(
            id="Methane_Fire",
            comp_id="Room_1",
            fire_id="Methane_Fire",
            location=[5, 5],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=50000,
            radiative_fraction=0.35,
            data_table=[
                [0, 0, 0, 0.09, 0, 0, 0, 0, 0.001],
                [1, 5, 0, 0.09, 0, 0, 0, 0, 0.001],
                [100, 5, 0, 0.09, 0, 0, 0, 0, 0.001],
                [101, 0, 0, 0.09, 0, 0, 0, 0, 0.001],
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
        mechanical_vents=mechanical_vents,
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
