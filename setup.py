from setuptools import setup, find_packages

version = '0.0'

setup(name='acc',
      version=version,
      description="An implementation of Accounting Pattern by Martin Fowler",
      long_description="""\
""",
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='accounting',
      author='Kenji Noguchi',
      author_email='tokyo246@gmail.com',
      url='https://github.com/knoguchi/acc',
      license='Apache License Version 2.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "py-money"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      setup_requires=['nose>=1.0']
      )
