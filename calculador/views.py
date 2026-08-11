from django.shortcuts import render
import math


def truncar_dos_decimales(valor):
    # Trunca a 2 decimales y devuelve un string exacto para renderizar sin imprecisiones
    return f"{math.floor(valor * 100) / 100:.2f}"


def calcular(request):
    contexto = {}

    if request.method == 'POST':

        # DATOS OBLIGATORIOS
        distancia_str = request.POST.get("distancia")
        frecuencia_str = request.POST.get("frecuencia")

        contexto['distancia'] = distancia_str
        contexto['frecuencia'] = frecuencia_str

        distanciaTotal = float(distancia_str)
        frecuencia = float(frecuencia_str)

        # Radio máximo en el punto medio
        resultado_crudo = 8.656 * math.sqrt(distanciaTotal / frecuencia)
        contexto['resultado'] = truncar_dos_decimales(resultado_crudo)


        # OPCIONES AVANZADAS
        stringAltura1 = request.POST.get('altura1')
        stringAltura2 = request.POST.get('altura2')
        stringDisObs = request.POST.get('distanciaObs')
        stringAltObs = request.POST.get('alturaObs')

        contexto['altura1'] = stringAltura1
        contexto['altura2'] = stringAltura2
        contexto['distanciaObs'] = stringDisObs
        contexto['alturaObs'] = stringAltObs


        if stringAltura1 and stringAltura2:
            alt1 = float(stringAltura1)
            alt2 = float(stringAltura2)

            if stringDisObs:
                disObs = float(stringDisObs)
                altObs = float(stringAltObs) if stringAltObs else 0.0
            else:
                disObs = distanciaTotal / 2
                altObs = 0.0 

            if disObs < distanciaTotal:
                distanciaRestante = distanciaTotal - disObs

                # 1. Calculamos los valores crudos en float para mantener precisión matemática interna
                radioObsCrudo = 17.312 * math.sqrt((disObs * distanciaRestante) / (frecuencia * distanciaTotal))
                alturaLOS_cruda = alt1 + ((alt2 - alt1) * (disObs / distanciaTotal))
                
                # Para la lógica interna usaremos el radio numérico truncado
                radio_num = math.floor(radioObsCrudo * 100) / 100
                altura_los_num = math.floor(alturaLOS_cruda * 100) / 100

                punto_inferior_fresnel = altura_los_num - radio_num

                altura_obstruccion = max(0.0, altObs - punto_inferior_fresnel) if altObs > 0 else max(0.0, -punto_inferior_fresnel)

                porcentaje_crudo = (altura_obstruccion / radio_num) * 100 if radio_num > 0 else 0
                porcentaje_num = math.floor(porcentaje_crudo * 100) / 100

                despejado = porcentaje_num <= 40.0

                #calculo de metros faltantes (solo si hay obstruccion)
                if not despejado:
                    #la LOS requiere estar como minimo en: Altura del obstaculo + 60% del radio 
                    los_minima = altObs + (0.6 * radio_num)
                    metros_faltantes_num = max(0.0, los_minima - altura_los_num)
                    contexto['metros_faltantes'] = truncar_dos_decimales(metros_faltantes_num)

                # 2. Asignamos al contexto la versión formateada en texto exacto
                contexto['evaluar_obstaculo'] = True
                contexto['radioObs'] = truncar_dos_decimales(radioObsCrudo)
                contexto['alturaLOS'] = truncar_dos_decimales(alturaLOS_cruda)
                contexto['porcentaje_obstruido'] = truncar_dos_decimales(porcentaje_crudo)
                contexto['despejado'] = despejado
                contexto['involucra_suelo'] = punto_inferior_fresnel < 0    

            else:
                contexto['error_obstaculo'] = "La distancia al obstaculo debe ser menor que la distancia total"

    return render(request, 'calculador/index.html', contexto)