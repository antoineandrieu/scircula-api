import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scircula_api",
    version="0.3.0",
    author="Antoine Andrieu",
    author_email="antoine@scircula.com",
    description="SCIRCULA API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/scircula/scircula-api/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
