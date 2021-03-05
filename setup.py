import setuptools
from Cython.Build import cythonize

setuptools.setup(name='checkers',
                 author='Pedro Marques',
                 author_email='pedro.r.marques@gmail.com',
                 description='Checkers',
                 url='https://github.com/pedro-r-marques/checkers',
                 packages=setuptools.find_packages(),
                 ext_modules=cythonize([setuptools.Extension(
                     "checkers.checkers_lib", sources=[
                         "checkers/py_checkers.pyx",
                     ],
                     extra_compile_args=['-std=c++17'],
                     language='c++',
                 )], compiler_directives={'language_level': "3"}),
                 zip_safe=False,
                 install_requires=[
                     'flask',
                 ],
                 include_package_data=True,
                 python_requires='>=3.8',
                 version='0.0.1')
