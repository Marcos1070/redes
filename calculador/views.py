from django.shortcuts import render
import math

def calcular(request):
    
    #usamos un diccionario de contexto para pasar las variables ordenadas al html, arranca vacio por defecto para que la carga inicial (GET) las variables no existan y la plantilla no intente renderizar resultados antes de tiempo
    contexto = {}

    if request.method == 'POST':

        # DATOS OBLIGATORIOS (capturamos strings primero para el contexto)
        distancia_str = request.POST.get("distancia")
        frecuencia_str = request.POST.get("frecuencia")

        # guardamos los valores ingresados en el contexto para mantenerlos en los input del html
        contexto['distancia'] = distancia_str
        contexto['frecuencia'] = frecuencia_str

        # convertimos en float para los calculos
        distanciaTotal = float(distancia_str)
        frecuencia = float(frecuencia_str)

        # radio maximo en el punto medio
        resultado = 8.656 * math.sqrt(distanciaTotal / frecuencia)
        resultado_entero = int(resultado * 100) #RESULTADO TRUNCADO (NO REDONDEADO)
        resultado = resultado_entero / 100
        contexto['resultado'] = resultado #guardamos el resultado en el contexto


        #OPCIONES AVANZADAS
        #DATOS EN FORMA DE STRINGS QUE SE OBTUVIERON DEL HTML (HAY QUE PASARLOS A NUMEROS REALES)
        
        stringAltura1 = request.POST.get('altura1')
        stringAltura2 = request.POST.get('altura2')
        stringDisObs = request.POST.get('distanciaObs')
        stringAltObs = request.POST.get('alturaObs')


        #guardamos los valores ingresados en el contexto para mantenerlos en el html

        contexto['altura1'] = stringAltura1
        contexto['altura2'] = stringAltura2
        contexto['distanciaObs'] = stringDisObs
        contexto['alturaObs'] = stringAltObs
 

        #si ingreso alturas de antenas (con o sin obstaculo explicito)
        if stringAltura1 and stringAltura2:
            alt1 = float(stringAltura1)
            alt2 = float(stringAltura2)

            #si no ingreso un obstaculo particular, evaluamos el punto medio por defecto
            if stringDisObs:
                disObs = float(stringDisObs)
                altObs = float(stringAltObs) if stringAltObs else 0.0

            else:
                disObs = distanciaTotal / 2
                altObs = 0.0 #nivel del suelo en el punto medio

            if disObs < distanciaTotal:
                distanciaRestante = distanciaTotal - disObs

                #radio de la zona de Fresnel en la posicion evaluada
                radioObsCrudo = 17.32 * math.sqrt((disObs * distanciaRestante) / (frecuencia * distanciaTotal))  ## El 17.32 equivale a sqrt(300), constante que resulta de adaptar la velocidad de la luz y convertir km a metros.
                radioObs = int(radioObsCrudo * 100) / 100 #truncamos el numero para quedarnos con un resultado mas corto

                #altura de la linea de vista (LOS) sobre el obstaculo
                alturaLOS_cruda = alt1 + ((alt2 - alt1) * (disObs / distanciaTotal))
                alturaLOS = int(alturaLOS_cruda * 100) / 100 #truncamos de nuevo

                #punto mas bajo de la zona de fresnel (LOS - Radio)
                punto_inferior_fresnel = alturaLOS - radioObs

                #obstruccion respecto al suelo u objeto
                # si el objeto/suelo penetra la zona:
                altura_obstruccion = max(0.0, altObs - punto_inferior_fresnel) if altObs > 0 else max(0.0, -punto_inferior_fresnel)

                #porcentaje de la zona invadida por el suelo/obstaculo
                porcentaje_obstruido = (altura_obstruccion / radioObs) * 100 if radioObs > 0 else 0
                porcentaje_obstruido = int(porcentaje_obstruido * 100) / 100

                # la invacion no debe superar el 40% (mantiene el 60% libre)
                despejado = porcentaje_obstruido <= 40.0


                contexto['evaluar_obstaculo'] = True
                contexto['radioObs'] = radioObs
                contexto['alturaLOS'] = alturaLOS
                contexto['porcentaje_obstruido'] = porcentaje_obstruido
                contexto['despejado'] = despejado
                contexto['involucra_suelo'] = punto_inferior_fresnel < 0    

            else:
                contexto['error_obstaculo'] = "La distancia al obstaculo debe ser menor que la distancia total"

    return render(request, 'calculador/index.html', contexto) # render: renderiza la plantilla HTML y le pasa la variable contexto para que se muestre en pantalla