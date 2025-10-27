from setuptools import setup, find_packages

setup(
    name="CompBase",          
    version="0.1.4",            
    author="Young",
    author_email="yang13515360252@163.com",
    description="Base Class for Derived Researcher Class",
    long_description=open("README.md", encoding="utf-8").read(),  
    long_description_content_type="text/markdown",
    url="https://github.com/ElenYoung/CompBase",
    package_dir={'': 'src'}, 
    packages=find_packages(where='src'),   
    install_requires=[   
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',  
)