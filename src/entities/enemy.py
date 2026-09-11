"""Animated enemy and elite hero models."""

import itertools, math, pygame
from .. import settings

_id_counter = itertools.count()

class Enemy:
    def __init__(self, x, y, audio, effects, variant="guard"):
        self.id = next(_id_counter); self.x = float(x); self.y = float(y)
        self.width = settings.ENEMY_WIDTH; self.height = settings.ENEMY_HEIGHT
        self.variant = "elite" if variant == "guard" and x >= 900 else variant
        self.health = settings.ENEMY_MAX_HEALTH * (2 if self.variant == "elite" else 1)
        self.max_health = self.health
        self.alert = False; self.dead = False; self.death_timer = 30
        self.attack_windup = 0; self.attack_cooldown = 0; self.anim_time = 0.0
        self.audio = audio; self.effects = effects

    @property
    def rect(self): return pygame.Rect(int(self.x-self.width/2),int(self.y-self.height),self.width,self.height)
    @property
    def fully_gone(self): return self.dead and self.death_timer <= 0

    def update(self, player):
        if self.dead: self.death_timer -= 1; return
        self.anim_time += 0.15; distance=abs(player.x-self.x); was_alert=self.alert
        if not player.hidden and distance < settings.ENEMY_DETECTION_RANGE: self.alert=True
        if self.alert and not was_alert: self.audio.play("alert")
        if not self.alert: return
        if self.attack_cooldown>0: self.attack_cooldown-=1
        if self.attack_windup>0:
            self.attack_windup-=1
            if self.attack_windup==0: self._resolve_attack(player)
            return
        if distance<=settings.ENEMY_ATTACK_RANGE:
            if self.attack_cooldown==0: self.attack_windup=settings.ENEMY_ATTACK_WINDUP; self.attack_cooldown=settings.ENEMY_ATTACK_COOLDOWN
        else: self.x += settings.ENEMY_SPEED if player.x>self.x else -settings.ENEMY_SPEED

    def _resolve_attack(self, player):
        if abs(player.x-self.x)<=settings.ENEMY_ATTACK_RANGE+15 and player.alive:
            player.take_damage(settings.ENEMY_ATTACK_DAMAGE); self.audio.play("enemy_attack")

    def take_damage(self, amount, hit_x=None, hit_y=None):
        if self.dead: return
        self.health-=amount
        if hit_x is not None: self.effects.hit_sparks(hit_x,hit_y)
        self.audio.play("hit")
        if self.health<=0: self.health=0; self.dead=True; self.death_timer=34

    def can_be_assassinated(self, player):
        return not self.dead and player.hidden and abs(self.x-player.x)<=settings.ASSASSINATION_RANGE and not self.alert

    def draw(self, surface):
        if self.fully_gone: return
        x,bottom=int(self.x),int(self.y)
        if self.dead: return self._draw_death_fade(surface,x,bottom)
        elite=self.variant=="elite"; base=(118,128,142) if not elite else (76,98,130); hi=(182,193,207) if not elite else (130,176,226)
        accent=settings.COLOR_ACCENT_RED if self.alert else ((168,88,112) if elite else (103,116,132)); dark=(9,13,20)
        stride=int(math.sin(self.anim_time)*4) if self.attack_windup==0 else 0; head,shoulder,hip=bottom-75,bottom-57,bottom-33
        shadow=pygame.Surface((100,34),pygame.SRCALPHA); pygame.draw.ellipse(shadow,(0,0,0,110),(6,10,88,18)); surface.blit(shadow,(x-50,bottom-8))
        cape=[(x-18,shoulder),(x+18,shoulder),(x+22,bottom-20),(x+8,bottom-15),(x-18,bottom-25)]; pygame.draw.polygon(surface,(20,26,36),cape)
        pygame.draw.circle(surface,dark,(x,head),17 if elite else 15)
        pygame.draw.polygon(surface,base,[(x-14,head+2),(x-8,head-15),(x+10,head-15),(x+15,head+3),(x+9,head+14),(x-10,head+14)])
        pygame.draw.line(surface,hi,(x-7,head-1),(x+10,head-3),3)
        if self.alert: pygame.draw.line(surface,settings.COLOR_ACCENT_RED,(x-3,head+5),(x+10,head+3),2)
        pygame.draw.polygon(surface,base,[(x-14,shoulder),(x+14,shoulder),(x+11,hip),(x-11,hip)]); pygame.draw.line(surface,hi,(x-9,shoulder+7),(x+9,shoulder+7),3); pygame.draw.circle(surface,accent,(x,shoulder+16),3)
        if self.attack_windup>0:
            pygame.draw.line(surface,hi,(x+8,shoulder+2),(x+27,shoulder-10),6); pygame.draw.line(surface,hi,(x-7,shoulder+4),(x-22,shoulder+15),5); pygame.draw.line(surface,(222,228,235),(x+27,shoulder-10),(x+51,shoulder-30),4)
        else:
            pygame.draw.line(surface,hi,(x-7,shoulder+3),(x-20,shoulder+17),5); pygame.draw.line(surface,hi,(x+7,shoulder+3),(x+20,shoulder+17),5)
        pygame.draw.line(surface,hi,(x-6,hip),(x-16+stride,bottom),6); pygame.draw.line(surface,hi,(x+6,hip),(x+16-stride,bottom),6)
        pygame.draw.line(surface,dark,(x-16+stride,bottom),(x-29+stride,bottom),7); pygame.draw.line(surface,dark,(x+16-stride,bottom),(x+29-stride,bottom),7)
        bw=58 if elite else 48; hp=int(bw*self.health/self.max_health); pygame.draw.rect(surface,settings.COLOR_PANEL,(x-bw//2,bottom-103,bw,6),border_radius=3); pygame.draw.rect(surface,settings.COLOR_ACCENT_RED if self.alert else hi,(x-bw//2,bottom-103,hp,6),border_radius=3)
        if elite: pygame.draw.circle(surface,settings.COLOR_GOLD,(x,bottom-113),4)
        if self.alert: pygame.draw.circle(surface,settings.COLOR_ACCENT_RED,(x,bottom-116),4)

    def _draw_death_fade(self,surface,x,bottom):
        t=self.death_timer/34; alpha=max(0,int(255*t)); drop=int((1-t)*20); ghost=pygame.Surface((110,120),pygame.SRCALPHA); color=(*settings.COLOR_ENEMY_IDLE,alpha); cx,cy=55,55+drop
        pygame.draw.circle(ghost,color,(cx,cy-25),15,3); pygame.draw.line(ghost,color,(cx,cy-10),(cx,cy+25),5); pygame.draw.line(ghost,color,(cx,cy+25),(cx-22,cy+55),5); pygame.draw.line(ghost,color,(cx,cy+25),(cx+22,cy+55),5); pygame.draw.line(ghost,(*settings.COLOR_ACCENT_RED,alpha),(cx,cy+5),(cx+35,cy-25),3); surface.blit(ghost,(x-55,bottom-110))
