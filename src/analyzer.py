from pathlib import Path

import pandas
import polars

from logger import logger
from src.input_reader import read_input_files
from src.models.Action import Action
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
        if isinstance(dataframe[requirement.column].dtype, polars.datatypes.List):
            return dataframe[requirement.column].list.contains(requirement.value)
        elif isinstance(dataframe[requirement.column].dtype, polars.datatypes.String):
            return dataframe[requirement.column].str.contains(requirement.value)
        else:
            raise ValueError(f"Column {requirement.column} is not of type List or String. Cannot apply INCLUDES operation.")
    elif requirement.operation == KPIOperation.NOT_INCLUDES:
        if isinstance(dataframe[requirement.column].dtype, polars.datatypes.List):
            return ~dataframe[requirement.column].list.contains(requirement.value)
        elif isinstance(dataframe[requirement.column].dtype, polars.datatypes.String):
            return ~dataframe[requirement.column].str.contains(requirement.value)
        else:
            raise ValueError(f"Column {requirement.column} is not of type List or String. Cannot apply NOT_INCLUDES operation.")
    return None


def apply_requirement(dataframe: polars.DataFrame, requirement: KPIRequirement) -> polars.DataFrame:
    requirement_condition = get_requirement_condition(dataframe=dataframe, requirement=requirement)
    return dataframe.filter(requirement_condition)


def get_chart_data(file: Path = None) -> (pandas.DataFrame, pandas.DataFrame | None):
    if file is not None:
        dataframe = polars.read_parquet(file)
        if dataframe is None:
            raise Exception(f"File {file} is empty or invalid.")
    else:
        dataframe = read_input_files()
        if dataframe is None:
            raise Exception("No valid files found in the input folder.")

    base_dataframe = dataframe.clone()

    general_bar_chart = {}
    bet_line_chart = {}
    actions = dataframe["action"].unique().to_list()
    bet_actions = list(filter(
        lambda x: x in actions,
        [Action.BET.value] + [Action(f"bet{i}").value for i in range(1, 101)],
    ))
    total_weight = dataframe["weight"].sum()
    for kpi in SETTINGS.KPIS:
        logger.info(f"Processing KPI: {kpi.display_name}")
        start_dataframe = dataframe.clone()

        for requirement in kpi.requirements:
            logger.info(f"Processing requirement: {requirement} on {dataframe.shape[0]} rows")
            dataframe = apply_requirement(dataframe=dataframe, requirement=requirement)
            logger.info(f"Rows that match requirement: {dataframe.shape[0]}")

        if dataframe.shape[0] == 0:
            logger.warning("No rows match the KPI requirements.")
            general_bar_chart[kpi.display_name] = {action: 0 for action in actions}
            bet_line_chart[kpi.display_name] = {action: 0 for action in bet_actions}
            dataframe = start_dataframe
            continue

        weight_by_action = {}
        for action in actions:
            weight_by_action[action] = dataframe.filter(dataframe["action"] == action)["weight"].sum()

        general_bar_chart[kpi.display_name] = {}
        bet_line_chart[kpi.display_name] = {}
        for action, weight in weight_by_action.items():
            percentage = (weight / total_weight) * 100
            general_bar_chart[kpi.display_name][action] = percentage
            logger.info(f"Percentage of {action}: {percentage:.2f}%")

            if action in bet_actions:
                bet_line_chart[kpi.display_name][action] = percentage

        total_percentage = sum(general_bar_chart[kpi.display_name].values())
        for action in actions:
            general_bar_chart[kpi.display_name][action] /= total_percentage

        bet_total_percentage = sum(bet_line_chart[kpi.display_name].values())
        for action in bet_actions:
            bet_line_chart[kpi.display_name][action] /= bet_total_percentage

        general_bar_chart[f"{kpi.display_name}\n{total_percentage:.2f}%"] = general_bar_chart[kpi.display_name]
        del general_bar_chart[kpi.display_name]

        bet_line_chart[f"{kpi.display_name}\n{bet_total_percentage:.2f}%"] = bet_line_chart[kpi.display_name]
        del bet_line_chart[kpi.display_name]

        dataframe = base_dataframe.join(dataframe, on=base_dataframe.columns, how="anti")

    return (
        polars.DataFrame(general_bar_chart).to_pandas(),
        polars.DataFrame(bet_line_chart).to_pandas() if bet_line_chart else None,
    )
