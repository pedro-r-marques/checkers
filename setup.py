import setuptools
from Cython.Build import cythonize

setuptools.setup(name='checkers',
                 author='Pedro Marques',
                 author_email='pedro.r.marques@gmail.com',
                 description='Checkers',
                 url='https://github.com/pedro-r-marques/checkers',
                 packages=setuptools.find_packages(),
                 ext_modules=cythonize([
                     setuptools.Extension(
                         "libcheckers.py_checkers", sources=[
                             "libcheckers/py_checkers.pyx",
                         ],
                         extra_compile_args=['-std=c++17'],
                         language='c++',
                     ),
                     setuptools.Extension(
                         "libcheckers.py_scorer", sources=[
                             "libcheckers/py_scorer.pyx",
                         ],
                         extra_compile_args=['-std=c++17'],
                         language='c++',
                     )
                 ], compiler_directives={'language_level': "3"}),
                 zip_safe=False,
                 install_requires=[
                     'flask',
                 ],
                 include_package_data=True,
                 python_requires='>=3.9',
                 version='0.0.1')
