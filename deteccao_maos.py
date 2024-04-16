import os

import cv2
import mediapipe as mp


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


while True:
    sucesso, img = camera.read()
    img = cv2.flip(img, 1) # invertendo a esquerda pela direita
    img,todas_maos = encontra_coordenadas_maos(img)
    
    if len(todas_maos) == 1: #so irá mandar os comandos caso tenha uma mão na tela
        if todas_maos[0]["lado"] == "Right":
            info_dedos_mao1 = dedos_levantados(todas_maos[0])
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