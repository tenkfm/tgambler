from setuptools import setup, find_packages

setup(
    name="common",            # именно так, чтобы при импорте было `import common`
    version="0.1.1",
    packages=find_packages(),  # найдёт папку common/common
)
