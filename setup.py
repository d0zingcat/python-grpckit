import os


from setuptools import setup, find_packages


_root = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(_root, "requirements.txt")) as f:
    requirements = f.readlines()

with open(os.path.join(_root, "README.md")) as f:
    readme = f.read()


def find_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [
        (dirpath.replace(package + os.sep, "", 1), filenames)
        for dirpath, dirnames, filenames in os.walk(package)
    ]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename) for filename in filenames])
    return filepaths


setup(
    name="grpckit",
    version="0.1.3",
    description="python grpckit framework",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/d0zingcat/python-grpckit",
    author="d0zingcat",
    author_email="i@d0zingcat.dev",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["rpc", "grpc", "grpckit"],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    # package_data={'grpckit': find_package_data('grpckit')},
    python_requires=">=3",
    install_requires=requirements,
    entry_points={
        "console_scripts": ["grpckit=grpckit.cli:main"],
    },
)
