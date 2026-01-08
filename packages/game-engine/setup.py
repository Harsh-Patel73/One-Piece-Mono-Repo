from setuptools import setup, find_packages

setup(
    name="optcg-engine",
    version="1.0.0",
    description="One Piece TCG Game Engine - Shared game logic for training and simulation",
    author="OPTCG Team",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "pydantic>=2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    package_data={
        "": ["*.json"],
    },
    include_package_data=True,
)
