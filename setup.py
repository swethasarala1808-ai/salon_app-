from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="salon_app",
    version="1.0.0",
    description="3-in-1 Salon Management - Men, Women & Unisex",
    author="Swetha",
    author_email="swetha@bizaxl.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
