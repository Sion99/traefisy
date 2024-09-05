from setuptools import setup, find_packages

setup(
    name="traefisy",
    version="0.1.1",
    description="A simple and efficient CLI tool for easy Traefik configuration.",
    author="sion",
    author_email="kmicety1@gmail.com",
    url="https://github.com/sion99/traefisy",
    packages=find_packages(),
    keywords=[
        "traefik",
        "traefik configuration"
    ],
    include_package_data=True,
    install_requires=[
        "typer[all]",
        "rich",
        "sqlalchemy",
        "pyyaml",
        "ruamel.yaml"
    ],
    entry_points={
        "console_scripts": [
            "traefisy=traefisy.main:app",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # 최소 지원하는 Python 버전
)