import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='cycleslip',
     version='0.1',
     scripts=['cycle_slip'],
     author="EMBRACE/INPE",
     author_email="desenvolvimento.embrace@inpe.br",
     description="Analyse and correct cycle slips in rinex files",
     long_description_content_type="text/markdown",
     url="https://github.com/embrace-inpe/cycle-slip-correction",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )