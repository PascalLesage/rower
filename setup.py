from setuptools import setup

setup(
    name='RoWer',
    version="0",
    packages=["RoWer"],
    package_data={'RoWer': ["data/*.json"]},
    author="Pascal Lesage",
    author_email="pascal.lesage@polymtl.com",
    #license=""
    url="https://github.com/PascalLesage/RoWer",
    install_requires=['bw2data'],
    # long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        #'Operating System :: Microsoft :: Windows',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)
