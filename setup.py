import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="critic-bench-example",
    version="0.1.3",
    author="gmftbyGMFTBY",
    author_email="lantiangmftby@gmail.com",
    description="The evaluation toolkit for CriticBench benchmark",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gmftbyGMFTBY/CriticBench",
    packages=setuptools.find_packages(),
)
