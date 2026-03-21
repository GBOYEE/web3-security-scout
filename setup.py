from setuptools import setup, find_packages

setup(
    name="web3-security-scout",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)