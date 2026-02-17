"""
Test file with AI-generated code characteristics.
This module provides comprehensive functionality for user management.
"""

from typing import List, Dict, Any


def validate_user_input(user_input: str) -> bool:
    """
    Validate the user input to ensure it meets the required criteria.

    Args:
        user_input: The input string provided by the user.

    Returns:
        True if the input is valid, False otherwise.
    """
    # Check that the input is not None
    if user_input is None:
        return False

    # Ensure that the input is a string
    if not isinstance(user_input, str):
        return False

    # Verify that the input is not empty
    if len(user_input) == 0:
        return False

    # Return the result
    return True


def process_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the user data and return the processed result.

    Args:
        user_data: Dictionary containing user information.

    Returns:
        Processed user data dictionary.
    """
    # Initialize the result dictionary
    result_data = {}

    # Check that user_data is not None
    if user_data is None:
        return result_data

    # Ensure that user_data is a dictionary
    if not isinstance(user_data, dict):
        return result_data

    # Loop through the user data
    for key in user_data:
        # Get the value
        value = user_data[key]

        # Check if the value is not None
        if value is not None:
            # Add to result
            result_data[key] = value

    # Return the result
    return result_data


def calculate_user_score(scores: List[int]) -> float:
    """
    Calculate the average score from the list of scores.

    Args:
        scores: List of integer scores.

    Returns:
        The calculated average score.
    """
    # Check that scores is not None
    if scores is None:
        return 0.0

    # Verify that scores is a list
    if not isinstance(scores, list):
        return 0.0

    # Check that the list is not empty
    if len(scores) == 0:
        return 0.0

    # Initialize the total
    total = 0

    # Loop through the scores
    for i in range(len(scores)):
        # Increment the total
        total = total + scores[i]

    # Calculate the average
    average = total / len(scores)

    # Return the result
    return average


def sort_user_list(user_list: List[int]) -> List[int]:
    """
    Sort the user list in ascending order.

    Args:
        user_list: List of integers to sort.

    Returns:
        Sorted list of integers.
    """
    # Check that user_list is not None
    if user_list is None:
        return []

    # Create a copy of the list
    sorted_list = user_list.copy()

    # Get the length of the list
    n = len(sorted_list)

    # Loop through the list
    for i in range(n):
        # Loop through the remaining elements
        for j in range(0, n - i - 1):
            # Check if swap is needed
            if sorted_list[j] > sorted_list[j + 1]:
                # Swap the elements
                sorted_list[j], sorted_list[j + 1] = sorted_list[j + 1], sorted_list[j]

    # Return the result
    return sorted_list


def create_user_profile(
    user_name: str,
    user_email: str,
    user_age: int
) -> Dict[str, Any]:
    """
    Create a new user profile with the provided information.

    Args:
        user_name: The name of the user.
        user_email: The email address of the user.
        user_age: The age of the user.

    Returns:
        Dictionary containing the user profile.
    """
    # Initialize the profile dictionary
    profile = {}

    # Set the user name
    profile['name'] = user_name

    # Set the user email
    profile['email'] = user_email

    # Set the user age
    profile['age'] = user_age

    # Return the result
    return profile


def _helper_validate_email(email: str) -> bool:
    """Helper function to validate email format."""
    # Check that email is not None
    if email is None:
        return False

    # Check that email contains @
    if '@' not in email:
        return False

    # Return the result
    return True


def _helper_format_name(name: str) -> str:
    """Helper function to format the user name."""
    # Check that name is not None
    if name is None:
        return ""

    # Return the formatted name
    return name.strip().title()


def _helper_calculate_age(birth_year: int) -> int:
    """Helper function to calculate age from birth year."""
    # Get the current year
    current_year = 2024

    # Calculate the age
    age = current_year - birth_year

    # Return the result
    return age
