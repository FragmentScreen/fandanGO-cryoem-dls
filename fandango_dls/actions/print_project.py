"""
Print project action for DLS Cryo-EM plugin

Displays stored project information from the database
"""

from fandango_dls.db.sqlite_db import get_project_info
from tabulate import tabulate


def print_project(project_name):
    """
    Print information for a FandanGO project

    Args:
        project_name (str): Name of the project to display

    Returns:
        success (bool): Whether the operation succeeded
        info: Project information or error message
    """
    print('FandanGO project info:\n')
    success = False
    info = None

    try:
        column_names, project_info = get_project_info(project_name)
        print(tabulate(project_info, headers=column_names, tablefmt="pretty"))
        success = True
        info = project_info
    except Exception as e:
        info = f'Error retrieving project info: {e}'
        print(info)

    return success, info


def perform_action(args):
    """
    Entry point for the print-project action

    Args:
        args (dict): Dictionary containing:
            - name: Project name

    Returns:
        dict: Results dictionary with success status and info
    """
    success, info = print_project(args['name'])
    results = {'success': success, 'info': info}
    return results
