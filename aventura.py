import pygame

class Aventura:
    def __init__(self, game):
        self.game = game
        # Diálogos originales restaurados
        self.textos_data = {
            "gardenia": ["...Una gardenia blanca", "Antes, la dejaban en el umbral...", "de quienes amaban en silencio", "Eres precioso/a sin saberlo, eso decían"],
            "cheesecake": ["...¿Un cheesecake?", "Dicen que hacer cheesecake es tardado.", "Necesita muchas horas para asentarse", "Para volverse suave sin perder firmeza", "Me dijiste que te gustaban, ¿no?"],
            "calendario": ["...Ya es febrero.", "El 14.", "Día del amor y la amistad."],
            "radio": ["...Esa canción.", "¿Aún recuerdas cuando te dije que me gustaba?", "Hehe"],
            "cinnamoroll": ["¿Qué es esto?", "Es el peluche favorito de Rose."],
            "carta": ["Una carta...", "Parece que es el momento de leerla..."],
            "taza": ["Una taza de café caliente.", "Aún sale humo.", "Quisiera tener una taza compartida con alguien."],
            "cuadro": ["Es un cuadro muy bonito.", "Es un dibujo que hizo Rose."]
        }

    def actualizar(self):
        # Bloquear movimiento si hay interfaces abiertas
        if self.game.mostrando_carta or self.game.mostrando_cuadro or self.game.dialogando:
            return

        keys = pygame.key.get_pressed()
        moviendo = False
        vel = 5
        
        # Movimiento y selección de sprites
        if keys[pygame.K_w]: 
            self.game.angel_y -= vel
            self.game.sprite_actual = "piernaizatras"
            moviendo = True
        elif keys[pygame.K_s]: 
            self.game.angel_y += vel
            self.game.sprite_actual = "piernaiz"
            moviendo = True
        elif keys[pygame.K_a]: 
            self.game.angel_x -= vel
            self.game.sprite_actual = "caminaizquierda"
            moviendo = True
        elif keys[pygame.K_d]: 
            self.game.angel_x += vel
            self.game.sprite_actual = "caminaderecha"
            moviendo = True

        if not moviendo:
            if "atras" in self.game.sprite_actual: self.game.sprite_actual = "paradoatras"
            elif "izquierda" in self.game.sprite_actual: self.game.sprite_actual = "paradoizquierda"
            elif "derecha" in self.game.sprite_actual: self.game.sprite_actual = "paradoderecha"
            else: self.game.sprite_actual = "parado"

        # --- LÓGICA DE COLISIONES (CÓDIGO ORIGINAL) ---
        if self.game.sala_actual == 'nerissa1':
            self.game.angel_x = max(50, min(self.game.angel_x, 720))
            self.game.angel_y = max(110, min(self.game.angel_y, 310))
            # Cambio de sala a Cocina
            if self.game.angel_x >= 690 and keys[pygame.K_e]:
                self.game.sala_actual = 'cocina'
                self.game.angel_x = 110
                self.game.angel_y = 200
        else: 
            # COCINA
            # Pared derecha invisible (620) para no pisar la mesa de la carta
            self.game.angel_x = max(40, min(self.game.angel_x, 620))
            
            # Límite vertical según la encimera (Escalón original)
            if self.game.angel_x > 380:
                lim_inf = 320 # Zona derecha despejada
            else:
                lim_inf = 180 # Zona izquierda (choca con muebles abajo)
            
            # Límite superior para no salirse del fondo
            lim_sup = 70
            
            self.game.angel_y = max(lim_sup, min(self.game.angel_y, lim_inf))

            # Salida de la cocina a la habitación
            if self.game.angel_x <= 90 and keys[pygame.K_e]:
                self.game.sala_actual = 'nerissa1'
                self.game.angel_x = 680
                self.game.angel_y = 250

    def dibujar_interfaz(self):
        # Burbujas de interacción [E]
        if self.game.sala_actual == 'nerissa1' and self.game.angel_x >= 670:
            self.game.dibujar_burbuja("COCINA [E]", (self.game.angel_x - 30, self.game.angel_y - 40))
        if self.game.sala_actual == 'cocina' and self.game.angel_x <= 110:
            self.game.dibujar_burbuja("VOLVER [E]", (self.game.angel_x - 30, self.game.angel_y - 40))

        # Cuadro de diálogo con la CARA
        if self.game.dialogando:
            # Fondo
            pygame.draw.rect(self.game.screen, (10, 10, 10), (50, 420, 700, 150))
            pygame.draw.rect(self.game.screen, (255, 255, 255), (50, 420, 700, 150), 2)
            
            # Cabeza del personaje (Sprite p1_normal)
            if "p1_normal" in self.game.sprites:
                face = pygame.transform.scale(self.game.sprites["p1_normal"], (120, 120))
                self.game.screen.blit(face, (70, 435))
            
            # Texto
            fuente = pygame.font.SysFont("Arial", 22)
            try:
                linea_texto = self.game.dialogo_actual[self.game.indice_texto]
                txt_surf = fuente.render(linea_texto, True, (255, 255, 255))
                self.game.screen.blit(txt_surf, (210, 465))
            except (IndexError, AttributeError):
                pass