from setuptools import setup

setup(
    name='GBUtils',
    version='53',
    py_modules=['GBUtils'],
    
    # AGGIUNTO: Elenco delle dipendenze necessarie per GBUtils
    install_requires=[
        'numpy',
        'sounddevice',
        'scipy',
    ],

    author='Gabriele Battaglia',
    author_email='tuo.iz4apu@libero.it',
    description='Pacchetto di utilities varie per i miei software',
    url='https://github.com/GabrieleBattaglia/GBUtils',
)