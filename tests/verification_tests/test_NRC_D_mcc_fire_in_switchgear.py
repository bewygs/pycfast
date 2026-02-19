from __future__ import annotations

import os
from pathlib import Path

from pycfast import (
    CFASTModel,
    Compartments,
    Devices,
    Fires,
    MaterialProperties,
    MechanicalVents,
    SimulationEnvironment,
    WallVents,
)

from .verification import (
    compare_model_to_verification_data,
    get_verification_data_dir,
)

verification_data_dir = get_verification_data_dir(
    Path(__file__).parent,
    "NRC_Users_Guide" + os.sep + "D_MCC_Fire_in_Switchgear",
)


def test_mcc_in_switchgear_simulation(tmp_path):
    """Test construction of CFASTModel for the MCC_in_switchgear.in file."""
    prefix = "MCC_in_switchgear"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=3600,
        print=600,
        smokeview=10,
        spreadsheet=10,
        init_pressure=101300,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
    )

    material_properties = [
        MaterialProperties(
            id="SwMCCConcrete",
            material="Switchgear MCC Concrete (user''s guide)",
            conductivity=1.6,
            density=2400,
            specific_heat=0.75,
            thickness=0.6,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="SwMCCSteel",
            material="Switchgear MCC Steel (user''s guide)",
            conductivity=54,
            density=7850,
            specific_heat=0.465,
            thickness=0.0015,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="THIEF",
            material="Thief Cable (per NUREG CR 6931)",
            conductivity=0.2,
            density=2264,
            specific_heat=1.5,
            thickness=0.015,
            emissivity=0.8,
        ),
    ]

    compartments = [
        Compartments(
            id="Low Ceiling Area",
            depth=8.5,
            height=3,
            width=8.5,
            ceiling_mat_id="SwMCCConcrete",
            ceiling_thickness=0.6,
            wall_mat_id="SwMCCConcrete",
            wall_thickness=0.6,
            floor_mat_id="SwMCCConcrete",
            floor_thickness=0.6,
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="High Ceiling Area",
            depth=8.5,
            height=9.1,
            width=8.6,
            ceiling_mat_id="SwMCCConcrete",
            ceiling_thickness=0.6,
            wall_mat_id="SwMCCConcrete",
            wall_thickness=0.6,
            floor_mat_id="SwMCCConcrete",
            floor_thickness=0.6,
            origin_x=8.5,
            origin_y=0,
            origin_z=0,
        ),
    ]

    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["Low Ceiling Area", "High Ceiling Area"],
            bottom=0,
            height=2.9,
            width=8.5,
            face="RIGHT",
            offset=0,
        ),
        WallVents(
            id="WallVent_2",
            comps_ids=["High Ceiling Area", "OUTSIDE"],
            bottom=0,
            height=0.013,
            width=1,
            face="FRONT",
            offset=5.97,
        ),
        WallVents(
            id="WallVent_3",
            comps_ids=["Low Ceiling Area", "OUTSIDE"],
            bottom=0,
            height=0.013,
            width=1,
            face="REAR",
            offset=2.5,
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["OUTSIDE", "Low Ceiling Area"],
            area=[0.2, 0.2],
            heights=[2.45, 2.45],
            flow=0.735,
            cutoffs=[200, 300],
            offsets=[0, 4.25],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_2",
            comps_ids=["High Ceiling Area", "OUTSIDE"],
            area=[0.2, 0.2],
            heights=[6.05, 6.05],
            flow=0.735,
            cutoffs=[200, 300],
            offsets=[8.6, 4.25],
            filter_time=0,
            filter_efficiency=0,
        ),
    ]

    fires = [
        Fires(
            id="MCC 702 kW",
            comp_id="Low Ceiling Area",
            fire_id="MCC 702 kW_Fire",
            location=[2.8, 4.15],
            carbon=3,
            chlorine=0.5,
            hydrogen=4.5,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=10300,
            radiative_fraction=0.53,
            data_table=[
                [0, 0, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [72, 7.02, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [144, 28.08, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [216, 63.18, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [288, 112.32, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [360, 175.5, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [432, 252.72, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [504, 343.98, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [576, 449.28, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [648, 568.62, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [720, 702, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [1200, 702, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [2340, 0, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [2350, 0, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
            ],
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1",
            comp_id="Low Ceiling Area",
            location=[2.8, 4.15, 2.6],
            type="CYLINDER",
            material_id="THIEF",
            surface_orientation="FLOOR",
            temperature_depth=0.00405,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2",
            comp_id="Low Ceiling Area",
            location=[3, 5.5, 2.6],
            type="CYLINDER",
            material_id="THIEF",
            normal=[-0.1449999, -0.9787492, -0.1449998],
            temperature_depth=0.00405,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 3",
            comp_id="High Ceiling Area",
            location=[4.25, 4.25, 9],
            type="CYLINDER",
            material_id="THIEF",
            surface_orientation="CEILING",
            temperature_depth=0.00405,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 4",
            comp_id="Low Ceiling Area",
            location=[3.5, 5, 2.4],
            type="CYLINDER",
            material_id="SwMCCSteel",
            normal=[-0.6357073, -0.7719302, 0],
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
        wall_vents=wall_vents,
        ceiling_floor_vents=[],
        mechanical_vents=mechanical_vents,
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


def test_mcc_in_switchgear_one_compartment_simulation(tmp_path):
    """Test construction of CFASTModel for the MCC_in_switchgear_one_compartment.in file."""
    prefix = "MCC_in_switchgear_one_compartment"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
        time_simulation=3600,
        print=600,
        smokeview=10,
        spreadsheet=10,
        init_pressure=101300,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
    )

    material_properties = [
        MaterialProperties(
            id="SwMCCConcrete",
            material="Switchgear MCC Concrete (user''s guide)",
            conductivity=1.6,
            density=2400,
            specific_heat=0.75,
            thickness=0.6,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="SwMCCSteel",
            material="Switchgear MCC Steel (user''s guide)",
            conductivity=54,
            density=7850,
            specific_heat=0.465,
            thickness=0.0015,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="THIEF",
            material="Thief Cable (per NUREG CR 6931)",
            conductivity=0.2,
            density=2264,
            specific_heat=1.5,
            thickness=0.015,
            emissivity=0.8,
        ),
    ]

    compartments = [
        Compartments(
            id="Low Ceiling Area",
            depth=8.5,
            height=9.1,
            width=17.1,
            ceiling_mat_id="SwMCCConcrete",
            ceiling_thickness=0.6,
            wall_mat_id="SwMCCConcrete",
            wall_thickness=0.6,
            floor_mat_id="SwMCCConcrete",
            floor_thickness=0.6,
            cross_sect_areas=[145.35, 145.35, 73.1, 73.1],
            cross_sect_heights=[0, 2.99, 3.01, 9.1],
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    wall_vents = [
        WallVents(
            id="WallVent_2",
            comps_ids=["Low Ceiling Area", "OUTSIDE"],
            bottom=0,
            height=0.013,
            width=1,
            face="FRONT",
            offset=8.05,
        ),
        WallVents(
            id="WallVent_3",
            comps_ids=["Low Ceiling Area", "OUTSIDE"],
            bottom=0,
            height=0.013,
            width=1,
            face="REAR",
            offset=2.5,
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["OUTSIDE", "Low Ceiling Area"],
            area=[0.2, 0.2],
            heights=[2.45, 2.45],
            flow=0.735,
            cutoffs=[200, 300],
            offsets=[0, 4.25],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_2",
            comps_ids=["Low Ceiling Area", "OUTSIDE"],
            area=[0.2, 0.2],
            heights=[6.05, 6.05],
            flow=0.735,
            cutoffs=[200, 300],
            offsets=[17.1, 4.25],
            filter_time=0,
            filter_efficiency=0,
        ),
    ]

    fires = [
        Fires(
            id="MCC 702 kW",
            comp_id="Low Ceiling Area",
            fire_id="MCC 702 kW_Fire",
            location=[2.8, 4.15],
            carbon=3,
            chlorine=0.5,
            hydrogen=4.5,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=10300,
            radiative_fraction=0.53,
            data_table=[
                [0, 0, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [72, 7.02, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [144, 28.08, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [216, 63.18, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [288, 112.32, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [360, 175.5, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [432, 252.72, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [504, 343.98, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [576, 449.28, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [648, 568.62, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [720, 702, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [1200, 702, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [2340, 0, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [2350, 0, 2.4, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
            ],
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1",
            comp_id="Low Ceiling Area",
            location=[2.8, 4.15, 2.6],
            type="CYLINDER",
            material_id="THIEF",
            surface_orientation="FLOOR",
            temperature_depth=0.00405,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2",
            comp_id="Low Ceiling Area",
            location=[3, 5.5, 2.6],
            type="CYLINDER",
            material_id="THIEF",
            normal=[-0.1449999, -0.9787492, -0.1449998],
            temperature_depth=0.00405,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 3",
            comp_id="Low Ceiling Area",
            location=[8.6, 4.25, 9],
            type="CYLINDER",
            material_id="THIEF",
            surface_orientation="FLOOR",
            temperature_depth=0.00405,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 4",
            comp_id="Low Ceiling Area",
            location=[3.5, 5, 2.4],
            type="CYLINDER",
            material_id="SwMCCSteel",
            normal=[-0.6357073, -0.7719302, 0],
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
        wall_vents=wall_vents,
        ceiling_floor_vents=[],
        mechanical_vents=mechanical_vents,
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
