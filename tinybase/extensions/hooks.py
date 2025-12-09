"""
Extension lifecycle hooks.

Provides decorators and a registry for extension lifecycle events:
- on_startup: Called when TinyBase starts
- on_shutdown: Called when TinyBase shuts down
"""

from typing import Callable

# Global hook registries
_startup_hooks: list[Callable[[], None]] = []
_shutdown_hooks: list[Callable[[], None]] = []


def on_startup(func: Callable[[], None]) -> Callable[[], None]:
    """
    Decorator to register a function to run on TinyBase startup.
    
    The decorated function will be called after all extensions are loaded,
    before the server starts accepting requests.
    
    Example:
        from tinybase.extensions import on_startup
        
        @on_startup
        def initialize_my_extension():
            print("Extension initialized!")
    """
    _startup_hooks.append(func)
    return func


def on_shutdown(func: Callable[[], None]) -> Callable[[], None]:
    """
    Decorator to register a function to run on TinyBase shutdown.
    
    The decorated function will be called when the server is shutting down,
    before the process exits.
    
    Example:
        from tinybase.extensions import on_shutdown
        
        @on_shutdown
        def cleanup_my_extension():
            print("Extension shutting down!")
    """
    _shutdown_hooks.append(func)
    return func


async def run_startup_hooks() -> None:
    """Execute all registered startup hooks."""
    for hook in _startup_hooks:
        try:
            result = hook()
            # Handle async hooks
            if hasattr(result, "__await__"):
                await result
        except Exception as e:
            # Log but don't fail startup
            import logging
            logging.getLogger(__name__).error(f"Error in startup hook {hook.__name__}: {e}")


async def run_shutdown_hooks() -> None:
    """Execute all registered shutdown hooks."""
    for hook in _shutdown_hooks:
        try:
            result = hook()
            # Handle async hooks
            if hasattr(result, "__await__"):
                await result
        except Exception as e:
            # Log but don't fail shutdown
            import logging
            logging.getLogger(__name__).error(f"Error in shutdown hook {hook.__name__}: {e}")


def clear_hooks() -> None:
    """Clear all registered hooks. Used for testing."""
    global _startup_hooks, _shutdown_hooks
    _startup_hooks = []
    _shutdown_hooks = []

