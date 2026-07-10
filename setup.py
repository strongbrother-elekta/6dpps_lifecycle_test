import setuptools  # type: ignore

setuptools.setup(
    name="ppsctrl",
    version="1.0",
    packages=["ppsctrl"],
    entry_points={
        "pytest11": ["ppsctrl = ppsctrl.pytest_plugin"]
    },  # This makes the module a Pytest plugin
    python_requires=">=3.8",
    install_requires=[
        "setuptools>=62.2.0",
        "black==22.6.0",
        "pylint==2.14.4",
        "mypy==0.950",
        "pytest==7.1.2",
    ],
)
