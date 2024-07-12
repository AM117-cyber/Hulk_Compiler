import subprocess
from pathlib import Path

def test_run_pipeline():
    # Define la ruta del archivo main.py
    main_file = Path('main.py')

    # Define la ruta del archivo de entrada
    input_file = Path('custom_test1.hulk')

    # Define la ruta del archivo de salida
    output_file = Path('end.c')

    # Ejecuta main.py 20 veces
    for i in range(40):
        # Ejecuta main.py con el archivo de entrada y salida como argumentos
        subprocess.run(['python', main_file, input_file, output_file])
        with open('ok.txt', 'a', encoding='utf-8') as file:
            file.write(str(i))
# Ejecuta la prueba
test_run_pipeline()
