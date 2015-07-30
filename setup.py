from setuptools import setup, find_packages

dependencies = []

setup(
    name="ceilometer-janitor",
    version="0.1.5",
    packages=find_packages(),
    install_requires=dependencies,
    author="Jorge Niedbalski R.",
    author_email="jnr@metaklass.org",
    description="Cleanup vms based on ceilometer stats",
    keywords="ceilometer vm stats",
    include_package_data=True,
    license="BSD",
    entry_points={
	'console_scripts' : [
		'ceilometer-janitor = ceilometer_janitor:main'
	]
    },

    classifiers=['Development Status :: 3 - Alpha',
                'Intended Audience :: Developers',
                'Operating System :: Unix ']
)
