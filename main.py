"""
Password Tool - A simple CLI utility for generating and evaluating passwords.

This module provides two main functionalities:
1. Generating random passwords with configurable lengths.
2. Evaluating the strength of a password based on length and character variety.

Author: User
Date: 2026
"""

import random
import string
import datetime
from typing import Callable

# --- Allowed character sets ---
UPPER = string.ascii_uppercase
LOWER = string.ascii_lowercase
NUMBERS = '0123456789'
SPECIAL = '!@#$%^&*()_-*/+'
# Combined set used for password generation
ALL_CHARS = string.ascii_letters + NUMBERS + SPECIAL

SAVED_FILE = 'saved_password_list.txt'


def _has_all_categories(password: str) -> bool:
    """
    Check whether the password contains at least one character from each category.

    Args:
        password (str): The password to inspect.

    Returns:
        bool: True if the password has upper, lower, digit and special characters.
    """
    return (
        any(c in UPPER for c in password)
        and any(c in LOWER for c in password)
        and any(c in NUMBERS for c in password)
        and any(c in SPECIAL for c in password)
    )


def generate_password(length: int = 8) -> str:
    """
    Generate a random password with the given length and save it to the log file.

    The password is guaranteed to include at least one uppercase letter,
    one lowercase letter, one digit and one special character.

    Args:
        length (int): Desired password length (must be at least 8).

    Returns:
        str: The generated password.

    Raises:
        ValueError: If the requested length is smaller than 8.
    """
    if length < 8:
        raise ValueError('length must be at least 8')

    # Regenerate until every character category is present
    while True:
        password = ''.join(random.choice(ALL_CHARS) for _ in range(length))
        if _has_all_categories(password):
            break

    # --- Save the password to the log file ---
    with open(SAVED_FILE, 'a+', encoding='utf-8') as f:
        f.seek(0)
        lines = f.readlines()

        # Write a header the first time the file is created
        if not lines:
            f.write(f"{'No.':<6} | {'Password':<25} | {'Creation Time':<30}\n")
            f.write('-' * 70 + '\n')
            data_lines = []
        else:
            # First two lines are the header and the separator
            data_lines = lines[2:]

        next_index = len(data_lines) + 1
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"{next_index:<6} | {password:<25} | {timestamp:<30}\n")

    return password


def check_strength(password: str) -> tuple[str, int, list[str]]:
    """
    Evaluate the strength of a password based on length and character variety.

    The password is NOT stored anywhere. This function only inspects it in memory.

    Args:
        password (str): The password to evaluate.

    Returns:
        tuple[str, int, list[str]]:
            - level: human-readable strength label.
            - score: numeric score between 0 and 100.
            - feedback: list of suggestions to improve the password (may be empty).
    """
    score = 0
    feedback: list[str] = []

    # --- Length score ---
    if len(password) >= 8:
        score += 20
    else:
        feedback.append('Use at least 8 characters')
    if len(password) >= 12:
        score += 15
    if len(password) >= 16:
        score += 15

    # --- Character variety score ---
    if any(c in UPPER for c in password):
        score += 10
    else:
        feedback.append('Add uppercase letters')

    if any(c in LOWER for c in password):
        score += 10
    else:
        feedback.append('Add lowercase letters')

    if any(c in NUMBERS for c in password):
        score += 10
    else:
        feedback.append('Add digits')

    if any(c in SPECIAL for c in password):
        score += 10
    else:
        feedback.append('Add special characters')

    # --- Penalty for common patterns ---
    common_patterns = ['123', 'abc', 'qwerty', 'password', 'admin', '111']
    if any(p in password.lower() for p in common_patterns):
        score = max(0, score - 20)
        feedback.append('Contains a common pattern')

    # --- Clamp score to [0, 100] ---
    score = max(0, min(100, score))

    # --- Map score to a human-readable level ---
    if score >= 80:
        level = 'very strong'
    elif score >= 60:
        level = 'strong'
    elif score >= 40:
        level = 'medium'
    else:
        level = 'weak'

    return level, score, feedback


def engine(generate_func: Callable, strength_func: Callable) -> None:
    """
    Main program engine that provides an interactive command-line menu.

    Args:
        generate_func (Callable): Password generator (usually generate_password).
        strength_func (Callable): Password strength checker (usually check_strength).

    Returns:
        None

    Side Effects:
        - Reads input from the user and prints output to the console.
        - Handles invalid input gracefully without crashing.
    """
    while True:
        print('\n*** Password Tool ***')
        user_command = input('1# create password\n2# check password strength\n3# exit\n> ').strip()

        # --- Exit ---
        if user_command == '3':
            print('program closed.')
            break

        # --- Option 1: generate a password ---
        if user_command == '1':
            length = input('enter password length (min 8): ').strip()
            try:
                length_int = int(length)
            except ValueError:
                print('[!] must be a number')
                continue

            if length_int < 8:
                print('[!] must be at least 8')
                continue

            print('-' * 20)
            print(f'generated: {generate_func(length_int)}')
            print('-' * 20)

        # --- Option 2: check password strength ---
        elif user_command == '2':
            user_password = input('enter your password (min 4 chars): ').strip()
            if not user_password or len(user_password) < 4:
                print('[!] must be at least 4 characters')
                continue

            level, score, feedback = strength_func(user_password)
            print('-' * 20)
            print(f'level : {level}')
            print(f'score : {score}/100')
            if feedback:
                print('hints :')
                for hint in feedback:
                    print(f'  - {hint}')
            print('-' * 20)

        # --- Invalid option ---
        else:
            print('[!] invalid option, try again')


# --- Program entry point ---
if __name__ == '__main__':
    engine(generate_password, check_strength)