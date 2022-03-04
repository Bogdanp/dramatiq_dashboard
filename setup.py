import os

from setuptools import setup


def rel(*xs):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *xs)


with open(rel("README.md")) as f:
    long_description = f.read()


with open(rel("dramatiq_dashboard", "__init__.py"), "r") as f:
    version_marker = "__version__ = "
    for line in f:
        if line.startswith(version_marker):
            _, version = line.split(version_marker)
            version = version.strip().strip('"')
            break
    else:
        raise RuntimeError("Version marker not found.")


dependencies = [
    "dataclasses; python_version < '3.7'",
    "dramatiq[redis]>=1.6,<2.0",
    "jinja2>=2,<3",
    "redis>=2.0,<5.0",
]

extra_dependencies = {
}

extra_dependencies["all"] = list(set(sum(extra_dependencies.values(), [])))
extra_dependencies["dev"] = extra_dependencies["all"] + [
    # Docs
    "alabaster",
    "sphinx<1.8",
    "sphinxcontrib-napoleon",

    # Linting
    "flake8",
    "flake8-bugbear",
    "flake8-quotes",
    "isort",

    # Misc
    "bumpversion",
    "hiredis",
    "twine",
    "wheel",

    # Testing
    "pytest",
    "pytest-benchmark[histogram]",
    "pytest-cov",
    "tox",
]

setup(
    name="dramatiq_dashboard",
    version=version,
    author="Bogdan Popa",
    author_email="bogdan@cleartype.io",
    description="A dashboard for Dramatiq (Redis-only!).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[
        "dramatiq_dashboard"
    ],
    include_package_data=True,
    install_requires=dependencies,
    python_requires=">=3.6",
    extras_require=extra_dependencies,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: System :: Distributed Computing",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",  # FIXME
    ],
)
