from setuptools import setup
from Cython.Build import cythonize
import numpy as np

setup(
    name='Darts Recognition',
    ext_modules=cythonize(
        "core/helper_functions/binary_diff_images.pyx",
        language_level="3",
    ),
    include_dirs=[np.get_include()],
    zip_safe=False,
)
