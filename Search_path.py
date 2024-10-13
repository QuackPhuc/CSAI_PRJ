from collections import deque
import pygame
import numpy as np
from Objects import Object, Ares, Stone, Directions, All_Ares_move, All_move
from Get_Map import get_Map

Object.Map = get_Map('input.txt')


def BFS(obj: Object, goal_pos: list):
    init_pos = obj.init_pos
    Map = obj.Map
    visited = set()
    visited.add(init_pos)


