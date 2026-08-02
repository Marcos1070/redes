from django.shortcuts import render
import math

def calcular(request):
    
    #usamos un diccionario de contexto para pasar las variables ordenadas al html, arranca vacio por defecto para que la carga inicial (GET) las variables no existan y la plantilla no intente renderizar resultados antes de tiempo
    contexto = {}

    if request.method == 'POST':

        #OPCIONES POR DEFECTO

        distanciaTotal = float(request.POST.get("distancia"))
        frecuencia = float(request.POST.get("frecuencia"))

        resultado = 8.656 * math.sqrt(distanciaTotal / frecuencia)

        #RESULTADO TRUNCADO (NO REDONDEADO)
        resultado_entero = int(resultado * 100)
        resultado = resultado_entero / 100

        #guardamos el resultado en el contexto
        contexto['resultado'] = resultado


        #OPCIONES AVANZADAS
        #DATOS EN FORMA DE STRINGS QUE SE OBTUVIERON DEL HTML (HAY QUE PASARLOS A NUMEROS REALES)
        
        stringAltura1 = request.POST.get('altura1')
        stringAltura2 = request.POST.get('altura2')
        stringDisObs = request.POST.get('distanciaObs')
        stringAltObs = request.POST.get('alturaObs')

        #si el usuario completo todos esos datos opcionales
        if stringAltura1 and stringAltura2 and stringDisObs and stringAltObs:
            alt1 = float(stringAltura1)
            alt2 = float(stringAltura2)
            disObs = float(stringDisObs)
            altObs = float(stringAltObs) 

            #validacion: la distancia al obstaculo no puede ser mayor que la distancia total

            if disObs < distanciaTotal:
                distanciaRestante = distanciaTotal - disObs

                #radio de la zona de Fresnel en el punto del obstaculo
                radioObsCrudo = 17.32 * math.sqrt((disObs * distanciaRestante) / (frecuencia * distanciaTotal))  ## El 17.32 equivale a sqrt(300), constante que resulta de adaptar la velocidad de la luz y convertir km a metros.
                radioObs = int(radioObsCrudo * 100) / 100 #truncamos el numero para quedarnos con un resultado mas corto

                #altura de la linea de vista (LOS) sobre el obstaculo
                alturaLOS_cruda = alt1 + ((alt2 - alt1) * (disObs / distanciaTotal))
                alturaLOS = int(alturaLOS_cruda * 100) / 100 #truncamos de nuevo

                #limite inferior de la zona (60% libre recomendado)
                limite60 = alturaLOS - (0.6 * radioObs)


                #calculo de diferencia con respecto al limite del 60%
                diferencia_cruda = altObs - limite60
                margen = int(diferencia_cruda * 100) / 100

                contexto['evaluar_obstaculo'] = True
                contexto['radioObs'] = radioObs
                contexto['alturaLOS'] = alturaLOS
                contexto['margen'] = abs(margen) #se usa el abs para mostrar siempre un numero positivo
                contexto['despejado'] = altObs <= limite60

            else:
                contexto['error_obstaculo'] = "La distancia al obstaculo debe ser menor que la distancia total"

    return render(request, 'calculador/index.html', contexto) # render: renderiza la plantilla HTML y le pasa la variable contexto para que se muestre en pantalla