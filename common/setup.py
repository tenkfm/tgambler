from setuptools import setup, find_packages

setup(
    name="common",            # именно так, чтобы при импорте было `import common`
    version="0.1.3",
    packages=find_packages(),  # найдёт папку common/common
    install_requires=[         # List of dependencies
        'firebase-admin',      # Add firebase-admin as a required dependency
    ],
)
