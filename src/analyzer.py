from pathlib import Path

import polars

from logger import logger
from src.input_reader import read_input_files
from src.models.KPI import KPIRequirement, KPIOperation
from src.settings import SETTINGS


def get_requirement_condition(dataframe: polars.DataFrame, requirement: KPIRequirement):
    if requirement.operation == KPIOperation.EQUALS:
        return dataframe[requirement.column] == requirement.value
    elif requirement.operation == KPIOperation.NOT_EQUALS:
        return dataframe[requirement.column] != requirement.value
    elif requirement.operation == KPIOperation.GREATER_THAN:
        return dataframe[requirement.column] > requirement.value
    elif requirement.operation == KPIOperation.GREATER_THAN_OR_EQUALS:
        return dataframe[requirement.column] >= requirement.value
    elif requirement.operation == KPIOperation.LESS_THAN:
        return dataframe[requirement.column] < requirement.value
    elif requirement.operation == KPIOperation.LESS_THAN_OR_EQUALS:
        return dataframe[requirement.column] <= requirement.value
    elif requirement.operation == KPIOperation.INCLUDES:
        return dataframe[requirement.column].list.contains(requirement.value)
    elif requirement.operation == KPIOperation.NOT_INCLUDES:
        return ~dataframe[requirement.column].list.contains(requirement.value)


def apply_requirement(dataframe: polars.DataFrame, requirement: KPIRequirement) -> polars.DataFrame:
    requirement_condition = get_requirement_condition(dataframe=dataframe, requirement=requirement)
    return dataframe.filter(requirement_condition)


def get_chart_data(file: Path = None) -> polars.DataFrame:
    if file is not None:
        dataframe = polars.read_parquet(file)
        if dataframe is None:
            raise Exception(f"File {file} is empty or invalid.")
    else:
        dataframe = read_input_files()
        if dataframe is None:
            raise Exception("No valid files found in the input folder.")

    base_dataframe = dataframe.clone()

    kpi_results = {}
    actions = dataframe["action"].unique()
    total_weight = dataframe["weight"].sum()
    for kpi in SETTINGS.KPIS:
        logger.info(f"Processing KPI: {kpi.display_name}")

        for requirement in kpi.requirements:
            logger.info(f"Processing requirement: {requirement}")
            dataframe = apply_requirement(dataframe=dataframe, requirement=requirement)
            logger.info(f"Rows that match requirement: {dataframe.shape[0]}")

        if dataframe.shape[0] == 0:
            logger.warning("No rows match the KPI requirements.")
            kpi_results[kpi.display_name] = {action: 0 for action in actions}
            continue

        weight_by_action = {}
        for action in actions:
            weight_by_action[action] = dataframe.filter(dataframe["action"] == action)["weight"].sum()

        kpi_results[kpi.display_name] = {}
        for action, weight in weight_by_action.items():
            percentage = (weight / total_weight) * 100
            kpi_results[kpi.display_name][action] = percentage
            logger.info(f"Percentage of {action}: {percentage:.2f}%")

        total_percentage = sum(kpi_results[kpi.display_name].values())
        for action in actions:
            kpi_results[kpi.display_name][action] /= total_percentage

        kpi_results[f'{kpi.display_name}\n{total_percentage:.2f}%'] = kpi_results[kpi.display_name]
        del kpi_results[kpi.display_name]

        dataframe = base_dataframe.join(dataframe, on=base_dataframe.columns, how="anti")

    output = polars.DataFrame(kpi_results)
    return output.to_pandas()
