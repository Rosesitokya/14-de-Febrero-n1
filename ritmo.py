import pygame
import cv2
import random

class Nota:
    def __init__(self, carril, es_larga=False):
        self.carril = carril
        self.x = 200 + (carril * 100)
        self.y = -100
        self.vel = 8 
        self.es_larga = es_larga
        self.largo = random.randint(300, 500) if es_larga else 35
        self.activa = True
        self.fallada = False 
        self.game_over = False
        self.sostenida = False 
        self.canal_largo = None
        try:
            self.img_mal = pygame.image.load(self.game.resource_path("mal.png")).convert_alpha()
        except Exception as e:
            self.img_mal = pygame.Surface((50, 50))

    def caer(self):
        self.y += self.vel

    def dibujar(self, pantalla, color_base):
        color = (130, 130, 130) if self.fallada else color_base
        if self.es_larga:
            # Dibujamos el cuerpo hacia arriba desde la posición Y
            s = pygame.Surface((70, max(0, self.largo)), pygame.SRCALPHA)
            alpha = 70 if self.fallada else 200
            s.fill((color[0], color[1], color[2], alpha))
            pantalla.blit(s, (self.x + 10, self.y - self.largo))
        
        pygame.draw.rect(pantalla, color, (self.x, self.y, 90, 30), border_radius=5)
        pygame.draw.rect(pantalla, (255, 255, 255), (self.x, self.y, 90, 30), 1, border_radius=5)

