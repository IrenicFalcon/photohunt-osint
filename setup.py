from setuptools import setup, find_packages

setup(
    name="photohunt-osint",  
    version="1.0.1",       
    author="IrenicFalcon",      
    description="OSINT photo search for people based on Search4Faces", 
    long_description=open("README.md").read(), 
    long_description_content_type="text/markdown", 
    url="https://github.com/IrenicFalcon/photohunt-osint", 
    packages=find_packages(),
    license="MIT",
    keywords="osint photo search4faces search people",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
        "Framework :: AsyncIO", 
    ],
    python_requires=">=3.6", 
    install_requires=[ 
        "httpx", 
        "jinja2",    
        "openpyxl",    
        "aiofiles",      
        "tqdm",         
    ],
    entry_points={ 
        "console_scripts": [
            "photohunt=photohunt.__main__:main",  
        ],
    },
)