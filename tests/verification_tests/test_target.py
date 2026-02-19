from __future__ import annotations

from pathlib import Path

from pycfast import (
    CFASTModel,
    Compartments,
    Devices,
    Fires,
    MaterialProperties,
    SimulationEnvironment,
)

from .verification import (
    compare_model_to_verification_data,
    get_verification_data_dir,
)

verification_data_dir = get_verification_data_dir(Path(__file__).parent, "Target")


def test_target_1_simulation(tmp_path):
    """Test construction of CFASTModel for the target_1.in file."""
    prefix = "target_1"

    simulation_env = SimulationEnvironment(
        title="ADIABATIC_TARGET_SURFACE_TEMPERATURE_VERIFICIATION_CASE",
        time_simulation=20,
        print=1,
        smokeview=1,
        spreadsheet=1,
        init_pressure=101325,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
        extra_custom=(
            "&DIAG ADIABATIC_TARGET_VERIFICATION = 'ON' RADIATIVE_INCIDENT_FLUX = 1/"
        ),
    )

    material_properties = [
        MaterialProperties(
            id="ConcreteBE2",
            material="Concrete ICFMP BE2",
            conductivity=2,
            density=2300,
            specific_heat=0.9,
            thickness=0.15,
            emissivity=0.95,
        ),
        MaterialProperties(
            id="TC",
            material="Thermocouple (small steel target for plume temp)",
            conductivity=54,
            density=7850,
            specific_heat=0.425,
            thickness=0.001,
            emissivity=0.95,
        ),
    ]

    compartments = [
        Compartments(
            id="Compartment 1",
            depth=10,
            height=10,
            width=10,
            ceiling_mat_id="ConcreteBE2",
            ceiling_thickness=0.15,
            wall_mat_id="ConcreteBE2",
            wall_thickness=0.15,
            floor_mat_id="ConcreteBE2",
            floor_thickness=0.15,
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1",
            comp_id="Compartment 1",
            location=[5, 5, 5],
            type="PLATE",
            material_id="TC",
            surface_orientation="FLOOR",
            temperature_depth=0.0005,
            depth_units="M",
            adiabatic=True,
            convection_coefficients=[0.003, 0.005],
        ),
    ]

    # No fires in target_1
    fires = []

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


def test_target_2_simulation(tmp_path):
    """Test construction of CFASTModel for the target_2.in file."""
    prefix = "target_2"

    simulation_env = SimulationEnvironment(
        title="Fire to target radiation",
        time_simulation=1,
        print=1,
        smokeview=1,
        spreadsheet=1,
        init_pressure=101300,
        relative_humidity=50,
        interior_temperature=20,
        exterior_temperature=20,
        extra_custom=(
            "&DIAG VERIFICATION_FIRE_HEAT_FLUX = 50 GAS_TEMPERATURE = 20 "
            "PARTIAL_PRESSURE_H2O = 0 PARTIAL_PRESSURE_CO2 = 0/"
        ),
    )

    material_properties = [
        MaterialProperties(
            id="Concrete",
            material="Concrete",
            conductivity=1.6,
            density=2400,
            specific_heat=0.75,
            thickness=0.6,
            emissivity=1,
        ),
    ]

    compartments = [
        Compartments(
            id="Comp_1",
            depth=6,
            height=8,
            width=6,
            ceiling_mat_id="Concrete",
            ceiling_thickness=0.6,
            wall_mat_id="Concrete",
            wall_thickness=0.6,
            floor_mat_id="Concrete",
            floor_thickness=0.6,
            origin_x=0,
            origin_y=0,
            origin_z=0,
        ),
    ]

    fires = [
        Fires(
            id="MCC 702 kW",
            comp_id="Comp_1",
            fire_id="MCC 702 kW_Fire",
            location=[3, 3],
            carbon=3,
            chlorine=0.5,
            hydrogen=4.5,
            nitrogen=0,
            oxygen=0,
            heat_of_combustion=10300,
            radiative_fraction=0.5,
            data_table=[
                [0, 100, 4, 2, 0.082, 0.175, 0, 0.3127314, 0],
                [1, 100, 4, 2, 0.082, 0.175, 0, 0.3127314, 0],
            ],
        ),
    ]

    devices = [
        Devices.create_target(
            id="Targ 1",
            comp_id="Comp_1",
            location=[3, 3, 8],
            type="PLATE",
            material_id="Concrete",
            surface_orientation="FLOOR",
            temperature_depth=0.3,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 2",
            comp_id="Comp_1",
            location=[3, 3, 6],
            type="PLATE",
            material_id="Concrete",
            surface_orientation="FLOOR",
            temperature_depth=0.3,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 3",
            comp_id="Comp_1",
            location=[3, 3, 5],
            type="PLATE",
            material_id="Concrete",
            surface_orientation="FLOOR",
            temperature_depth=0.3,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 4",
            comp_id="Comp_1",
            location=[3, 3, 4.5],
            type="PLATE",
            material_id="Concrete",
            surface_orientation="FLOOR",
            temperature_depth=0.3,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 5",
            comp_id="Comp_1",
            location=[3, 3, 4.4],
            type="PLATE",
            material_id="Concrete",
            surface_orientation="FLOOR",
            temperature_depth=0.3,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 6",
            comp_id="Comp_1",
            location=[3, 3, 4.3],
            type="PLATE",
            material_id="Concrete",
            surface_orientation="FLOOR",
            temperature_depth=0.3,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 7",
            comp_id="Comp_1",
            location=[3, 3, 4.2],
            type="PLATE",
            material_id="Concrete",
            surface_orientation="FLOOR",
            temperature_depth=0.3,
            depth_units="M",
        ),
        Devices.create_target(
            id="Targ 8",
            comp_id="Comp_1",
            location=[3, 3, 4.1],
            type="PLATE",
            material_id="Concrete",
            surface_orientation="FLOOR",
            temperature_depth=0.3,
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
