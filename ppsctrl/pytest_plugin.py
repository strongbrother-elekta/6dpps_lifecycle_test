"""Pytest plugin config file.

Here we can add custom command line options and other things that should be globally available.
For this to work, the setup.py file must contain the following argument to `setuptools.setup`:

`entry_points={"pytest11": ["<plugin-name> = <plugin-name>.pytest_plugin"]}`

where `plugin` means the file `plugin.py`.

For details, see Pytest documentation: https://docs.pytest.org/en/6.2.x/writing_plugins.html#writing-plugins
"""

DEFAULT_TARGET_HOST = "192.168.150.2"


# Add custom Pytest command line options
def pytest_addoption(parser):
    parser.addoption(
        "--target-host",
        action="store",
        default=DEFAULT_TARGET_HOST,
        help=f"Address of the target host. Default is {DEFAULT_TARGET_HOST}.",
    )
