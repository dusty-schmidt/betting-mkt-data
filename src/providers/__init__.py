# src/providers/__init__.py
"""Provider package initialization.

This module automatically discovers and registers all provider implementations
by scanning the providers directory for modules containing BaseProvider subclasses.
"""

import importlib
import pkgutil
import inspect
from pathlib import Path
from .base import BaseProvider

def get_all_providers() -> list[BaseProvider]:
    """Automatically discover and return all provider instances.
    
    Scans the providers directory for modules containing classes that inherit
    from BaseProvider and instantiates them.
    """
    providers = []
    providers_dir = Path(__file__).parent
    
    # Iterate through all modules in the providers directory
    for importer, modname, ispkg in pkgutil.iter_modules([str(providers_dir)]):
        # Skip base module and __pycache__
        if modname in ('base', '__pycache__'):
            continue
            
        try:
            # Import the module
            module = importlib.import_module(f'.{modname}', package='src.providers')
            
            # Find all classes in the module that inherit from BaseProvider
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if it's a BaseProvider subclass (but not BaseProvider itself)
                if issubclass(obj, BaseProvider) and obj is not BaseProvider:
                    # Instantiate and add to providers list
                    providers.append(obj())
                    break  # Only take the first provider class from each module
        except Exception as e:
            # Log but don't crash if a provider fails to load
            import logging
            logging.warning(f"Failed to load provider from {modname}: {e}")
            continue
    
    return providers
