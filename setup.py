from setuptools import setup, find_packages

setup(
    name='app-usage-gui',
    version='1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={
        'app_usage_gui': ['resources/*'],
    },
    install_requires=[
        'psutil==5.9.8',
        'pynput==1.8.1',
        'requests==2.32.4',
        'pillow==12.1.1',
        'pywinauto==0.6.8',
        'MouseInfo==0.1.3',
        'PyGetWindow==0.0.9',
        'PyMsgBox==1.0.9',
        'pyperclip==1.9.0',
        'PyRect==0.2.0',
        'PyScreeze==1.0.1',
        'pytweening==1.2.0',
        'pyinstaller==6.12.0',
        # macOS specific
        'pyobjc-core==11.0; sys_platform == "darwin"',
        'pyobjc-framework-Cocoa==11.0; sys_platform == "darwin"',
        'pyobjc-framework-Quartz==11.0; sys_platform == "darwin"',
        'rubicon-objc==0.5.0; sys_platform == "darwin"'
    ],
    entry_points={
        'console_scripts': [
            'app-usage-gui=app_usage_gui.main:main',
        ],
    },
)
