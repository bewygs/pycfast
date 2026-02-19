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
    "NRC_Users_Guide" + os.sep + "G_Transient_Fire_in_Corridor",
)


def test_transient_fire_in_corridor_simulation(tmp_path):
    """Test construction of CFASTModel for the Transient in Corridor.in file."""
    prefix = "Transient in Corridor"

    simulation_env = SimulationEnvironment(
        title="MCC Fire Corridor",
        time_simulation=3600,
        print=300,
        smokeview=10,
        spreadsheet=10,
        init_pressure=101300,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
    )

    material_properties = [
        MaterialProperties(
            id="CorConcrete",
            material="Corridor Concrete (User''s Guide)",
            conductivity=1.6,
            density=2400,
            specific_heat=0.75,
            thickness=0.5,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="CorXPE",
            material="Corridor XPE Cable (NUREG 1824)",
            conductivity=0.21,
            density=1375,
            specific_heat=1.56,
            thickness=0.003,
            emissivity=0.9,
        ),
    ]

    compartments = [
        Compartments(
            id="Compartment 1",
            depth=4.1,
            height=6.1,
            width=8.1,
            hall=True,
            ceiling_mat_id="CorConcrete",
            ceiling_thickness=0.5,
            wall_mat_id="CorConcrete",
            wall_thickness=0.5,
            floor_mat_id="CorConcrete",
            floor_thickness=0.5,
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Compartment 2",
            depth=23.4,
            height=6.1,
            width=2,
            ceiling_mat_id="CorConcrete",
            ceiling_thickness=0.5,
            wall_mat_id="CorConcrete",
            wall_thickness=0.5,
            floor_mat_id="CorConcrete",
            floor_thickness=0.5,
            origin_x=8.1,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Compartment 3",
            depth=4.1,
            height=6.1,
            width=45.1,
            ceiling_mat_id="CorConcrete",
            ceiling_thickness=0.5,
            wall_mat_id="CorConcrete",
            wall_thickness=0.5,
            floor_mat_id="CorConcrete",
            floor_thickness=0.5,
            origin_x=10.1,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Compartment 4",
            depth=6,
            height=6.1,
            width=8.12,
            ceiling_mat_id="CorConcrete",
            ceiling_thickness=0.5,
            wall_mat_id="CorConcrete",
            wall_thickness=0.5,
            floor_mat_id="CorConcrete",
            floor_thickness=0.5,
            origin_x=20.7,
            origin_y=4.1,
            origin_z=0,
        ),
        Compartments(
            id="Compartment 5",
            depth=6.6,
            height=6.1,
            width=10.3,
            ceiling_mat_id="CorConcrete",
            ceiling_thickness=0.5,
            wall_mat_id="CorConcrete",
            wall_thickness=0.5,
            floor_mat_id="CorConcrete",
            floor_thickness=0.5,
            origin_x=20.7,
            origin_y=10.1,
            origin_z=0,
        ),
        Compartments(
            id="Compartment 6",
            depth=6.6,
            height=6.1,
            width=10.6,
            ceiling_mat_id="CorConcrete",
            ceiling_thickness=0.5,
            wall_mat_id="CorConcrete",
            wall_thickness=0.5,
            floor_mat_id="CorConcrete",
            floor_thickness=0.5,
            origin_x=20.7,
            origin_y=16.7,
            origin_z=0,
        ),
        Compartments(
            id="Compartment 7",
            depth=8.2,
            height=6.1,
            width=12.2,
            ceiling_mat_id="CorConcrete",
            ceiling_thickness=0.5,
            wall_mat_id="CorConcrete",
            wall_thickness=0.5,
            floor_mat_id="CorConcrete",
            floor_thickness=0.5,
            origin_x=55.2,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Compartment 8",
            depth=15.2,
            height=6.1,
            width=3,
            ceiling_mat_id="CorConcrete",
            ceiling_thickness=0.5,
            wall_mat_id="CorConcrete",
            wall_thickness=0.5,
            floor_mat_id="CorConcrete",
            floor_thickness=0.5,
            origin_x=64.4,
            origin_y=8.2,
            origin_z=0,
        ),
    ]

    wall_vents = [
        # Inter-compartment connections
        WallVents(
            id="WallVent_1",
            comps_ids=["Compartment 1", "Compartment 2"],
            bottom=0,
            height=6.1,
            width=4.1,
            face="RIGHT",
            offset=0,
        ),
        WallVents(
            id="WallVent_2",
            comps_ids=["Compartment 2", "Compartment 3"],
            bottom=0,
            height=4.5,
            width=4.6,
            face="RIGHT",
            offset=0,
        ),
        WallVents(
            id="WallVent_3",
            comps_ids=["Compartment 3", "Compartment 4"],
            bottom=0,
            height=6.1,
            width=8.12,
            face="REAR",
            offset=10.6,
        ),
        WallVents(
            id="WallVent_4",
            comps_ids=["Compartment 4", "Compartment 5"],
            bottom=0,
            height=6.1,
            width=8.12,
            face="REAR",
            offset=0,
        ),
        WallVents(
            id="WallVent_5",
            comps_ids=["Compartment 5", "Compartment 6"],
            bottom=0,
            height=2.4,
            width=1.6,
            face="REAR",
            offset=4.2,
        ),
        WallVents(
            id="WallVent_6",
            comps_ids=["Compartment 3", "Compartment 7"],
            bottom=0,
            height=6.1,
            width=4.1,
            face="RIGHT",
            offset=0,
        ),
        WallVents(
            id="WallVent_7",
            comps_ids=["Compartment 7", "Compartment 8"],
            bottom=0,
            height=6.1,
            width=3,
            face="REAR",
            offset=9.2,
        ),
        # External leakage vents
        WallVents(
            id="WallVent_8",
            comps_ids=["Compartment 1", "OUTSIDE"],
            bottom=0,
            height=0.0254,
            width=2,
            face="LEFT",
            offset=0,
        ),
        WallVents(
            id="WallVent_9",
            comps_ids=["Compartment 2", "OUTSIDE"],
            bottom=0,
            height=0.0254,
            width=1,
            face="REAR",
            offset=0,
        ),
        WallVents(
            id="WallVent_10",
            comps_ids=["Compartment 8", "OUTSIDE"],
            bottom=0,
            height=0.0254,
            width=2,
            face="REAR",
            offset=0,
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["OUTSIDE", "Compartment 1"],
            area=[1, 1],
            heights=[4.9, 4.9],
            flow=1.67,
            cutoffs=[200, 300],
            offsets=[7, 2.5],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_2",
            comps_ids=["Compartment 7", "OUTSIDE"],
            area=[1, 1],
            heights=[4.8, 4.8],
            flow=1.67,
            cutoffs=[200, 300],
            offsets=[2, 6.5],
            filter_time=0,
            filter_efficiency=0,
        ),
    ]

    fires = [
        Fires(
            id="Transient Combustibles",
            comp_id="Compartment 8",
            fire_id="Pallets",
            location=[2.43, 14.63],
            carbon=6,
            chlorine=0,
            hydrogen=10,
            nitrogen=0,
            oxygen=5,
            heat_of_combustion=17100,
            radiative_fraction=0.37,
            data_table=[
                [0, 0, 0.44, 1.3, 0.004, 0.015, 0, 0, 0],
                [42, 8.200001, 0.44, 1.3, 0.004, 0.015, 0, 0, 0],
                [84.00001, 100, 0.44, 1.3, 0.004, 0.015, 0, 0, 0],
                [126, 225, 0.44, 1.3, 0.004, 0.015, 0, 0, 0],
                [168, 400, 0.44, 1.3, 0.004, 0.015, 0, 0, 0],
                [210, 624.9999, 0.44, 1.3, 0.004, 0.015, 0, 0, 0],
                [252, 899.9999, 0.44, 1.3, 0.004, 0.015, 0, 0, 0],
                [294, 1225, 0.44, 1.3, 0.004, 0.015, 0, 0, 0],
                [336, 1600, 0.44, 1.3, 0.004, 0.015, 0, 0, 0],
                [378, 2025, 0.44, 1.3, 0.004, 0.015, 0, 0, 0],
                [420, 2500, 0.44, 1.3, 0.004, 0.015, 0, 0, 0],
                [840, 2500, 0.44, 1.3, 0.004, 0.015, 0, 0, 0],
                [1330, 0, 0.44, 1.3, 0.004, 0.015, 0, 0, 0],
            ],
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1",
            comp_id="Compartment 2",
            location=[1, 0.45, 4.8],
            type="PLATE",
            material_id="CorXPE",
            surface_orientation="CEILING",
            temperature_depth=0.0015,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2",
            comp_id="Compartment 6",
            location=[5.2, 4.15, 4.8],
            type="PLATE",
            material_id="CorXPE",
            surface_orientation="CEILING",
            temperature_depth=0.0015,
            depth_units="M",
        ),
        Devices.create_heat_detector(
            id="HeatDetector_1",
            comp_id="Compartment 1",
            location=[1.5, 1.6, 6.039],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_2",
            comp_id="Compartment 3",
            location=[2.6, 2.05, 6.039],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_3",
            comp_id="Compartment 3",
            location=[11.9, 2.05, 6.039],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_4",
            comp_id="Compartment 3",
            location=[39.9, 2.05, 6.039],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_5",
            comp_id="Compartment 5",
            location=[5.15, 3.3, 6.039],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_6",
            comp_id="Compartment 6",
            location=[5.3, 3.3, 6.039],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_7",
            comp_id="Compartment 7",
            location=[6.1, 4.1, 6.039],
            setpoint=30,
            rti=5,
        ),
        Devices.create_heat_detector(
            id="HeatDetector_8",
            comp_id="Compartment 8",
            location=[1.5, 10.2, 6.039],
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
