"""Particles, weapon trails, hit sparks and cinematic screen shake."""

import random, math, pygame
from . import settings

class Particle:
    __slots__ = ("x","y","vx","vy","life","max_life","color","size","shrink")
    def __init__(self,x,y,vx,vy,life,color,size=3,shrink=True):
        self.x=x; self.y=y; self.vx=vx; self.vy=vy; self.life=life; self.max_life=life; self.color=color; self.size=size; self.shrink=shrink
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=settings.PARTICLE_GRAVITY; self.life-=1
    @property
    def alive(self): return self.life>0
    def draw(self,surface):
        t=self.life/self.max_life; size=max(1,int(self.size*t)) if self.shrink else self.size; alpha=max(0,min(255,int(255*t)))
        glow=pygame.Surface((size*4,size*4),pygame.SRCALPHA); pygame.draw.circle(glow,(*self.color,max(0,alpha//5)),(size*2,size*2),size*2); pygame.draw.circle(glow,(*self.color,alpha),(size*2,size*2),size); surface.blit(glow,(self.x-size*2,self.y-size*2))

class EffectsManager:
    def __init__(self): self.particles=[]; self.slashes=[]; self._shake_timer=0; self._shake_strength=0
    def shake(self,strength,duration=10): self._shake_strength=max(self._shake_strength,strength); self._shake_timer=max(self._shake_timer,duration)
    def get_shake_offset(self):
        if self._shake_timer<=0: return 0,0
        m=self._shake_strength*(self._shake_timer/10); return random.randint(-int(m),int(m)),random.randint(-int(m),int(m))
    def _burst(self,x,y,count,color,speed_min,speed_max,life_min,life_max,size):
        for _ in range(count):
            a=random.uniform(0,math.tau); speed=random.uniform(speed_min,speed_max)
            self.particles.append(Particle(x,y,math.cos(a)*speed,math.sin(a)*speed,random.randint(life_min,life_max),color,size))
    def slash_effect(self,x,y,facing):
        self._burst(x,y,18,settings.COLOR_TEXT,4,9,8,16,3)
        self.slashes.append([x,y,facing,0])
        self.shake(2,5)
    def hit_sparks(self,x,y):
        self._burst(x,y,20,settings.COLOR_ACCENT_RED,2,8,10,22,4); self.shake(settings.SHAKE_ON_HIT,9)
    def assassination_burst(self,x,y):
        self._burst(x,y,42,settings.COLOR_ACCENT_GREEN,2,9,20,38,5)
        self._burst(x,y,14,settings.COLOR_TEXT,3,8,12,24,3)
        self.shake(settings.SHAKE_ON_ASSASSINATION,16)
    def dust_step(self,x,y):
        for _ in range(8):
            self.particles.append(Particle(x,y,random.uniform(-2,2),random.uniform(-1.8,-.2),random.randint(10,18),settings.COLOR_TEXT_DIM,2))
    def update(self):
        for p in self.particles: p.update()
        self.particles=[p for p in self.particles if p.alive]
        for s in self.slashes: s[3]+=1
        self.slashes=[s for s in self.slashes if s[3]<12]
        if self._shake_timer>0: self._shake_timer-=1
    def draw(self,surface):
        for s in self.slashes:
            x,y,facing,age=s; alpha=max(0,180-age*15); trail=pygame.Surface((180,130),pygame.SRCALPHA)
            rect=pygame.Rect(15,15,150,100); start=math.radians(205 if facing==1 else -25); end=math.radians(335 if facing==1 else 155)
            pygame.draw.arc(trail,(settings.COLOR_ACCENT_RED[0],settings.COLOR_ACCENT_RED[1],settings.COLOR_ACCENT_RED[2],alpha),rect,start,end,8)
            pygame.draw.arc(trail,(255,245,245,alpha),rect.inflate(-8,-8),start,end,3)
            surface.blit(trail,(x-90,y-65))
        for p in self.particles: p.draw(surface)
