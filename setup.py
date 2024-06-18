from setuptools import setup, find_packages

setup(
    name='app-usage-gui',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={
        'app_usage_gui': ['resources/*'],
    },
    install_requires=[
        'psutil',
        'tk'
    ],
    entry_points={
        'console_scripts': [
            'app-usage-gui=app_usage_gui.main:main',
        ],
    },
)
