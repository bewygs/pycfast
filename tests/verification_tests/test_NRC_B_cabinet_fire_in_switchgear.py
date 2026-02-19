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
    "NRC_Users_Guide" + os.sep + "B_Cabinet_Fire_in_Switchgear",
)


def test_cabinet_fire_in_switchgear_simulation(tmp_path):
    """Test construction of CFASTModel for the Cabinet_fire_in_switchgear.in file."""
    prefix = "Cabinet_fire_in_switchgear"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
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
            id="CABSWConcrete",
            material="Cabinet Switchgear Concrete Floor (user''s guide)",
            conductivity=1.6,
            density=2400,
            specific_heat=0.75,
            thickness=0.5,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="CABSWSteel",
            material="Cabinet Switchgear Steel Cabinet (user''s guide)",
            conductivity=48,
            density=7854,
            specific_heat=0.559,
            thickness=0.0015,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="THIEF",
            material="Thief Cable (per NUREG CR 6931)",
            conductivity=0.2,
            density=2150,
            specific_heat=1.5,
            thickness=0.015,
            emissivity=0.8,
        ),
    ]

    compartments = [
        Compartments(
            id="Switchgear Room",
            depth=18.5,
            height=6.1,
            width=26.5,
            ceiling_mat_id="CABSWConcrete",
            ceiling_thickness=0.5,
            wall_mat_id="CABSWConcrete",
            wall_thickness=0.5,
            floor_mat_id="CABSWConcrete",
            floor_thickness=0.5,
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["Switchgear Room", "OUTSIDE"],
            bottom=0,
            height=0.013,
            width=1.0922,
            face="LEFT",
            offset=15.0114,
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["OUTSIDE", "Switchgear Room"],
            area=[0.3, 0.3],
            heights=[5.6, 5.6],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.472,
            cutoffs=[200, 300],
            offsets=[2.5, 6],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_2",
            comps_ids=["OUTSIDE", "Switchgear Room"],
            area=[0.3, 0.3],
            heights=[5.6, 5.6],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.472,
            cutoffs=[200, 300],
            offsets=[2.5, 9],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_3",
            comps_ids=["OUTSIDE", "Switchgear Room"],
            area=[0.3, 0.3],
            heights=[5.6, 5.6],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.472,
            cutoffs=[200, 300],
            offsets=[2.5, 12],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_4",
            comps_ids=["Switchgear Room", "OUTSIDE"],
            area=[0.3, 0.3],
            heights=[5.6, 5.6],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.472,
            cutoffs=[200, 300],
            offsets=[24, 6],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_5",
            comps_ids=["Switchgear Room", "OUTSIDE"],
            area=[0.3, 0.3],
            heights=[5.6, 5.6],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.472,
            cutoffs=[200, 300],
            offsets=[24, 9],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_6",
            comps_ids=["Switchgear Room", "OUTSIDE"],
            area=[0.3, 0.3],
            heights=[5.6, 5.6],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.472,
            cutoffs=[200, 300],
            offsets=[24, 12],
            filter_time=0,
            filter_efficiency=0,
        ),
    ]

    fires = [
        Fires(
            id="PE_PVC 464 kW",
            comp_id="Switchgear Room",
            fire_id="PE_PVC 464 kW_Fire",
            location=[8.3, 9.5],
            carbon=2,
            chlorine=0.5,
            hydrogen=3.5,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=20900,
            radiative_fraction=0.49,
            data_table=[
                [0, 0, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
                [72, 4.64, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
                [144, 18.56, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
                [216, 41.76, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
                [288, 74.24001, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
                [360, 116, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
                [432, 167.04, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
                [504, 227.36, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
                [576, 296.96, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
                [648, 375.84, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
                [720, 464, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
                [1200, 464, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
                [1920, 0, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
                [1930, 0, 2.4, 0.18, 0.147, 0.136, 0, 0.4026547, 0],
            ],
        ),
        Fires(
            id="MCC Cable Tray Secondary Fire",
            comp_id="Switchgear Room",
            fire_id="MCC Cable Tray Secondary Fire_Fire",
            location=[8.3, 9.5],
            ignition_criterion="TIME",
            set_point=480,
            carbon=2,
            chlorine=0.5,
            hydrogen=3.5,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=20900,
            radiative_fraction=0.49,
            data_table=[
                [0, 0, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [150, 147, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [300, 326, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [450, 657, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [600, 1106, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [750, 1142, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [900, 1187, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [1050, 1049, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [1200, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [1350, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [1500, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [1650, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [1800, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [1950, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [2100, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [2250, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [2400, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [2550, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [2700, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [2850, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [3000, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [3150, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [3300, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [3450, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
                [3600, 678, 3.8, 1, 0.147, 0.136, 0, 0.4026547, 0],
            ],
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1",
            comp_id="Switchgear Room",
            location=[8.3, 7, 2.4],
            type="PLATE",
            material_id="CABSWSteel",
            surface_orientation="RIGHT WALL",
            temperature_depth=0.00075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2",
            comp_id="Switchgear Room",
            location=[8.3, 12, 2.4],
            type="PLATE",
            material_id="CABSWSteel",
            surface_orientation="LEFT WALL",
            temperature_depth=0.00075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 3",
            comp_id="Switchgear Room",
            location=[8.3, 9.5, 3.9],
            type="CYLINDER",
            material_id="THIEF",
            surface_orientation="FLOOR",
            temperature_depth=0.003,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 4",
            comp_id="Switchgear Room",
            location=[8.3, 9.5, 4.4],
            type="CYLINDER",
            material_id="THIEF",
            surface_orientation="FLOOR",
            temperature_depth=0.003,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 5",
            comp_id="Switchgear Room",
            location=[8.3, 9.5, 4.9],
            type="CYLINDER",
            material_id="THIEF",
            surface_orientation="FLOOR",
            temperature_depth=0.003,
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


def test_initial_fire_only_simulation(tmp_path):
    """Test construction of CFASTModel for the Initial_fire_only.in file."""
    prefix = "Initial_fire_only"

    simulation_env = SimulationEnvironment(
        title="CFAST Simulation",
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
            id="CABSWConcrete",
            material="Cabinet Switchgear Concrete Floor (user''s guide)",
            conductivity=1.6,
            density=2400,
            specific_heat=0.75,
            thickness=0.5,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="CABSWSteel",
            material="Cabinet Switchgear Steel Cabinet (user''s guide)",
            conductivity=48,
            density=7854,
            specific_heat=0.559,
            thickness=0.0015,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="THIEF",
            material="Thief Cable (per NUREG CR 6931)",
            conductivity=0.2,
            density=2150,
            specific_heat=1.5,
            thickness=0.015,
            emissivity=0.8,
        ),
    ]

    compartments = [
        Compartments(
            id="Switchgear Room",
            depth=18.5,
            height=6.1,
            width=26.5,
            ceiling_mat_id="CABSWConcrete",
            ceiling_thickness=0.5,
            wall_mat_id="CABSWConcrete",
            wall_thickness=0.5,
            floor_mat_id="CABSWConcrete",
            floor_thickness=0.5,
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["Switchgear Room", "OUTSIDE"],
            bottom=0,
            height=0.013,
            width=1.0922,
            face="LEFT",
            offset=15.0114,
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["OUTSIDE", "Switchgear Room"],
            area=[0.3, 0.3],
            heights=[5.6, 5.6],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.472,
            cutoffs=[200, 300],
            offsets=[0, 9.25],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_2",
            comps_ids=["OUTSIDE", "Switchgear Room"],
            area=[0.3, 0.3],
            heights=[5.6, 5.6],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.472,
            cutoffs=[200, 300],
            offsets=[0, 9.25],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_3",
            comps_ids=["OUTSIDE", "Switchgear Room"],
            area=[0.3, 0.3],
            heights=[5.6, 5.6],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.472,
            cutoffs=[200, 300],
            offsets=[0, 9.25],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_4",
            comps_ids=["Switchgear Room", "OUTSIDE"],
            area=[0.3, 0.3],
            heights=[5.6, 5.6],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.472,
            cutoffs=[200, 300],
            offsets=[0, 9.25],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_5",
            comps_ids=["Switchgear Room", "OUTSIDE"],
            area=[0.3, 0.3],
            heights=[5.6, 5.6],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.472,
            cutoffs=[200, 300],
            offsets=[0, 9.25],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_6",
            comps_ids=["Switchgear Room", "OUTSIDE"],
            area=[0.3, 0.3],
            heights=[5.6, 5.6],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=0.472,
            cutoffs=[200, 300],
            offsets=[0, 9.25],
            filter_time=0,
            filter_efficiency=0,
        ),
    ]

    fires = [
        Fires(
            id="PE_PVC 464 kW",
            comp_id="Switchgear Room",
            fire_id="PE_PVC 464 kW_Fire",
            location=[8.3, 9.5],
            carbon=1,
            chlorine=0,
            hydrogen=4,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=20900,
            radiative_fraction=0.49,
            data_table=[
                [0, 0, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
                [72, 4.64, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
                [144, 18.56, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
                [216, 41.76, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
                [288, 74.24001, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
                [360, 116, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
                [432, 167.04, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
                [504, 227.36, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
                [576, 296.96, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
                [648, 375.84, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
                [720, 464, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
                [1200, 464, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
                [1920, 0, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
                [1930, 0, 2.4, 0.18, 0.11, 0.11, 0, 0, 0],
            ],
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1",
            comp_id="Switchgear Room",
            location=[8.3, 7, 2.4],
            type="PLATE",
            material_id="CABSWSteel",
            surface_orientation="RIGHT WALL",
            temperature_depth=0.00075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2",
            comp_id="Switchgear Room",
            location=[8.3, 12, 2.4],
            type="PLATE",
            material_id="CABSWSteel",
            surface_orientation="LEFT WALL",
            temperature_depth=0.00075,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 3",
            comp_id="Switchgear Room",
            location=[8.3, 9.5, 3.9],
            type="CYLINDER",
            material_id="THIEF",
            surface_orientation="FLOOR",
            temperature_depth=0.003,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 4",
            comp_id="Switchgear Room",
            location=[8.3, 9.5, 4.4],
            type="CYLINDER",
            material_id="THIEF",
            surface_orientation="FLOOR",
            temperature_depth=0.003,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 5",
            comp_id="Switchgear Room",
            location=[8.3, 9.5, 4.9],
            type="CYLINDER",
            material_id="THIEF",
            surface_orientation="FLOOR",
            temperature_depth=0.003,
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
