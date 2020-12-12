# -*- coding: utf-8 -*-
"""proyecto_final_matdis2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JbGFVDSryWCprZgYQddwIR5MPTsUKD4x

**Integrantes:**

María Alejandra Jiménez Herrera <<majimenezh@unal.edu.co>>, 1193127371

Juan Pablo Delgado Cárcamo <<judelgadoc@unal.edu.co>>, 1001218721

# Problema

SHA-256 es una función hash criptográfica utilizada en seguridad web, transacciones de Bitcoin [1]
entre otros. Este algoritmo originalmente se diseñó con números primos como base y es
supremamente eficiente ya que desde el 2001 [2] que fue publicado no se le han encontrado
colisiones.
Como proyecto para el final de la materia pensamos en modificar este algoritmo cambiando la base
de números primos [2, 3] a números compuestos para hacer una comparación de nuestra
modificación respecto al algoritmo original.
Con el contenido que hemos visto en las clases hemos aprendido que el manejo de números primos
con módulos disminuye la probabilidad de encontrar colisiones para ciertos algoritmos entonces
queremos hacer un análisis de resultados con el experimento.

# State of the art
Sha-2 es un algoritmo muy conocido y sorprendente por su eficiencia y utilidad, por esto mismo otras personas ya han analizado cada parte de éste y hecho modificaciones para estudiar sus resultados, a continuación algunos ejemplos:

* Sha-2 es la mejoría de Sha-1 que a su vez es la evolución de Sha-0; Sha-0 Fue publicado en 1993 y atacado en 1998 por su vulnerabilidad matemática.En el 2000 aparece Sha-1 que aunque no fue atacado exitosamente, en el 2004 se le encontró una debilidad matemática, en el 2001 aparece Sha-2 al que no se le han encontrado colisiones hasta el momento y ha sido objeto de estudio de muchos criptógrafos[4]. 

* [5] Realizó una comparación de los algoritmos Sha-1 y Sha-2 modificando las condiciones iniciales de cada uno para comparar la aletoriedad modelandola con teoría de probabilidad Bayesiana y adicional a esto hicieron una modificacion de Sha usando la función Sha-1 con los manipuladores de funciones de Sha-2.

* En el 2018 [6] hicieron una modificación del Sha-1 y compararon la eficiencia con el original. La modificación consistía en adicionar un contador dentro de uno de los ciclos aumentando el resumen del mensaje de 160 a 192 bits.

# Materiales y métodos

Para materiales y métodos vale la pena explicar el arreglo de los mensajes, en sha256 necesitamos que cada mensaje sea de 512 bits, para esto se hace un proceso que [4,7] definen como "message padding", sin embargo solo describen el algoritmo sin explicar sus fundamentos matemáticos.
El algoritmo tiene muchos pasos que reducen significativamente la posibilidad de colisiones y usa sistema hexadecimal, La modificación hecha respecto al algoritmo principal consiste en cambiar un arreglo de numeros primos en hexadecimal por un arreglo de no primos y convetirlos en hexadecimal. Estos numeros son la base de todo el algoritmo

Como acabamos de comentar, el algoritmo original tiene un valor inicial, es un arreglo de cadenas hexadecimales que en nuestra implementación llamamos DM, o digest message. Estas cadenas se obtienen al tomar los primeros 32 bits de la parte fraccionaria de la raíz cuadrada de los primeros 8 números primos

Por ejemplo $(\sqrt{2})_{10}= (1.4142135623730951)_{10} =(1.6A09E667F3BCCCB9242B)_{16}$

Entonces tomamos como primer valor de DM a $6A09E667$

Similarmente, tenemos otro arreglo de constantes definidas en el algoritmo original, llamado K, en este caso tomamos los primeros 64 números primos, y en lugar de la raíz cuadrada aplicamos la raíz cúbica.

Por ejemplo $(\sqrt[3]{2})_{10}= (1.2599210498948732)_{10} =(1.428A2F98D728B0AC2C)_{16}$

Entonces tomamos como primer valor de DM a $428A2F98$

La definición del algoritmo también indica que los mensajes deben ser de 512 bits, para hacerlo se hace un procedimiento llamado message padding.

Ahora, con nuestro mensaje de 512 bits, lo dividimos en bloques de 64 bits.
Teniendo esto en cuenta, un pseudocódigo del sha256 es
```
for each bloque:
    W[0..15] <- Los primeros 16 sub bloques de 4 bits
    for i <- 16, i < 63, i <- i+1:
        W[i] <- W[i - 16] + sigma_0(W[i-15]) + W[i-7] + sigma_1(W[i-2])
    A, B, C, D, E, F, G, H <- DM
    for i <- 0, i <= 63, i <- i+1:
        temp_1 <- H + Sigma_1(E) + Ch(E, F, G) + W[i] + K[i]
        A, B, C, D, E, F, G, H <- T_1 + Sigma_0(A) + Maj(A, B, C), A, B, C, (D + T_1), E, F, G 
    for i <- 0, i <- 8, i <- i+1:
        DM[i] <- suma de la letra correspondiente con el valor actual de DM[i]
    return DM
```
Donde sigma_0, sigma_1, Sigma_0, Sigma_1, Ch, Maj son funciones bit a bit, toda operación retorna valores de 32 bytes.
"""

import math, timeit

# Para hacer compresión y mantenerme en los 32 bytes
W = 32         
M = 1 << W
FF = M - 1      


# primos vs no-primos para las constantes iniciales de compresión 
def get_K(with_primes):
    """
    Si usamos el algoritmo con primos, tomará el arreglo de constantes
    iniciales que hemos comentado.
    En caso contrario tomará los primeros 32 bits de la parte fraccionaria
    de la raíz cúbica de los números compuestos en el conjunto [4, 87], es decir
    el mismo procedimiento que en el algoritmo original solo que esta vez usando
    números compuestos

    Rápidamente notamos que si usamos números compuestos corremos el riesgo de
    tener una constante 0, por ejemplo la raíz cúbica de 8 es 2, número cuya parte
    fraccionaria es exactamente 0. 
    """
    if with_primes:
        K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
            0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
            0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
            0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
            0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
            0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
            0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
            0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
            0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]
    else:
        chosen_list = [4,6,8,9,10,12,14,15,16,18,20,21,22,24,25,26,
             27,28,30,32,33,34,35,36,38,39,40,42,44,45,46,48,
             49,50,51,52,54,55,56,57,58,59,60,62,63,64,65,66,
             68,69,70,72,74,75,76,77,78,80,81,82,84,85,86,87]
        K = []
        for i in chosen_list:
            temp = math.pow(i, 1/3)
            temp = float.hex(math.modf(temp)[0]).split("p")
            K.append(int(temp[0][4:12], 16))
    return K
        

# primos vs no-primos para los digest messages
def get_DM(with_primes):
    """
    Si usamos el algoritmo con primos, tomará el arreglo de constantes
    iniciales que hemos comentado.
    En caso contrario tomará los primeros 32 bits de la parte fraccionaria
    de la raíz cúbica de los números compuestos en el conjunto [4, 87], es decir
    el mismo procedimiento que en el algoritmo original solo que esta vez usando
    números compuestos
    """
    if with_primes:
        DM = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
              0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
    else:
        chosen_list = [4,6,8,9,10,12,14,15]
        DM = []
        for i in chosen_list:
            temp = math.pow(i, 1/2)
            temp = float.hex(math.modf(temp)[0]).split("p")
            DM.append(int(temp[0][4:12], 16))
    return DM

def rotr(x, b):
    """
    Rotar b bits a la derecha, por ejemplo 1000 sería 0001 con b=1
    """
    return ((x >> b) | (x << (W - b))) & FF

def Pad(W):
    """
    Para hacer el message padding, debemos resolver para k la ecuación l+1+k = 448 (mod 512) donde l:=tamaño del mensaje.
    Luego de eso por definición escribimos W + 1 + k veces 0 + l, todo en bits, donde +:= concatenación, W:= mensaje
    decimos que mdi = l/8, npad = k/8, entonces l + k - 447 = 0 (mod 512), si quitamos 7 bits (el \x80)
    y los agregamos después tenemos que l + k - 440 = 0 (mod 64), entonces npad = 55 - mdi, 
    similarmente se puede demostrar el caso con mdi > 56
    """
    mdi = len(W) % 64           
    L = (len(W) << 3).to_bytes(8, 'big') 
    npad = 55 - mdi if mdi < 56 else 119 - mdi  
    return bytes(W, 'utf-8') + b'\x80' + (b'\x00' * npad) + L   


def Maj(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)

def Ch(x, y, z):    
    return (x & y) ^ (~x & z)

def Sigma_0(x):
    return rotr(x, 2)^rotr(x, 13)^rotr(x, 22)

def Sigma_1(x):
    return rotr(x, 6)^rotr(x, 11)^rotr(x, 25)

def sigma_0(x):
    return rotr(x, 7)^rotr(x, 18)^x>>3

def sigma_1(x):
    return rotr(x, 17)^rotr(x, 19)^x>>10

def sha256(M, with_primes=True):
    M = Pad(M)         
    DM = get_DM(with_primes)
    K = get_K(with_primes)      
    for j in range(0, len(M), 64):  
        S = M[j:j + 64]          
        W = [0] * 64
        W[0:16] = [int.from_bytes(S[i:i + 4], 'big') for i in range(0, 64, 4)]  # No olvidar que es big endian
        for i in range(16, 64):
            W[i] = (W[i - 16] + sigma_0(W[i-15]) + W[i-7] + sigma_1(W[i-2])) & FF
        A, B, C, D, E, F, G, H = DM 
        for i in range(64):
            T_1 = H + Sigma_1(E) + Ch(E, F, G) + W[i] + K[i]
            A, B, C, D, E, F, G, H = (T_1 + Sigma_0(A) + Maj(A, B, C)) & FF, A, B, C, (D + T_1) & FF, E, F, G
        DM = [(X + Y) & FF for X, Y in zip(DM, (A, B, C, D, E, F, G, H))]
    bd = b''.join(Di.to_bytes(4, 'big') for Di in DM)
    return ''.join('{:02x}'.format(i) for i in bd)

"""### Experimentos

* Una función hash debe ser determinista, es decir que para el mismo mensaje debe dar el mismo hash, para probar esto haremos la función hash 100 veces con un mensaje y si da diferente marcará "Error" y saldrá del bucle, en caso contrario imprimirá "Correcto" al final.
"""

def exp1(mes, with_primes=True):
    ans = sha256(mes, with_primes)
    temp = ans
    flag = True
    n = 1
    while ans == temp and flag and n<=100:
        temp = sha256(mes, with_primes)
        if (temp != ans):
            flag = False
        n += 1
    if flag:
        print("Correcto")
    else:
        print("Error")

"""* Una función hash debe ser rápida, por lo tanto la ejecutaremos con el mismo mensaje 1000 veces y contabilizaremos el tiempo promedio de ejecución."""

def exp2(mes, with_primes):
    temp = timeit.timeit(lambda: sha256(mes, with_primes), number=1000)/1000
    print("Tamaño del mensaje en bits: %s, tiempo de ejecución en segundos: %s" % (len(mes.encode('utf-8'))*8, temp))

"""* Como sha256 se implementa para seguridad, es conveniente que dos mensajes muy parecidos deben dar resultados diferentes para que sea difícil de vulnerar, por lo tanto ejecutaremos la función con un mensaje y compararemos el resultado ejecutandola con el mensaje menos las últimas 3 letra (experimento 3 solo disponible para cadenas de longitud mayor o igual a 3)"""

def exp3(mes, with_primes):
    hash1 = sha256(mes, with_primes)
    hash2 = sha256(mes[:len(mes)-3], with_primes)
    print("SHA256(mensaje)=%s"%hash1, "SHA256(mensaje_cortado)=%s"%hash2)

"""# Resultados"""

mes = """Había una vez una iguana
Con una ruana de lana
Peinandose la melena junto al río Magdalena"""


print("Experimento 1")
exp1(mes, True)
exp1(mes, False)
print("Experimento 2")
exp2(mes, True)
exp2(mes, False)
print("Experimento 3")
exp3(mes, True)
exp3(mes, False)

"""Estos resultados indican que nuestra implementación del algoritmo es determinista. También es bastante rápida, el tiempo de ejecución con un mensaje de 736 bits es cercano a una milésima de segundo. El último experimento también indica que el algoritmo no revela fácilmente como llegó al resultado obtenido cuando se somete a prueba con mensajes parecidos.

# Conclusiones

Como podemos ver el hash parece cumplir correctamente con las condiciones de rapidez y determinismo.
El algoritmo está tan bien elaborado que los cambios de números primos a no primos no afecta tan significativamente su eficiencia por lo que viendo los resultados sigue funcionando perfectamente bien. Sin embargo es posible que al correrlo muchas veces aparezcan colisiones pero esto es dificil de comprobar.

Sha-2 es un algoritmo sencillo pero muy eficiente, con razón se sigue usando en temas tan importantes como las transacciones de criptomonedas.

# Referencias

[1] S. Nakamoto, «bitcoin,» [En línea]. Available: https://bitcoin.org/files/bitcoin-paper/bitcoin_es_latam.pdf.

[2] Wikipedia, «SHA-2,» [En línea]. Available: https://es.wikipedia.org/wiki/SHA-2.

[3] J. Domínguez-Gómez, «Criptography_SHA_256_es,» [En línea]. Available:
https://academy.bit2me.com/wp-content/uploads/2019/10/Criptography_SHA_256_es.pdf.

[4] Sheikh, Farhana, and Leonel Sousa, editors. Circuits and Systems for Security and Privacy. 0 ed., CRC Press, 2017. DOI.org (Crossref), doi:10.1201/b19499.

[5] Al-Odat, Zeyad, et al. “Randomness Analyses of the Secure Hash Algorithms, SHA-1, SHA-2 and Modified SHA.” 2019 International Conference on Frontiers of Information Technology (FIT), IEEE, 2019, pp. 316–3165. DOI.org (Crossref), doi:10.1109/FIT47737.2019.00066.

[6] Quilala, Rogel. (2018). Modified SHA-1 Algorithm. 11. 1027-1034. https://www.researchgate.net/publication/329183090_Modified_SHA-1_Algorithm

[7] NIST. (2018). Secure Hash Standard. https://csrc.nist.gov/csrc/media/publications/fips/180/4/archive/2012-03-06/documents/fips180-4.pdf
"""