# Importa bibliotecas necessárias para o projeto
import tkinter as tk
import mss
import numpy as np
import cv2
from ultralytics import YOLO
import time
import ctypes
import win32gui, win32con, win32api
import math
import keyboard
import threading
import queue
import torch  # Adicionado para verificação de GPU
import json  # Adicionado para configurações dinâmicas
import logging  # Adicionado para debug avançado
import unittest  # Adicionado para testes unitários