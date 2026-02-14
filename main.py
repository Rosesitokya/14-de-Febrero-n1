import pygame

import sys

import cv2

import random

from aventura import Aventura

from ritmo import RitmoGame

import os

class Game:
    @staticmethod
    def resource_path(relative_path): # <--- QUITA EL 'self' DE AQUÍ
        """ Obtiene la ruta absoluta de los recursos para PyInstaller """
        import sys, os # Asegúrate de que estén importados
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def __init__(self):

        pygame.init()

        pygame.mixer.set_num_channels(32)

        pygame.mixer.init()

        self.screen = pygame.display.set_mode((800, 600))

        pygame.display.set_caption("¿Quieres ser mi San Valentin?")
        icono_ventana = pygame.image.load(self.resource_path("corazon.ico"))
        pygame.display.set_icon(icono_ventana)

        self.clock = pygame.time.Clock()

       

        try:
            self.img_menu = pygame.image.load(self.resource_path("menu.png")).convert_alpha()
            self.img_menu = pygame.transform.scale(self.img_menu, (800, 600))
        except:
            self.img_menu = pygame.Surface((800, 600))
            self.img_menu.fill((255, 192, 203))



        # --- CARGA DE SPRITES Y RECURSOS ---

        self.sprites = {}

        lista_sprites = ["parado", "paradoatras", "paradoizquierda", "paradoderecha",

                         "caminaizquierda", "caminaderecha", "piernaizatras",

                         "piernaderechaatras", "piernaiz", "piernaderecha", "p1_normal"]

        for n in lista_sprites:
            try:
                self.sprites[n] = pygame.image.load(self.resource_path(f"{n}.png")).convert_alpha()
            except:
                self.sprites[n] = pygame.Surface((50, 50))



        self.obj_imgs = {}

        # Lista de los 7 recuerdos + la carta

        self.objetos_lista = ["cuadro", "taza", "carta", "cinnamoroll", "radio", "calendario", "cheesecake", "gardenia"]

        self.pos_dibujo = {

            "cuadro": (95, 100), "taza": (200, 180), "gardenia": (270, 180),

            "cheesecake": (480, 170), "calendario": (660, 120), "radio": (240, 415),

            "cinnamoroll": (310, 390), "carta": (660, 350)

        }

        for o in self.objetos_lista:
            try:
                self.obj_imgs[o] = pygame.image.load(self.resource_path(f"{o}.png")).convert_alpha()
            except:
                self.obj_imgs[o] = pygame.Surface((40, 40))



        try:
            self.bg_nerissa = pygame.transform.scale(pygame.image.load(self.resource_path("nerissa1.png")), (800, 600))
            self.bg_cocina = pygame.transform.scale(pygame.image.load(self.resource_path("cocina.png")), (800, 600))
            self.img_cuadro_grande = pygame.transform.scale(pygame.image.load(self.resource_path("cuadroima.png")), (450, 450))
            self.img_carta_full = pygame.image.load(self.resource_path("cartaescrita.png")).convert_alpha()
        except:
            print("Error: No se pudieron cargar los fondos o imágenes grandes.")

        try:

            temp_img = pygame.image.load(self.resource_path("p1_feliz.png")).convert_alpha()

            ancho_deseado = 450 # Ajusta este número si lo quieres más grande o chico

           

            # Calculamos la proporción para que no se vea ancho

            ratio = ancho_deseado / temp_img.get_width()

            alto_proporcional = int(temp_img.get_height() * ratio)

           

            self.img_final = pygame.transform.scale(temp_img, (ancho_deseado, alto_proporcional))

        except:

            self.img_final = pygame.Surface((400, 600))

        try:

            temp_hablando = pygame.image.load(self.resource_path("p1_hablando.png")).convert_alpha()

            # Usamos el mismo ancho que definimos para la otra (450)

            ratio = 450 / temp_hablando.get_width()

            alto_prop = int(temp_hablando.get_height() * ratio)

            self.img_hablando = pygame.transform.scale(temp_hablando, (450, alto_prop))

        except:

            self.img_hablando = self.img_final # Respaldo por si falla





        # --- VARIABLES DE ESTADO ---

        self.estado = "MENU"

        self.volumen = 0.5

        self.sala_actual = 'nerissa1'

        self.angel_x, self.angel_y = 300, 200

        self.sprite_actual = "parado"

        self.dialogando = False

        self.dialogo_actual = []

        self.indice_texto = 0

        self.objetos_vistos = set()

        self.mostrando_carta = False

        self.mostrando_cuadro = False

        self.zoom_carta = 400

        self.vida = 100

        self.notas = []

        self.spawn_timer = 0

        self.video_cap = None

        self.listo_para_ritmo = False

        self.leyendo_carta_final = False

        self.last_frame = None



        # --- INICIAR MÓDULOS ---

        self.mod_aventura = Aventura(self)

        self.mod_ritmo = RitmoGame(self)



    def dibujar_menu(self):

        # 1. DIBUJAR EL FONDO PRIMERO (Ocupa toda la pantalla 800x600)

        self.screen.blit(self.img_menu, (0, 0))

       

        # 2. TÍTULO (Más abajo y con sombra real)

        fuente_tit = pygame.font.SysFont("Impact", 100) # Un poco más grande para que resalte

       

        # Renderizamos los textos

        titulo_sombra = fuente_tit.render("SAN VALENTÍN", True, (0, 0, 0))

        titulo_principal = fuente_tit.render("SAN VALENTÍN", True, (255, 105, 180))

       

        # Posición del título (bajado a Y=150 para que esté más centrado verticalmente)

        pos_x = 400 - titulo_principal.get_width() // 2

        pos_y = 150

       

        # Dibujamos sombra (un poco desplazada) y luego el texto rosa

        self.screen.blit(titulo_sombra, (pos_x + 5, pos_y + 5))

        self.screen.blit(titulo_principal, (pos_x, pos_y))

       

        # 3. BOTONES (Ubicados en el medio/bajo)

        ancho_b, alto_b = 280, 55 # Un poquito más grandes para que se vean pro

       

        # Centramos los rectángulos en X=400 y los bajamos en Y

        self.rect_jugar = pygame.Rect(400 - ancho_b//2, 330, ancho_b, alto_b)

        self.rect_config = pygame.Rect(400 - ancho_b//2, 400, ancho_b, alto_b)

        self.rect_salir = pygame.Rect(400 - ancho_b//2, 470, ancho_b, alto_b)



        botones = [

            (self.rect_jugar, "INICIAR"),

            (self.rect_config, f"SONIDO: {int(self.volumen * 100)}%"),

            (self.rect_salir, "SALIR")

        ]



        for r, texto in botones:

            # Dibujar el cuerpo del botón (Rosa con transparencia o sólido)

            pygame.draw.rect(self.screen, (255, 150, 180), r, border_radius=15)

            # Borde blanco grueso

            pygame.draw.rect(self.screen, (255, 255, 255), r, 3, border_radius=15)

           

            # Texto del botón

            fuente_btn = pygame.font.SysFont("Arial", 30, True)

            txt_surf = fuente_btn.render(texto, True, (255, 255, 255))

            self.screen.blit(txt_surf, (r.centerx - txt_surf.get_width()//2, r.centery - txt_surf.get_height()//2))

   

    def dibujar_burbuja(self, texto, pos):

        fuente = pygame.font.SysFont("Arial", 16, True)

        txt_surf = fuente.render(texto, True, (255, 255, 255))

        padding = 10

        rect_bg = pygame.Rect(pos[0]-5, pos[1]-5, txt_surf.get_width() + padding, 28)

        pygame.draw.rect(self.screen, (0, 0, 0), rect_bg)

        pygame.draw.rect(self.screen, (255, 215, 0), rect_bg, 2) # Borde dorado

        self.screen.blit(txt_surf, pos)



    def run(self):

        while True:

            dt = self.clock.tick(60)

            keys = pygame.key.get_pressed()



            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    if self.video_cap: self.video_cap.release()

                    pygame.quit(); sys.exit()

                if self.estado == "RITMO" and self.mod_ritmo.game_over:

                    if event.type == pygame.KEYDOWN:

                        # Aquí podrías detectar R o C también si quieres,

                        # pero ya lo hace ritmo.py

                        continue

                if self.estado == "RITMO" and self.mod_ritmo.stage_clear:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
            # 1. Liberamos el video y paramos música ANTES de cambiar
                            if self.video_cap:
                                self.video_cap.release()
                                self.video_cap = None
                            pygame.mixer.music.stop()
                            pygame.mixer.stop() # Para sonidos largos que hayan quedado

            # 2. Cambiamos el estado
                            self.estado = "FINAL"
                            self.dialogo_actual = [
                            "...", 
                            "¡Gracias por jugar un rato!", 
                            "Espero que te haya parecido lindo.", 
                            "No es mucho lo que hice...", 
                            "Aún así, mejoraré esto para la próxima.", 
                            "Espera atentamente...", 
                            "Y ten un bonito San Valentín.", 
                            "Te quiero mucho, muaaaa."
                        ]
                        self.indice_texto = 0
                        self.dialogando = True
            
            # IMPORTANTE: Desactivamos el flag para que no entre al siguiente IF
                        self.listo_para_ritmo = False 
                        continue

               

                # Dentro del loop de eventos en main.py

                if self.estado == "RITMO" and event.type == pygame.KEYDOWN:

                     # Si perdimos o si ganamos, ignoramos las flechas de ritmo

                    if self.mod_ritmo.game_over or self.mod_ritmo.stage_clear:

                        continue

                    teclas_juego = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]

                    for i, t in enumerate(teclas_juego):

                        if event.key == t:

                            for n in self.notas[:]:

                                # Si es el carril correcto, está en zona y NO es larga (las largas se sostienen)

                                if n.carril == i and 480 < n.y < 580 and n.activa:

                                    if not n.es_larga:

                                        self.mod_ritmo.combo += 1

                                        self.mod_ritmo.snd_corto.play()

                                        if n in self.notas: # <--- Añade esta línea de seguridad

                                            self.notas.remove(n)

                                        self.mod_ritmo.puntos += 100

                                        self.vida = min(100, self.vida + 5) # Te da vida al acertar

                                        # Si es larga, la lógica de sostener ya está en ritmo.py



                # Mouse e Interacciones

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.estado == "MENU":

                        if self.rect_jugar.collidepoint(event.pos):

                            self.estado = "AVENTURA"

                       

                        elif self.rect_config.collidepoint(event.pos):

                            # Ciclo de volumen: 0.0 -> 0.5 -> 1.0 -> 0.0

                            self.volumen = (self.volumen + 0.5) if self.volumen < 1.0 else 0.0

                            pygame.mixer.music.set_volume(self.volumen)

                            # También ajustamos los efectos de Ritmo

                            self.mod_ritmo.snd_corto.set_volume(self.volumen)

                            self.mod_ritmo.snd_largo.set_volume(self.volumen)

                       

                        elif self.rect_salir.collidepoint(event.pos):

                            pygame.quit(); sys.exit()

                   

                    elif self.estado == "FINAL": # Añadimos esta condición clara

                        self.indice_texto += 1

                    elif self.mostrando_cuadro:

                        self.mostrando_cuadro = False

                    elif self.mostrando_carta:

                        self.mostrando_carta = False

                        self.listo_para_ritmo = True

                        self.dialogo_actual = ["¿Viste todo?", "Son algunos recuerdos del pasado", "Cosas que me gustan", "Y te gustan a ti", "Como sea", "Presiona ENTER para seguir o click para volver"]

                        self.indice_texto = 0; self.dialogando = True

                    elif self.dialogando:

                        self.indice_texto += 1

                        if self.indice_texto >= len(self.dialogo_actual):

                            self.dialogando = False

                            if self.leyendo_carta_final:

                                self.mostrando_carta = True

                                self.leyendo_carta_final = False

                    elif self.sala_actual == 'cocina' and not self.dialogando:

                        for nombre, pos in self.pos_dibujo.items():

                            rect_obj = pygame.Rect(pos[0]-20, pos[1]-20, 80, 80)

                            if rect_obj.collidepoint(event.pos):

                                # Lógica especial Radio

                                if nombre == "radio":

                                    pygame.mixer.music.load(self.resource_path("alma dinamita - wos (letra) (mp3cut.net).mp3"))
                                    pygame.mixer.music.play()

                                    self.objetos_vistos.add("radio")

                               

                                # Lógica especial Carta

                                if nombre == "carta":

                                    reales = [v for v in self.objetos_vistos if v != "carta"]

                                    if len(reales) >= 7: # Son 7: taza, cuadro, gardenia, cheesecake, calendario, radio, cinnamoroll

                                        self.dialogo_actual = self.mod_aventura.textos_data["carta"]

                                        self.leyendo_carta_final = True

                                    else:

                                        faltan = 7 - len(reales)

                                        self.dialogo_actual = [f"Aún no puedo leerla...", f"Siento que me faltan {faltan} recuerdos por encontrar."]

                                else:

                                    if nombre == "cuadro": self.mostrando_cuadro = True

                                    self.objetos_vistos.add(nombre)

                                    self.dialogo_actual = self.mod_aventura.textos_data[nombre]

                               

                                self.indice_texto = 0

                                self.dialogando = True

                                break



                # ENTER para iniciar minijuego

                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.listo_para_ritmo:

                    self.estado = "RITMO"

                    self.last_frame = None

                    self.spawn_timer = 0 # <--- Asegúrate de que esto esté en 0

                    self.video_cap = cv2.VideoCapture(self.resource_path("nerissasboda.mp4"))
                    pygame.mixer.music.load(self.resource_path("audionerissa.mp3"))

                    pygame.mixer.music.play()



            # --- ACTUALIZAR ZOOM (FLECHAS) ---

            if self.mostrando_carta:

                if keys[pygame.K_UP]: self.zoom_carta = min(850, self.zoom_carta + 7)

                if keys[pygame.K_DOWN]: self.zoom_carta = max(200, self.zoom_carta - 7)



            # --- DIBUJO ---

            if self.estado == "MENU":

                self.dibujar_menu()

           

            elif self.estado == "AVENTURA":

                self.mod_aventura.actualizar()

               

                # 1. Fondo

                self.screen.blit(self.bg_nerissa if self.sala_actual == 'nerissa1' else self.bg_cocina, (0,0))

               

                # 2. Objetos de la cocina

                if self.sala_actual == 'cocina':

                    for n, p in self.pos_dibujo.items():

                        self.screen.blit(self.obj_imgs[n], p)

               

                # 3. Personaje

                self.screen.blit(self.sprites.get(self.sprite_actual, self.sprites["parado"]), (self.angel_x, self.angel_y))

               

                # 4. OVERLAYS (Cuadro y Carta) - Van debajo del diálogo

                if self.mostrando_cuadro:

                    # Lo centramos un poco más arriba para que no choque con el texto

                    self.screen.blit(self.img_cuadro_grande, (175, 40))

               

                if self.mostrando_carta:

                    overlay = pygame.Surface((800, 600), pygame.SRCALPHA)

                    overlay.fill((0, 0, 0, 210))

                    self.screen.blit(overlay, (0, 0))

                    w, h = self.img_carta_full.get_size()

                    alto = int(self.zoom_carta * (h / w))

                    img_scaled = pygame.transform.scale(self.img_carta_full, (self.zoom_carta, alto))

                    self.screen.blit(img_scaled, img_scaled.get_rect(center=(400, 300)))

                    self.dibujar_burbuja("FLECHAS ↑ ↓ PARA ZOOM / CLICK PARA CERRAR", (230, 40))



                # 5. INTERFAZ (Diálogos y Burbujas [E]) - SIEMPRE AL FINAL

                self.mod_aventura.dibujar_interfaz()



            elif self.estado == "RITMO":

                self.mod_ritmo.loop()



            elif self.estado == "FINAL":

                self.dibujar_final()



            pygame.display.flip()



    def dibujar_final(self):

        # 1. Limpieza de video si aún existe
        if self.video_cap:
            self.video_cap.release()
            self.video_cap = None
        
        self.screen.fill((0, 0, 0))

        # 2. Dibujar personaje
        img_a_mostrar = self.img_final if self.indice_texto == 0 else self.img_hablando
        pos_y = (600 - img_a_mostrar.get_height()) + 150
        self.screen.blit(img_a_mostrar, (400 - img_a_mostrar.get_width()//2, pos_y))

        # 3. Caja de diálogo
        caja = pygame.Surface((700, 150), pygame.SRCALPHA)
        caja.fill((255, 182, 193, 128))
        self.screen.blit(caja, (50, 420))
        pygame.draw.rect(self.screen, (255, 255, 255), (50, 420, 700, 150), 2, border_radius=10)

        fuente = pygame.font.SysFont("Arial", 28, True)
        
        # --- CAMBIO AQUÍ: Verificamos el índice correctamente ---
        if self.indice_texto < len(self.dialogo_actual):
            txt = self.dialogo_actual[self.indice_texto]
            t_surf = fuente.render(txt, True, (255, 255, 255))
            self.screen.blit(t_surf, (80, 460))
            self.dibujar_burbuja("CLICK PARA CONTINUAR", (550, 390))
        else:
            # En lugar de cerrar aquí, podrías mostrar un mensaje final 
            # o esperar el clic final en el loop de eventos.
            pygame.quit()
            sys.exit()

       

        self.dibujar_burbuja("CLICK PARA CONTINUAR", (550, 390))



if __name__ == "__main__":

    Game().run()