import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="service_flow",
    version="0.0.2",
    author="Xiaosong Xu",
    author_email="jackxxu@gmail.com",
    description="service object flow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jackxxu/service_flow",
    project_urls={
        "Bug Tracker": "https://github.com/jackxxu/service_flow/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)