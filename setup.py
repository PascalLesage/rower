from setuptools import setup

setup(
    name='rower',
    version="0.0.dev",
    packages=["rower"],
    package_data={'rower': ["data/*/*.json"]},
    author="Pascal Lesage",
    author_email="pascal.lesage@polymtl.com",
    #license=""
    url="https://github.com/PascalLesage/rower",
    install_requires=['bw2data', 'appdirs'],
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
