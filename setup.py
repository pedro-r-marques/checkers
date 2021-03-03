import setuptools

setuptools.setup(name='checkers',
                 author='Pedro Marques',
                 author_email='pedro.r.marques@gmail.com',
                 description='Checkers',
                 url='https://github.com/pedro-r-marques/checkers',
                 packages=setuptools.find_packages(),
                 install_requires=[
                     'flask',
                 ],
                 include_package_data=True,
                 python_requires='>=3.8',
                 version='0.0.1')
