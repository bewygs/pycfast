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
    "NRC_Users_Guide" + os.sep + "E_Trash_Fire_in_Cable_Spreading_Room",
)


def test_trash_fire_in_cable_spreading_room_simulation(tmp_path):
    """Test construction of CFASTModel for the Trash_fire_in_cable_spreading_room.in file."""
    prefix = "Trash_fire_in_cable_spreading_room"

    simulation_env = SimulationEnvironment(
        title="Trash Fire in Cable Spreading Room",
        time_simulation=3600,
        print=10,
        smokeview=10,
        spreadsheet=10,
        init_pressure=101300,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
    )

    material_properties = [
        MaterialProperties(
            id="CSRConcrete",
            material="CSR Concrete (user''s guide)",
            conductivity=1.6,
            density=2400,
            specific_heat=0.75,
            thickness=0.5,
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
            id="Cable Spreading Room",
            depth=18.5,
            height=4,
            width=40,
            ceiling_mat_id="CSRConcrete",
            ceiling_thickness=0.5,
            wall_mat_id="CSRConcrete",
            wall_thickness=0.5,
            floor_mat_id="CSRConcrete",
            floor_thickness=0.5,
            cross_sect_areas=[
                700.04,
                700.04,
                635.74,
                635.74,
                483.74,
                483.74,
                514.89,
                514.89,
                634.74,
                634.74,
                699.04,
                699.04,
                291.46,
                291.46,
            ],
            cross_sect_heights=[
                0,
                1.799,
                1.8,
                2.199,
                2.2,
                2.399,
                2.4,
                2.799,
                2.8,
                3.199,
                3.2,
                3.599,
                3.6,
                4,
            ],
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["Cable Spreading Room", "OUTSIDE"],
            bottom=0,
            height=0.01,
            width=2,
            face="FRONT",
            offset=5,
        ),
        WallVents(
            id="WallVent_2",
            comps_ids=["Cable Spreading Room", "OUTSIDE"],
            bottom=0,
            height=0.01,
            width=2,
            face="FRONT",
            offset=33,
        ),
        WallVents(
            id="WallVent_3",
            comps_ids=["Cable Spreading Room", "OUTSIDE"],
            bottom=0.01,
            height=1.99,
            width=2,
            face="FRONT",
            offset=33,
            open_close_criterion="TIME",
            time=[0, 770, 771],
            fraction=[0, 0, 1],
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["OUTSIDE", "Cable Spreading Room"],
            area=[0.25, 0.25],
            heights=[2.43, 2.43],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.7,
            cutoffs=[200, 300],
            offsets=[10.25, 3.25],
            open_close_criterion="TIME",
            time=[170, 171],
            fraction=[1, 0],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_2",
            comps_ids=["OUTSIDE", "Cable Spreading Room"],
            area=[0.25, 0.25],
            heights=[2.43, 2.43],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.7,
            cutoffs=[200, 300],
            offsets=[29.75, 3.25],
            open_close_criterion="TIME",
            time=[280.1, 281.1],
            fraction=[1, 0],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_3",
            comps_ids=["Cable Spreading Room", "OUTSIDE"],
            area=[0.25, 0.25],
            heights=[2.43, 2.43],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.7,
            cutoffs=[200, 300],
            offsets=[10.25, 15.25],
            open_close_criterion="TIME",
            time=[280.1, 281.1],
            fraction=[1, 0],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_4",
            comps_ids=["Cable Spreading Room", "OUTSIDE"],
            area=[0.25, 0.25],
            heights=[2.43, 2.43],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.7,
            cutoffs=[200, 300],
            offsets=[29.75, 15.25],
            open_close_criterion="TIME",
            time=[280.1, 281.1],
            fraction=[1, 0],
            filter_time=0,
            filter_efficiency=0,
        ),
    ]

    fires = [
        Fires(
            id="Transient Combustibles",
            comp_id="Cable Spreading Room",
            fire_id="Transient Combustibles_Fire",
            location=[33, 16.3],
            carbon=4,
            chlorine=0,
            hydrogen=7,
            nitrogen=0,
            oxygen=2.5,
            heat_of_combustion=30400,
            radiative_fraction=0.4,
            data_table=[
                [0, 0, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
                [48, 3.17, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
                [96, 12.68, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
                [144, 28.53, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
                [192, 50.72, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
                [240, 79.25, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
                [288, 114.12, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
                [336, 155.33, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
                [384, 202.88, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
                [432, 256.77, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
                [480, 317, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
                [799, 317, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
                [800, 0, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
                [3600, 0, 0.8, 0.282743, 0.014, 0.038, 0, 0, 0],
            ],
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1",
            comp_id="Cable Spreading Room",
            location=[33, 16.3, 1.8],
            type="CYLINDER",
            material_id="THIEF",
            surface_orientation="CEILING",
            temperature_depth=0.0001125,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2",
            comp_id="Cable Spreading Room",
            location=[33, 16.3, 2.3],
            type="CYLINDER",
            material_id="THIEF",
            surface_orientation="CEILING",
            temperature_depth=0.0001125,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 3",
            comp_id="Cable Spreading Room",
            location=[33, 16.3, 3.1],
            type="CYLINDER",
            material_id="THIEF",
            surface_orientation="CEILING",
            temperature_depth=0.0001125,
            depth_units="M",
        ),
        Devices.create_heat_detector(
            id="HeatDetector_1",
            comp_id="Cable Spreading Room",
            location=[4, 15.5, 3.96],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_2",
            comp_id="Cable Spreading Room",
            location=[11.9, 15.5, 3.96],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_3",
            comp_id="Cable Spreading Room",
            location=[19.8, 15.5, 3.96],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_4",
            comp_id="Cable Spreading Room",
            location=[27.7, 15.5, 3.96],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_5",
            comp_id="Cable Spreading Room",
            location=[35.7, 15.5, 3.96],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_6",
            comp_id="Cable Spreading Room",
            location=[4, 9.4, 3.96],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_7",
            comp_id="Cable Spreading Room",
            location=[11.9, 9.4, 3.96],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_8",
            comp_id="Cable Spreading Room",
            location=[27.7, 9.4, 3.96],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_9",
            comp_id="Cable Spreading Room",
            location=[35.7, 9.4, 3.96],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_10",
            comp_id="Cable Spreading Room",
            location=[4, 3.3, 3.96],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_11",
            comp_id="Cable Spreading Room",
            location=[11.9, 3.3, 3.96],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_12",
            comp_id="Cable Spreading Room",
            location=[19.8, 3.3, 3.96],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_13",
            comp_id="Cable Spreading Room",
            location=[27.7, 3.3, 3.96],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_14",
            comp_id="Cable Spreading Room",
            location=[35.7, 3.3, 3.96],
            setpoint=30,
            rti=5,
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
