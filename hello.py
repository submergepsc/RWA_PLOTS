#!/usr/bin/env python3
"""
Simple greeting module for RWAExpResults repository.
"""


def greet(name=None):
    """
    Greet a user with a friendly hello message.
    
    Args:
        name (str, optional): Name of the person to greet. Defaults to None.
    
    Returns:
        str: A greeting message
    """
    if name is not None:
        return f"Hello, {name}!"
    return "Hello!"


def main():
    """Main function to demonstrate the greeting."""
    print(greet())
    print(greet("World"))
    print(greet("RWAExpResults User"))


if __name__ == "__main__":
    main()
