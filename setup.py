from setuptools import setup, find_packages

setup(
    name="web3-security-scout",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "w3-scout=web3_security_scout.cli:main",
        ],
    },
    python_requires=">=3.8",
)