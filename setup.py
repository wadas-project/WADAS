# This file is part of WADAS project.
#
# WADAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WADAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WADAS. If not, see <https://www.gnu.org/licenses/>.
#
# Author(s): Stefano Dell'Osa, Alessandro Palla, Cesare Di Mauro, Antonio Farina
# Date: 2024-08-14
# Description: Setup module


from setuptools import find_packages, setup

description = (
    "Wild Animals Detection and Alert System (WADAS) is a project for "
    "AI-based detection and alert of wildlife in dangerous areas."
)


setup(
    name="wadas",
    version="0.5.1",
    packages=find_packages(),
    package_data={"": ["*.ui", "*.png", "*.jpg"]},
    include_package_data=True,
    author="Stefano Dell'Osa, Alessandro Palla, Antonio Farina, Cesare Di Mauro",
    author_email="stefano.dellosa@gmail.com, alespalla.ap@gmail.com, hexfati@gmail.com, cesare.di.mauro@gmail.com",  # noqa
    description=description,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/stefanodellosa-personal/WADAS",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    keywords="wildlife detection alert system ai",
)
