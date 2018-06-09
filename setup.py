from setuptools import setup

setup(
    name='rower',
    version="0.1",
    packages=["rower"],
    package_data={'rower': ["data/*/*.*"]},
    author="Pascal Lesage",
    author_email="pascal.lesage@polymtl.com",
    license=open('LICENSE').read(),
    url="https://github.com/PascalLesage/rower",
    install_requires=['bw2data', 'appdirs', 'pyprind'],
    long_description=open('README.md').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
    ],
)
