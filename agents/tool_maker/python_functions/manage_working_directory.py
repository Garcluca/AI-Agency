
import os

def manage_working_directory(action, file_name=None, file_content=None):
    """
    A function that can access the current working directory and manage files within it, such as creating and 
    reading files.

    Parameters:
    action (str): The action to perform ('list_directory', 'create_file', 'read_file', 'delete_file').
    file_name (str, optional): The name of the file for the action if applicable.
    file_content (str, optional): The content to write to the file if the action is create_file.
    
    Returns:
    List of directory contents for 'list_directory',
    Confirmation message for 'create_file' and 'delete_file',
    File content for 'read_file',
    Error message if the action fails.
    """
    
    # List contents of the current working directory
    if action == 'list_directory':
        try:
            return os.listdir('.')
        except Exception as e:
            return f"Error: {e}"

    # Create a file with the provided name and content
    elif action == 'create_file':
        if file_name is not None and file_content is not None:
            try:
                with open(file_name, 'w') as f:
                    f.write(file_content)
                return f"File '{file_name}' created successfully."
            except Exception as e:
                return f"Error: {e}"
        else:
            return "Error: file_name and file_content are required for creating a file."

    # Read the content of the file with the provided name
    elif action == 'read_file':
        if file_name is not None:
            try:
                with open(file_name, 'r') as f:
                    content = f.read()
                return content
            except Exception as e:
                return f"Error: {e}"
        else:
            return "Error: file_name is required for reading a file."

    # Delete the file with the provided name
    elif action == 'delete_file':
        if file_name is not None:
            try:
                os.remove(file_name)
                return f"File '{file_name}' deleted successfully."
            except Exception as e:
                return f"Error: {e}"
        else:
            return "Error: file_name is required for deleting a file."

    # Action is not recognized
    else:
        return "Error: invalid action."
