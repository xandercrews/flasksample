from setuptools import setup
from setuptools import find_packages

VERSION = (0,0,1)

setup(
	name='flasksample',
	version='.'.join(['%d' % v for v in VERSION]),
	description='Flask boilerplate project for REST',
	author='jonathan',
	author_email='None',
	license='None',
	packages=find_packages(),
	scripts=(
        'bin/flasksample',
	),
	include_package_data=True,
	data_files=(
            # TODO
	),

	# requirements
	setup_requires=(
		'setuptools==5.7',
	),
	install_requires=(
		'Flask==0.10.1',
		'PyYAML==3.11',
		'config==0.3.9',
        'gevent==1.0.1',
        'supervisor==3.1.1',
	),
	tests_require=(
		'nose>=1.0',
		'mock>=1.0.1',
        'coverage',
	),
)
