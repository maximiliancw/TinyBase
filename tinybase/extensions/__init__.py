"""
TinyBase Extension System.

Provides functionality for installing and managing extensions from GitHub repositories.
Extensions can register functions, add lifecycle hooks, and integrate third-party services.

Usage for extension developers:

    from tinybase.functions import Context, register
    from tinybase.extensions import on_startup, on_shutdown
    
    @on_startup
    def initialize():
        print("Extension loaded!")
    
    @on_shutdown
    def cleanup():
        print("Extension unloading!")
    
    @register(name="my_function", description="My extension function", auth="auth")
    def my_function(ctx: Context, payload: MyInput) -> MyOutput:
        return MyOutput(...)
"""

from tinybase.extensions.hooks import (
    on_startup,
    on_shutdown,
    run_startup_hooks,
    run_shutdown_hooks,
    clear_hooks,
)
from tinybase.extensions.loader import (
    load_enabled_extensions,
    load_extension_module,
    unload_extension,
    get_extensions_directory,
)
from tinybase.extensions.installer import (
    install_extension,
    uninstall_extension,
    check_for_updates,
    validate_manifest,
    parse_github_url,
    InstallError,
    ExtensionManifest,
)

__all__ = [
    # Hooks (for extension developers)
    "on_startup",
    "on_shutdown",
    # Hook runners (for internal use)
    "run_startup_hooks",
    "run_shutdown_hooks",
    "clear_hooks",
    # Loader
    "load_enabled_extensions",
    "load_extension_module",
    "unload_extension",
    "get_extensions_directory",
    # Installer
    "install_extension",
    "uninstall_extension",
    "check_for_updates",
    "validate_manifest",
    "parse_github_url",
    "InstallError",
    "ExtensionManifest",
]

