import pygame
import math

# Constantes
sz = 30
width, height = 800, 600
cols, rows = width // sz, height // sz
charges = []
K = 1000
running = False
magField = [[0] * cols for _ in range(rows)]

pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

holding_alt = False


class Charge:
    def __init__(self, x, y, charge, lazy):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2()
        self.acc = pygame.Vector2()
        self.charge = charge
        self.lazy = lazy
        self.position_history = [] 

    def apply_force(self, force):
        self.acc += force

    def field_line(self, x, y):
        disp = pygame.Vector2(x, y) - self.pos
        dist_sq = disp.length_squared()

    # Verificar si dist_sq es diferente de cero antes de la división
        if dist_sq != 0:
            disp.scale_to_length(K * self.charge / dist_sq)
        else:
        # Si dist_sq es cero, establecer disp en (0, 0) o algún otro valor apropiado
            disp = pygame.Vector2()

        return disp

    def update(self):
        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

    def render(self):
        c = abs(self.charge) * 10 if self.charge else 10
        l = self.charge * 7 if self.charge else 7
        if self.charge > 0:
            pygame.draw.circle(screen, (255, 0, 0), (int(self.pos.x), int(self.pos.y)), int(c))
            pygame.draw.line(screen, (255, 255, 255), (self.pos.x - l, self.pos.y),
                             (self.pos.x + l, self.pos.y), 2)
            pygame.draw.line(screen, (255, 255, 255), (self.pos.x, self.pos.y - l),
                             (self.pos.x, self.pos.y + l), 2)
        elif self.charge < 0:
            pygame.draw.circle(screen, (128, 0, 128), (int(self.pos.x), int(self.pos.y)), int(c))
            pygame.draw.line(screen, (255, 255, 255), (self.pos.x - l, self.pos.y),
                            (self.pos.x + l, self.pos.y), 2)

        
    def update(self):
        self.vel += self.acc
        self.pos += self.vel
        self.acc *= 0

        # Ajusta la velocidad al alcanzar los bordes
        if self.pos.x < 0:
            self.pos.x = 0
            self.vel.x *= -1
        elif self.pos.x > width:
            self.pos.x = width
            self.vel.x *= -1

        if self.pos.y < 0:
            self.pos.y = 0
            self.vel.y *= -1
        elif self.pos.y > height:
            self.pos.y = height
            self.vel.y *= -1


def main():
    global running, holding_alt

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    charges.append(Charge(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], 1, holding_alt))
                elif event.key == pygame.K_2:
                    charges.append(Charge(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], -1, holding_alt))
                elif event.key == pygame.K_RETURN:
                    running = not running
                elif event.key == pygame.K_LALT:
                    holding_alt = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LALT:
                    holding_alt = False

        screen.fill((255, 255, 255))

        for j in range(rows):
            for i in range(cols):
                x, y = i * sz + sz / 2, j * sz + sz / 2
                pygame.draw.rect(screen, (255, 255, 255), (i * sz, j * sz, sz, sz), 1)
                field_sum = pygame.Vector2()

                for c in charges:
                    field_line = c.field_line(x, y)
                    field_sum += field_line

                if magField[j][i] == 1:
                    pygame.draw.rect(screen, (0, 255, 255), (i * sz, j * sz, sz, sz))
                elif magField[j][i] == 2:
                    pygame.draw.rect(screen, (255, 0, 255), (i * sz, j * sz, sz, sz))

                if field_sum.length() > 0:
                    field_sum *= 100
                    field_sum.scale_to_length(15)
                    pygame.draw.line(screen, (0, 204, 0), (x, y), (x + field_sum.x, y + field_sum.y))
                pygame.draw.circle(screen, (0, 0, 0), (int(x), int(y)), 4)

        if running:
            for a in charges:
                for b in charges:
                    if a != b:
                        field_line = a.field_line(b.pos.x, b.pos.y)
                        field_line *= b.charge
                        b.apply_force(field_line)

                        # Verificar colisión y crear carga neutra
                        if a.charge * b.charge < 0:
                            distance = math.sqrt((a.pos.x - b.pos.x)**2 + (a.pos.y - b.pos.y)**2)
                            if distance < abs(a.charge) * 10 + abs(b.charge) * 10:  # Suma de los radios

                                # Eliminar cargas originales
                                charges.remove(a)
                                charges.remove(b)

            for c in charges:
                i = int(pygame.math.lerp(0, cols, c.pos.x / width))
                j = int(pygame.math.lerp(0, rows, c.pos.y / height))

                if 0 <= i < cols and 0 <= j < rows:
                    if magField[j][i] == 1:
                        c.vel.rotate(math.radians(3) * c.charge)
                    elif magField[j][i] == 2:
                        c.vel.rotate(-math.radians(3) * c.charge)

        for c in charges:
            if running and not c.lazy:
                c.update()
                c.position_history.append((c.pos.x, c.pos.y))
            c.render()

        pygame.display.flip()
        clock.tick(60)
        #for c in charges:
           # print(c.position_history)





if __name__ == "__main__":
    main()