from __future__ import annotations

from pathlib import Path

from pycfast import (
    CFASTModel,
    Compartments,
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
    Path(__file__).parent, "DOE_Guidance_Report"
)


def test_doe201_no_fire_simulation(tmp_path):
    """Test construction of CFASTModel for the DOE201.in file (no fire)."""
    prefix = "DOE201"

    simulation_env = SimulationEnvironment(
        title="DOE201, No Fire Simulation",
        time_simulation=2710,
        print=5,
        smokeview=5,
        spreadsheet=5,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
    )
    material_properties = [
        MaterialProperties(
            id="GYPS000",
            material="Gypsum for DOE sample problem",
            conductivity=0.2,
            density=700,
            specific_heat=1,
            thickness=0.016,
            emissivity=0.9,
        ),
        MaterialProperties(
            id="CONC003",
            material="Concrete for DOE sample problem",
            conductivity=1.75,
            density=2200,
            specific_heat=1,
            thickness=0.152,
            emissivity=0.94,
        ),
    ]
    compartments = [
        Compartments(
            id="Process Room",
            depth=3,
            height=2.6,
            width=3,
            ceiling_mat_id="GYPS000",
            ceiling_thickness=0.016,
            wall_mat_id="GYPS000",
            wall_thickness=0.016,
            floor_mat_id="CONC003",
            floor_thickness=0.152,
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
        Compartments(
            id="Airlock",
            depth=2,
            height=2.44,
            width=2,
            ceiling_mat_id="GYPS000",
            ceiling_thickness=0.016,
            wall_mat_id="GYPS000",
            wall_thickness=0.016,
            floor_mat_id="CONC003",
            floor_thickness=0.152,
            origin_x=3,
            origin_y=1,
            origin_z=0,
        ),
        Compartments(
            id="Corridor",
            depth=3,
            height=2.44,
            width=15,
            ceiling_mat_id="GYPS000",
            ceiling_thickness=0.016,
            wall_mat_id="GYPS000",
            wall_thickness=0.016,
            floor_mat_id="CONC003",
            floor_thickness=0.152,
            origin_x=0,
            origin_y=3,
            origin_z=0,
        ),
    ]
    wall_vents = [
        WallVents(
            id="WallVent_1",
            comps_ids=["Process Room", "Airlock"],
            bottom=0,
            height=0.0095,
            width=0.91,
            face="RIGHT",
            offset=1.2,
        ),
        WallVents(
            id="WallVent_2",
            comps_ids=["Process Room", "Airlock"],
            bottom=0,
            height=2.03,
            width=0.91,
            face="RIGHT",
            offset=1.2,
            open_close_criterion="TIME",
            time=[0, 0],
            fraction=[0, 0],
        ),
        WallVents(
            id="WallVent_3",
            comps_ids=["Process Room", "Corridor"],
            bottom=0.9,
            height=0.9,
            width=1.2,
            face="REAR",
            offset=0.5,
            open_close_criterion="TIME",
            time=[0, 0],
            fraction=[0, 0],
        ),
        WallVents(
            id="WallVent_4",
            comps_ids=["Process Room", "Corridor"],
            bottom=2.3,
            height=0.1,
            width=0.08,
            face="REAR",
            offset=1,
        ),
        WallVents(
            id="WallVent_5",
            comps_ids=["Airlock", "Corridor"],
            bottom=0,
            height=0.0095,
            width=0.91,
            face="REAR",
            offset=0.2,
        ),
        WallVents(
            id="WallVent_6",
            comps_ids=["Airlock", "Corridor"],
            bottom=0,
            height=2.03,
            width=0.91,
            face="REAR",
            offset=0.2,
            open_close_criterion="TIME",
            time=[0, 0],
            fraction=[0, 0],
        ),
        WallVents(
            id="WallVent_7",
            comps_ids=["Corridor", "OUTSIDE"],
            bottom=0,
            height=0.0095,
            width=0.91,
            face="REAR",
            offset=13.5,
        ),
        WallVents(
            id="WallVent_8",
            comps_ids=["Corridor", "OUTSIDE"],
            bottom=0,
            height=2.03,
            width=0.91,
            face="REAR",
            offset=13.5,
            open_close_criterion="TIME",
            time=[0, 0],
            fraction=[0, 0],
        ),
    ]
    mechanical_vents = [
        MechanicalVents(
            id="MechanicalVent_1",
            comps_ids=["Process Room", "OUTSIDE"],
            area=[0.05, 0.05],
            heights=[1, 10],
            flow=0.038,
            offsets=[0, 1.5],
            filter_time=0,
            filter_efficiency=99.97,
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
        mechanical_vents=mechanical_vents,
        fires=[],
        cfast_exe=cfast_exe,
        extra_arguments=extra_arguments,
        file_name=str(file_name),
    )

    results = model.run()
    assert isinstance(results, dict)

    compare_model_to_verification_data(
        results, verification_data_dir, prefix=prefix, tmp_path=tmp_path
    )
