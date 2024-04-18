import os
from time import sleep

import cv2
import mediapipe as mp
from pynput.keyboard import Controller

branco = (255,255,255)
preto = (0,0,0)
azul = (255,0,0)
verde = (0,255,0)
vermelho = (0,0,255)
azul_claro = (255,255,0)

teclas = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A','S','D','F','G','H','J','K','L'],
            ['Z','X','C','V','B','N','M', ',','.',' ']]
offset =50




mp_maos= mp.solutions.hands
mp_desenho = mp.solutions.drawing_utils

maos = mp_maos.Hands()

camera = cv2.VideoCapture(0) #CAPTURANDO A WEBCAM

resolucao_x = 1280
resolucao_y = 720
camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolucao_x)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolucao_y)
bloco_notas = False
chorme = False
calculadora = False
contador = 0 
texto = ">"
teclado = Controller()

def encontra_coordenadas_maos(img, lado_invertido = False):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
    resultado = maos.process(img_rgb)
    todas_maos= []

    if resultado.multi_hand_landmarks: #se detectar alguma mão desenha a mão
        for lado_maos, marcacao_maos in zip(resultado.multi_handedness ,resultado.multi_hand_landmarks): #multi_hand_landmarks são as coordenadas dos pontos das mãos
            info_maos = {}
            coordenadas = []
            for macacao in marcacao_maos.landmark: #for feito para amzernar as cordenadas dos pontos(landmark) adptada para pixel
                cord_x, cord_y, cord_z = int(macacao.x *resolucao_x ),int(macacao.y *resolucao_y ),int(macacao.z *resolucao_x )
                # print(cord_x, cord_y, cord_z)
                coordenadas.append((cord_x, cord_y, cord_z))
            info_maos['coordenadas'] = coordenadas
            todas_maos.append(info_maos)
            if lado_invertido:
                if lado_maos.classification[0].label == "Left":
                    info_maos["lado"] = "Right"
                else:
                    info_maos["lado"] = "Left"
            else:
                info_maos["lado"] = lado_maos.classification[0].label 
            # print(lado_maos.classification[0].label)
            # print(info_maos["lado"])
            mp_desenho.draw_landmarks(img, marcacao_maos, mp_maos.HAND_CONNECTIONS) #desenhando as coordenadadas e as conexões da mãos


    return img, todas_maos



def dedos_levantados(mao):
    dedos = []
    for ponta_dedo in [8,12,16,20]:
        if mao["coordenadas"][ponta_dedo][1] < mao["coordenadas"][ponta_dedo-2][1]: #verificando se a ponta do dedo é menor que a base base do dedo (menor pq o topo é 0 quanto mais baixo maior)
            dedos.append(True)
        else:
            dedos.append(False)
    return(dedos)


def imprime_botoes(img, posicao, letra, tamanho =50, cor_retangulo = branco):
    cv2.rectangle(img,posicao,(posicao[0]+tamanho, posicao[1]+tamanho),cor_retangulo,cv2.FILLED)
    cv2.rectangle(img,posicao,(posicao[0]+tamanho, posicao[1]+tamanho),azul,2)
    cv2.putText(img, letra, (posicao[0]+15, posicao[1]+30), cv2.FONT_HERSHEY_COMPLEX, 1, preto, 1)
    return img

while True:
    sucesso, img = camera.read()
    img = cv2.flip(img, 1) # invertendo a esquerda pela direita
    img,todas_maos = encontra_coordenadas_maos(img)


    
    if len(todas_maos) == 1: #so irá mandar os comandos caso tenha uma mão na tela
        info_dedos_mao1 = dedos_levantados(todas_maos[0])
        if todas_maos[0]["lado"] == "Left":
            indicador_x, indicador_y, indicador_z = todas_maos[0]['coordenadas'][8]
            cv2.putText(img, f'Distancia camera: {indicador_z}', (850, 50), cv2.FONT_HERSHEY_COMPLEX,1,branco,2)

            for indice_linha, linha_teclado in enumerate(teclas):
                for indice, letra in enumerate(linha_teclado):
                    if sum(info_dedos_mao1) <= 1: 
                        letra = letra.lower()
                    img= imprime_botoes(img, (offset+indice*80, indice+indice_linha*80), letra)

                    if offset+indice*80 < indicador_x < 100+indice*80 and offset+indice_linha*80 < indicador_y < 100+indice_linha*80:
                        img = imprime_botoes(img, (offset+indice*80, indice+indice_linha*80), letra, cor_retangulo=verde)
                        if indicador_z<-85:
                            contador = 1 
                            escreve = letra
                            img = imprime_botoes(img, (offset+indice*80, indice+indice_linha*80), letra, cor_retangulo=azul_claro)
            if contador: 
                contador +=1
                if contador==3:
                    texto += escreve
                    contador=0
                    teclado.press(escreve)
            if info_dedos_mao1 == [False, False, False, True] and len(texto)>1:
                texto = texto[:-1]
                sleep(0.15)

            cv2.rectangle(img, (offset, 450),(830, 500), branco, cv2.FILLED)
            cv2.rectangle(img, (offset, 450),(830, 500), azul, 1)
            cv2.putText(img, texto[-40:],(offset, 480), cv2.FONT_HERSHEY_COMPLEX, 1, preto,2 )
            cv2.circle(img,(indicador_x, indicador_y),7, azul, cv2.FILLED)

        if todas_maos[0]["lado"] == "Right":
            print(info_dedos_mao1)
            if info_dedos_mao1 == [True,False,False,False] and bloco_notas==False:
                os.startfile(r"C:\Windows\system32\notepad.exe")
                bloco_notas=True
            if info_dedos_mao1 == [True,True,False,False] and chorme==False:
                os.startfile(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
                chorme=True
            if info_dedos_mao1 == [True,True,True,False] and calculadora==False:
                os.startfile(r'C:\Windows\system32\calc.exe')
                calculadora=True
            if info_dedos_mao1 == [False,False,False,False] and bloco_notas==True:
                os.system("TASKKILL /IM notepad.exe")
                bloco_notas=False
            if info_dedos_mao1 == [True,False,False,True]:
                break


    cv2.imshow('Imagem', img)

    tecla = cv2.waitKey(1) #espera uma tecla ou 1 milisegundo

    if tecla == 27:  #esc para o codigo
        break
with open('texto.txt', 'w') as arquivo:
    arquivo.write(texto)