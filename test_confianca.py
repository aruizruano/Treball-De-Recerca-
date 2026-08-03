from detector_claude import analizar_texto_claude

texto = "El drama de los autonomos: 1,5 millones de estos trabajadores no se pueden coger bajas sin cerrar su negocio."

resultado = analizar_texto_claude(texto, verbose=True)

print("\n" + "="*60)
print("RESULTADO PROCESADO:")
print(resultado)
