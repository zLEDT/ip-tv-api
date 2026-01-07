from flet import *
import flet as ft
from screeninfo import get_monitors
import queue
import threading
import cv2
import requests
from time import sleep
from onvif import ONVIFCamera
import os
import psutil
import Librarys.cola as cola
import paho.mqtt.client as mqtt
import json
from datetime import datetime,timedelta
import pyttsx3
import subprocess
import base64
import ffmpegcv
from email.message import EmailMessage
import ssl, smtplib

import win32gui
import win32process
import win32con
import win32api


def bring_window_to_front(pid):
    def enum_windows_callback(hwnd, pid_to_find):
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        if found_pid == pid_to_find and win32gui.IsWindowVisible(hwnd):
            # Minimiza primero
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            sleep(0.1)  # Pequeña pausa para asegurar el cambio de estado
            # Restaura y trae al frente
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            raise StopIteration  # Detiene la búsqueda

    try:
        win32gui.EnumWindows(lambda hwnd, _: enum_windows_callback(hwnd, pid), None)
    except StopIteration:
        pass