import setuptools

setuptools.setup(
    name = 'dropboxuploadspeedtest',
    version = '1.0.0dev',
    packages = setuptools.find_packages(),
    entry_points = {'console_scripts': [
        'dropboxuploadspeedtest = dropboxuploadspeedtest.__main__:main',
    ]},
    install_requires = ['dropbox'],
)
