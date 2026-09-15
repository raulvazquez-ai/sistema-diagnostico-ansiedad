class NormalizadorDatos:
    def normalizar(self, datos_brutos):
        mapping_edad = {'Joven': 0, 'Normal': 1, 'Anciano': 2}
        normal = {}

        normal['antecedentes'] = 1 if datos_brutos.get('antecedentes') == 1 else 0

        normal['edad'] = mapping_edad.get(datos_brutos.get('edad'), 1) 

        normal['estres'] = 1 if datos_brutos.get('estres') == 1 else 0
        
        sintomas_list = datos_brutos.get('sintomas', [])
        all_sintomas = ['Nerviosismo', 'Fatiga', 'Concentracion', 'Irritabilidad', 'TensionMuscular', 'Sueño']
        sintomas = {s: (1 if s in sintomas_list else 0) for s in all_sintomas}
        normal['sintomas'] = sintomas
        
        return normal

print("Iniciando prueba de NormalizadorDatos...")

normalizador = NormalizadorDatos()

datos_brutos_1 = {
    'antecedentes': 1,  
    'edad': 'Joven',
    'estres': 0,        
    'sintomas': []      
}

print(f"\n--- Prueba 1 ---")
print(f"Probando con datos (Joven, Sí, No): {datos_brutos_1}")

normalizado_1 = normalizador.normalizar(datos_brutos_1)

print(f"Resultado normalizado 1: {normalizado_1}")
print("Verificación de valores:")
print(f"  Valor para 'Joven' (edad): {normalizado_1['edad']} (Esperado: 0)")
print(f"  Valor para 'Sí' (antecedentes): {normalizado_1['antecedentes']} (Esperado: 1)")
print(f"  Valor para 'No' (estres): {normalizado_1['estres']} (Esperado: 0)")

datos_brutos_2 = {
    'antecedentes': 0,  
    'edad': 'Anciano',
    'estres': 1,        
    'sintomas': ['Fatiga', 'Irritabilidad']
}

print(f"\n--- Prueba 2 ---")
print(f"Probando con datos (Anciano, No, Sí, con síntomas): {datos_brutos_2}")

normalizado_2 = normalizador.normalizar(datos_brutos_2)

print(f"Resultado normalizado 2: {normalizado_2}")
print("Verificación de valores:")
print(f"  Valor para 'Anciano' (edad): {normalizado_2['edad']} (Esperado: 2)")
print(f"  Valor para 'No' (antecedentes): {normalizado_2['antecedentes']} (Esperado: 0)")
print(f"  Valor para 'Sí' (estres): {normalizado_2['estres']} (Esperado: 1)")
print(f"  Valor para 'sintomas' (Fatiga=1, Irritabilidad=1): {normalizado_2['sintomas']['Fatiga'] == 1 and normalizado_2['sintomas']['Irritabilidad'] == 1}")

print("\nPrueba finalizada.")