class RitmoGame:
    def __init__(self, game):
        self.game = game
        self.mascota_actual = pygame.Surface((100, 100)) # Un cuadradito invisible por si falla lo demás
        self.ultimo_combo_cambio = 0
        self.rosa_pastel = (255, 182, 193)
        self.azul_pastel = (173, 216, 230)
        self.colores = [self.rosa_pastel, self.azul_pastel, self.rosa_pastel, self.azul_pastel]
        self.fps_video = 23.98
        self.puntos = 0
        self.combo = 0
        self.game_over = False
        self.intervalo_spawn = 18 
        self.snd_corto = pygame.mixer.Sound(self.game.resource_path("notacorta.mp3"))
        self.snd_largo = pygame.mixer.Sound(self.game.resource_path("notalarga.mp3"))
        self.snd_corto.set_volume(0.8)
        self.snd_largo.set_volume(0.8)
        self.max_tiempo_alcanzado = False
        self.max_combo = 0
        self.stage_clear = False
        try:
            self.img_bien = pygame.image.load(self.game.resource_path("bien.png")).convert_alpha()
            self.img_bien = pygame.transform.scale(self.img_bien, (200, 200))
        except:
            self.img_bien = pygame.Surface((200, 200)) # Respaldo
        # AÑADE ESTO AQUÍ:
        try:
            self.img_mal = pygame.image.load(self.game.resource_path("mal.png")).convert_alpha()
            self.img_mal = pygame.transform.scale(self.img_mal, (200, 200))
            nombres = ["normalri.png", "normal2ri.png", "normal3ri.png", "normal4ri.png"]
            self.imgs_combo = [pygame.image.load(self.game.resource_path(n)).convert_alpha() for n in nombres]
            self.imgs_combo = [pygame.transform.scale(img, (120, 120)) for img in self.imgs_combo]
            self.mascota_actual = self.imgs_combo[0]
        except Exception as e:
            print(f"Error cargando imágenes en ritmo: {e}")
            self.img_mal = pygame.Surface((200, 200))
            self.imgs_combo = [pygame.Surface((120, 120))]
            self.mascota_actual = self.imgs_combo[0]

    def loop(self):
        keys = pygame.key.get_pressed()
        teclas = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
        tiempo_actual_ms = pygame.mixer.music.get_pos()
        tiempo_dejar_de_spawnear = 240000 # 4:00 - Ya no nacen notas
        tiempo_limpieza_total = 245000   # 4:05 - Se borra la interfaz

        if self.game.video_cap and tiempo_actual_ms >= 0:
            frame_objetivo = int((tiempo_actual_ms / 1000.0) * self.fps_video)
            self.game.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_objetivo)
            ret, frame = self.game.video_cap.read()
            if ret:
                frame = cv2.resize(frame, (800, 600))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.game.last_frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            else:
                self.finalizar_ritmo()

        if self.game.last_frame:
            self.game.screen.blit(self.game.last_frame, (0, 0))
            overlay = pygame.Surface((800,600), pygame.SRCALPHA); overlay.fill((0,0,0,175))
            self.game.screen.blit(overlay, (0,0))
        
        if self.stage_clear:
            self.dibujar_clear()

        if self.game_over:
            if self.game.last_frame:
                self.game.screen.blit(self.game.last_frame, (0, 0))
            # PASAMOS LAS VARIABLES REALES EN VEZ DE NONE
            self.dibujar_interfaz(keys, teclas) 
            return

        # --- CORTE RADICAL EN 4:05 ---
        if tiempo_actual_ms >= tiempo_limpieza_total or tiempo_actual_ms == -1:
            if not self.game_over: # Solo si no perdimos antes
                self.stage_clear = True 
                pygame.mixer.music.stop()
                return

        # --- GENERACIÓN DE NOTAS (Con stop en 4:00) ---
        keys = pygame.key.get_pressed()
        teclas = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
        
        if tiempo_actual_ms >= tiempo_dejar_de_spawnear:
            self.max_tiempo_alcanzado = True

        # Solo nacen nuevas si no hemos llegado al 4:00
        if tiempo_actual_ms < tiempo_dejar_de_spawnear:
            self.game.spawn_timer += 1
            if self.game.spawn_timer > self.intervalo_spawn:
                carril = random.randint(0, 3)
                if all(abs(n.y - (-100)) > 250 for n in self.game.notas if n.carril == carril):
                    self.game.notas.append(Nota(carril, random.random() < 0.35))
                    self.game.spawn_timer = 0

        # --- LÓGICA DE PROCESAMIENTO Y ARREGLO DE AUDIO ---
        for n in self.game.notas[:]:
            n.caer()
            n.dibujar(self.game.screen, self.colores[n.carril])

            # FALLO POR POSICIÓN
            if n.y > 620 and n.activa and not n.sostenida:
                n.activa, n.fallada = False, True
                self.game.vida -= 15
                self.combo = 0 
                if n.es_larga and n.canal_largo: n.canal_largo.stop()

            # LÓGICA NOTA LARGA
            if n.es_larga and n.activa:
                if 480 < n.y < 600 and keys[teclas[n.carril]]:
                    if not n.sostenida:
                        n.sostenida = True
                        n.canal_largo = self.snd_largo.play(-1)
                
                if n.sostenida:
                    if not keys[teclas[n.carril]] or n.largo <= 0:
                        if n.canal_largo: n.canal_largo.stop()
                        n.sostenida = False
                        if n.largo < 80: 
                            if n in self.game.notas: self.game.notas.remove(n)
                            self.combo += 1 
                            if self.combo > self.max_combo: self.max_combo = self.combo
                        else:
                            # Si soltó demasiado pronto, ahí sí falla
                            n.activa, n.fallada = False, True
                            self.combo = 0 
                    
                    elif n.largo <= 0: # Si la nota se acaba mientras presiona
                        if n.canal_largo: n.canal_largo.stop()
                        n.sostenida = False
                        if n in self.game.notas: self.game.notas.remove(n)
                        self.combo += 1
                    else:
                        # Sigue presionando normalmente
                        n.largo -= 12 
                        self.puntos += 2
                        self.game.vida = min(100, self.game.vida + 0.6)
                        pygame.draw.circle(self.game.screen, (255, 255, 255), (n.x + 45, 540), 50, 2)

            # SEGURO PARA EL BORRADO FINAL
            if n.y > 750: 
                if n.es_larga and n.canal_largo: n.canal_largo.stop()
                if n in self.game.notas: # <--- Este es el seguro clave
                    self.game.notas.remove(n)

        self.dibujar_interfaz(keys, teclas)

    def dibujar_interfaz(self, keys, teclas):
        letras = ["D", "F", "J", "K"]
        
        if self.combo >= 3:
            if hasattr(self, 'imgs_combo') and self.combo != self.ultimo_combo_cambio:
                self.mascota_actual = random.choice(self.imgs_combo)
                self.ultimo_combo_cambio = self.combo

            f_combo = pygame.font.SysFont("Impact", 60)
            c_surf = f_combo.render(f"{self.combo}", True, (255, 255, 255))
            t_surf = pygame.font.SysFont("Arial", 25, True).render("COMBO", True, (255, 255, 255))
            self.game.screen.blit(c_surf, (50, 250))
            self.game.screen.blit(t_surf, (45, 310))
            if self.mascota_actual:
                self.game.screen.blit(self.mascota_actual, (20, 320))
        else:
            self.ultimo_combo_cambio = 0
            
            
        # SCORE BLANCO
        f_puntos = pygame.font.SysFont("Impact", 45)
        p_surf = f_puntos.render(f"SCORE: {self.puntos}", True, (255, 255, 255))
        self.game.screen.blit(p_surf, (520, 30))

        # TECLAS CON LETRAS
        for i in range(4):
            x = 200 + (i * 100)
            color_c = self.colores[i] if keys[teclas[i]] else (255, 255, 255)
            pygame.draw.circle(self.game.screen, color_c, (x + 45, 540), 40, 3)
            
            f_letra = pygame.font.SysFont("Arial", 28, True)
            l_surf = f_letra.render(letras[i], True, (255, 255, 255))
            self.game.screen.blit(l_surf, (x + 35, 525))

        # VIDA CON FONDO GRIS
        pygame.draw.rect(self.game.screen, (80, 80, 80), (760, 150, 15, 300))
        v_h = int(self.game.vida * 3)

        if not self.game_over:
            pygame.draw.rect(self.game.screen, (80, 80, 80), (760, 150, 15, 300))
            v_h = int(self.game.vida * 3)
            if self.game.vida > 0:
                pygame.draw.rect(self.game.screen, (0, 255, 127), (760, 450 - v_h, 15, v_h))
        
        # --- ACTIVACIÓN Y DIBUJO DE GAME OVER ---
        if self.game.vida <= 0:
            self.game_over = True # <--- Esto activará el 'return' del loop arriba
            pygame.mixer.music.pause()
            
            # Detenemos sonidos de notas largas si quedaron sonando
            for n in self.game.notas:
                if n.es_larga and n.canal_largo:
                    n.canal_largo.stop()

            # Fondo oscuro
            if self.game.vida <= 0:
                self.game_over = True
                pygame.mixer.music.pause()
            
            # Fondo oscuro
                s = pygame.Surface((800, 600), pygame.SRCALPHA)
                s.fill((0, 0, 0, 180)) 
                self.game.screen.blit(s, (0, 0))

            # Texto GAME OVER blanco
                f_tit = pygame.font.SysFont("Impact", 90)
                t_surf = f_tit.render("GAME OVER", True, (255, 255, 255))
                self.game.screen.blit(t_surf, (400 - t_surf.get_width()//2, 120))

            # Botón Reintentar (Rosa)
                rect_r = pygame.Rect(250, 280, 300, 60)
                pygame.draw.rect(self.game.screen, self.rosa_pastel, rect_r, border_radius=15)
                self.game.screen.blit(pygame.font.SysFont("Arial", 30, True).render("REINTENTAR (R)", True, (255, 255, 255)), (295, 295))

            # Botón Cocina (Azul)
                rect_c = pygame.Rect(250, 370, 300, 60)
                pygame.draw.rect(self.game.screen, self.azul_pastel, rect_c, border_radius=15)
                self.game.screen.blit(pygame.font.SysFont("Arial", 30, True).render("COCINA (C)", True, (255, 255, 255)), (335, 385))

            # Muñequito triste a la izquierda
                self.game.screen.blit(self.img_mal, (1, 400))

                k = pygame.key.get_pressed()
                if k[pygame.K_r]: 
                    self.reiniciar_todo()
                if k[pygame.K_c]: 
                    self.finalizar_ritmo()

    def reiniciar_todo(self):
        self.game.vida = 100
        self.puntos = 0
        self.combo = 0
        self.game.notas = []
        self.game_over = False
        self.max_tiempo_alcanzado = False
        pygame.mixer.music.play()
        if self.game.video_cap:
            self.game.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def finalizar_ritmo(self):
        pygame.mixer.stop()
        self.game.estado = "AVENTURA"
        self.game.vida, self.game.notas = 100, []
        pygame.mixer.music.stop()
        if self.game.video_cap: self.game.video_cap.release(); self.game.video_cap = None

    def dibujar_clear(self):
        # 1. Fondo oscuro
        s = pygame.Surface((800, 600), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180)) 
        self.game.screen.blit(s, (0, 0))

        # 2. Título CLEAR!
        f_tit = pygame.font.SysFont("Impact", 100)
        t_surf = f_tit.render("STAGE CLEAR!", True, (255, 255, 255))
        self.game.screen.blit(t_surf, (400 - t_surf.get_width()//2, 80))

        # 3. Stats (Puntaje y Max Combo)
        f_stats = pygame.font.SysFont("Arial", 35, True)
        txt_puntos = f_stats.render(f"PUNTUACIÓN TOTAL: {self.puntos}", True, (255, 255, 255))
        txt_combo = f_stats.render(f"COMBO MÁXIMO: {self.max_combo}", True, (255, 255, 255))
        
        self.game.screen.blit(txt_puntos, (400 - txt_puntos.get_width()//2, 200))
        self.game.screen.blit(txt_combo, (400 - txt_combo.get_width()//2, 250))

        # 4. Botones
        f_btn = pygame.font.SysFont("Arial", 30, True)
        # Botón Continuar (Rosa)
        rect_cont = pygame.Rect(250, 330, 300, 60)
        pygame.draw.rect(self.game.screen, self.rosa_pastel, rect_cont, border_radius=15)
        self.game.screen.blit(f_btn.render("CONTINUAR (Enter)", True, (255, 255, 255)), (285, 345))

        # Botón Salir (Azul)
        rect_salir = pygame.Rect(250, 420, 300, 60)
        pygame.draw.rect(self.game.screen, self.azul_pastel, rect_salir, border_radius=15)
        self.game.screen.blit(f_btn.render("SALIR (Esc)", True, (255, 255, 255)), (330, 435))

        # 5. Muñequito "bien" abajo a la izquierda
        self.game.screen.blit(self.img_bien, (0, 400))
