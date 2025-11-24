from fandango_dls.db.sqlite import connect_to_ddbb, close_connection_to_ddbb


def update_project(project_name, key, value):
    """Update or insert project information in the database"""
    connection = None
    try:
        connection = connect_to_ddbb()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO project_info VALUES (?, ?, ?)', (project_name, key, value))
        connection.commit()
        print(f'... project {project_name} updated: "{key}" = "{value}"')
    except Exception as e:
        print(f'... project could not be updated because of: {e}')
    finally:
        if connection:
            close_connection_to_ddbb(connection)


def get_project_info(project_name):
    """Get all project information from the database"""
    connection = None
    try:
        connection = connect_to_ddbb()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM project_info WHERE project_name = ?', (project_name,))
        project_info = cursor.fetchall()
        column_names = [columns[0] for columns in cursor.description]
        return column_names, project_info
    except Exception as e:
        print(f'... could not check projects because of: {e}')
    finally:
        if connection:
            close_connection_to_ddbb(connection)


def get_project_metadata(project_name):
    """Get metadata JSON for a project"""
    connection = None
    try:
        connection = connect_to_ddbb()
        cursor = connection.cursor()
        cursor.execute('SELECT value FROM project_info WHERE project_name = ? AND key = "metadata_json"', (project_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f'... could not retrieve metadata because of: {e}')
        return None
    finally:
        if connection:
            close_connection_to_ddbb(connection)


def get_project_data_location(project_name):
    """Get data location/retrieval info for a project"""
    connection = None
    try:
        connection = connect_to_ddbb()
        cursor = connection.cursor()
        cursor.execute('SELECT value FROM project_info WHERE project_name = ? AND key = "data_location"', (project_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f'... could not retrieve data location because of: {e}')
        return None
    finally:
        if connection:
            close_connection_to_ddbb(connection)
