import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sofahutils",
    version="0.2",
    description="Utilities such as dataclasses, logger, exceptions and shared helpers for sofah",
    long_description=long_description,
    install_requires=[
        'requests'
    ],
    long_description_content_type="text/markdown",
    url="https://github.com/sofahd/sofahutils",
    packages=["sofahutils"])
