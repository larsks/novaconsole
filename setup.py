import setuptools

setuptools.setup(
    install_requires=open('requires.txt').readlines(),
    version=1,
    name='novaconsole',
    packages=['novaconsole'],
    entry_points={
        'console_scripts': [
            'novaconsole = novaconsole.main:main',
        ],
    }
)
