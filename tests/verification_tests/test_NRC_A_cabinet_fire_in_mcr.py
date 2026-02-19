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
    Path(__file__).parent, "NRC_Users_Guide" + os.sep + "A_Cabinet_Fire_in_MCR"
)


def test_cabinet_fire_in_mcr_simulation(tmp_path):
    """Test construction of CFASTModel for the Cabinet_fire_in_MCR.in file."""
    prefix = "Cabinet_fire_in_MCR"

    simulation_env = SimulationEnvironment(
        title="MCR with smoke purge",
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
            id="MCROperator",
            material="MCR Operator (properties of water at 20 C)",
            conductivity=0.58,
            density=998.3,
            specific_heat=4.183,
            thickness=0.2032,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="MCRConcrete",
            material="MCR Concrete Floor (user''s guide)",
            conductivity=1.6,
            density=2400,
            specific_heat=0.75,
            thickness=0.5,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="MCRConcreteW",
            material="MCR Concrete Wall (user''s guide)",
            conductivity=1.6,
            density=2400,
            specific_heat=0.75,
            thickness=0.9,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="MCRGypsum",
            material="MCR Gypsum Walls (user''s guide)",
            conductivity=0.17,
            density=960,
            specific_heat=1.1,
            thickness=0.015875,
            emissivity=0.9,
        ),
    ]

    compartments = [
        Compartments(
            id="MCR",
            depth=13.8,
            height=5.2,
            width=27.1,
            ceiling_mat_id="MCRConcreteW",
            ceiling_thickness=0.9,
            wall_mat_id="MCRGypsum",
            wall_thickness=0.015875,
            floor_mat_id="MCRConcrete",
            floor_thickness=0.5,
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["MCR", "OUTSIDE"],
            bottom=0,
            height=0.013,
            width=0.91,
            face="LEFT",
            offset=7,
        ),
    ]

    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["MCR", "OUTSIDE"],
            area=[0.36, 0.36],
            heights=[4.9, 4.9],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=6.711792,
            cutoffs=[200, 300],
            offsets=[3.65, 12.85],
            open_close_criterion="TIME",
            time=[120, 121],
            fraction=[0.2, 1],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_2",
            comps_ids=["MCR", "OUTSIDE"],
            area=[0.36, 0.36],
            heights=[4.9, 4.9],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=6.711792,
            cutoffs=[200, 300],
            offsets=[20.75, 12.85],
            open_close_criterion="TIME",
            time=[120, 121],
            fraction=[0.2, 1],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_3",
            comps_ids=["OUTSIDE", "MCR"],
            area=[0.36, 0.36],
            heights=[3, 3],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=2.237264,
            cutoffs=[200, 300],
            offsets=[3.65, 3.25],
            open_close_criterion="TIME",
            time=[120, 121],
            fraction=[0.2, 1],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_4",
            comps_ids=["OUTSIDE", "MCR"],
            area=[0.36, 0.36],
            heights=[3, 3],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=2.237264,
            cutoffs=[200, 300],
            offsets=[12.25, 3.25],
            open_close_criterion="TIME",
            time=[120, 121],
            fraction=[0.2, 1],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_5",
            comps_ids=["OUTSIDE", "MCR"],
            area=[0.36, 0.36],
            heights=[3, 3],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=2.237264,
            cutoffs=[200, 300],
            offsets=[20.75, 3.25],
            open_close_criterion="TIME",
            time=[120, 121],
            fraction=[0.2, 1],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_6",
            comps_ids=["OUTSIDE", "MCR"],
            area=[0.36, 0.36],
            heights=[3, 3],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=2.237264,
            cutoffs=[200, 300],
            offsets=[3.25, 8.85],
            open_close_criterion="TIME",
            time=[120, 121],
            fraction=[0.2, 1],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_7",
            comps_ids=["OUTSIDE", "MCR"],
            area=[0.36, 0.36],
            heights=[3, 3],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=2.237264,
            cutoffs=[200, 300],
            offsets=[12.25, 8.85],
            open_close_criterion="TIME",
            time=[120, 121],
            fraction=[0.2, 1],
            filter_time=0,
            filter_efficiency=0,
        ),
        MechanicalVents(
            id="MechanicalVent_8",
            comps_ids=["OUTSIDE", "MCR"],
            area=[0.36, 0.36],
            heights=[3, 3],
            orientations=["HORIZONTAL", "HORIZONTAL"],
            flow=2.237264,
            cutoffs=[200, 300],
            offsets=[20.75, 8.85],
            open_close_criterion="TIME",
            time=[120, 121],
            fraction=[0.2, 1],
            filter_time=0,
            filter_efficiency=0,
        ),
    ]

    fires = [
        Fires(
            id="XPE_Neoprene 702 kW",
            comp_id="MCR",
            fire_id="XPE_Neoprene 702 kW_Fire",
            location=[2, 4],
            carbon=3,
            chlorine=0.5,
            hydrogen=4.5,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=10300,
            radiative_fraction=0.53,
            data_table=[
                [0, 0, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [72, 7.02, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [144, 28.08, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [216, 63.18, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [288, 112.32, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [360, 175.5, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [432, 252.72, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [504, 343.98, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [576, 449.28, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [648, 568.62, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [720, 702, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [1200, 702, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [2340, 0, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [2350, 0, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
            ],
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1",
            comp_id="MCR",
            location=[11.2, 5.5, 1.524],
            type="PLATE",
            material_id="MCROperator",
            surface_orientation="CEILING",
            temperature_depth=0.1016,
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


def test_cabinet_fire_in_mcr_no_ventilation_simulation(tmp_path):
    """Test construction of CFASTModel for the Cabinet_fire_in_MCR_no_ventilation.in file."""
    prefix = "Cabinet_fire_in_MCR_no_ventilation"

    simulation_env = SimulationEnvironment(
        title="MCR with no ventilation",
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
            id="MCROperator",
            material="MCR Operator (properties of water at 20 C)",
            conductivity=0.58,
            density=998.3,
            specific_heat=4.183,
            thickness=0.2032,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="MCRConcrete",
            material="MCR Concrete Floor (user''s guide)",
            conductivity=1.6,
            density=2400,
            specific_heat=0.75,
            thickness=0.5,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="MCRConcreteW",
            material="MCR Concrete Wall (user''s guide)",
            conductivity=1.6,
            density=2400,
            specific_heat=0.75,
            thickness=0.9,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="MCRGypsum",
            material="MCR Gypsum Walls (user''s guide)",
            conductivity=0.17,
            density=960,
            specific_heat=1.1,
            thickness=0.015875,
            emissivity=0.9,
        ),
    ]

    compartments = [
        Compartments(
            id="MCR",
            depth=13.8,
            height=5.2,
            width=27.1,
            ceiling_mat_id="MCRConcreteW",
            ceiling_thickness=0.9,
            wall_mat_id="MCRGypsum",
            wall_thickness=0.015875,
            floor_mat_id="MCRConcrete",
            floor_thickness=0.5,
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["MCR", "OUTSIDE"],
            bottom=0,
            height=0.013,
            width=0.91,
            face="LEFT",
            offset=7,
        ),
    ]

    fires = [
        Fires(
            id="XPE_Neoprene 702 kW",
            comp_id="MCR",
            fire_id="XPE_Neoprene 702 kW_Fire",
            location=[2, 4],
            carbon=3,
            chlorine=0.5,
            hydrogen=4.5,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=10300,
            radiative_fraction=0.53,
            data_table=[
                [0, 0, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [72, 7.02, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [144, 28.08, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [216, 63.18, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [288, 112.32, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [360, 175.5, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [432, 252.72, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [504, 343.98, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [576, 449.28, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [648, 568.62, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [720, 702, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [1200, 702, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [2340, 0, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
                [2350, 0, 2, 0.12, 0.082, 0.175, 0, 0.3127314, 0],
            ],
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1",
            comp_id="MCR",
            location=[11.2, 5.5, 1.524],
            type="PLATE",
            material_id="MCROperator",
            surface_orientation="CEILING",
            temperature_depth=0.1016,
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
