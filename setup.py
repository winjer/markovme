from setuptools import setup, find_packages
import os

version = '0.0.dev0'

setup(name='MarkovMe',
      version=version,
      license="Apache Software License",
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points = """
      [console_scripts]
      markovme = markovme.main:main
      """
      )
