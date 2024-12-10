#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 16:49:09 2021

@author: aline
"""
import math
import sys


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import numpy as np
from math import *
import random

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import threading
import matplotlib.pyplot as plt

''''''''''''''''''''''''''
'''''''''A modifier '''''
max_count = 100
''''''''''''''''''''''''''

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
''''''''''Ne pas modifier au dessous de cette ligne ''''''
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

mutex = threading.Lock()
store_pos_robot_x = np.zeros((max_count, 1))
store_pos_robot_y = np.zeros((max_count, 1))
store_ref_x_pixel = np.ones((max_count, 1))
store_ref_y_pixel = np.ones((max_count, 1))
store_image_x_pixel = np.zeros((max_count, 1))
store_image_y_pixel = np.zeros((max_count, 1))
store_temps_s = np.zeros((max_count, 1))


####################
# Classe : Parametre
#
# Hérite de la classe QWidget
#
# Cette classe crée un Widget qu'on peut insérer dans la fenêtre principale
#
# On peut accéder à la valeur de ce paramètre grâce à la méthode accesseur value()
#
#####################

class Parametre(QWidget):

    def __init__(self, val_label, val_min=0.0, val_max=100.0, val_step=1.0, default=0.0):
        QWidget.__init__(self)
        # ---------------------------------------------------------------------
        # ATTRIBUTS
        # ---------------------------------------------------------------------
        self.val = QDoubleSpinBox()

        # ---------------------------------------------------------------------
        # CREATION DU WIDGET
        # ---------------------------------------------------------------------

        label = QLabel(val_label)
        hspacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.val.setRange(val_min, val_max)
        self.val.setSingleStep(val_step)
        self.val.setValue(default)

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addSpacerItem(hspacer)
        layout.addWidget(self.val)

        self.setLayout(layout)

    # -------------------------------------------------------------------------
    # ACCESSEUR
    # -------------------------------------------------------------------------
    def value(self):
        return self.val.value()


# ------------------------------------------------------------------------------
#
# Classe : Figure_Image
#
#   Hérite de la classe QWidget
#
#   Cette classe crée un Widget qu'on peut insérer dans la fenêtre principale
#
# ------------------------------------------------------------------------------

class Figure_Image(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        # ---------------------------------------------------------------------
        # ATTRIBUTS
        # ---------------------------------------------------------------------
        self.figure = Figure(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.gca()

        # ---------------------------------------------------------------------
        # AXES, TITRES, ETC.
        # ---------------------------------------------------------------------
        self.ax.set_title("Coordonnées des points dans l'image")
        self.ax.grid(True)
        self.ax.set_xlabel('x [pixel]')
        self.ax.set_ylabel('y [pixel]')
        self.ax.set_xlim(-400.0, 400.0)
        self.ax.set_ylim(-400.0, 400.0)

        # ---------------------------------------------------------------------
        # CREATION DES GRAPHES
        # ---------------------------------------------------------------------

        self.point_consigne, = self.ax.plot([], [], color='red', marker='*', markersize=10)
        self.point_courant, = self.ax.plot([], [], color='green', marker='*', markersize=10)

        # ---------------------------------------------------------------------
        # MISE EN FORME
        # ---------------------------------------------------------------------
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # -------------------------------------------------------------------------

    # MISE A JOUR DE LA FIGURE
    # -------------------------------------------------------------------------

    def refresh_image(self, point_consigne, point_courant):
        # point consigne
        self.point_consigne.set_xdata(point_consigne[0])
        self.point_consigne.set_ydata(point_consigne[1])

        # point courant
        self.point_courant.set_xdata(point_courant[0])
        self.point_courant.set_ydata(point_courant[1])

        self.canvas.draw()


# ------------------------------------------------------------------------------
#
# Classe : Figure_Robot
#
#   Hérite de la classe QWidget
#
#   Cette classe crée un Widget qu'on peut insérer dans la fenêtre principale
#
# ------------------------------------------------------------------------------

class Figure_Robot(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        # ---------------------------------------------------------------------
        # ATTRIBUTS
        # ---------------------------------------------------------------------
        self.figure = Figure(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.gca()

        # ---------------------------------------------------------------------
        # AXES, TITRES, ETC.
        # ---------------------------------------------------------------------
        self.ax.set_title("Position de l'organe terminal du robot dans le repère monde")
        self.ax.grid(True)
        self.ax.set_xlabel('x [m]')
        self.ax.set_ylabel('y [m]')
        self.ax.set_xlim(-0.3, 0.3)
        self.ax.set_ylim(-0.3, 0.3)

        self.position_initiale, = self.ax.plot([], [], color='red', marker='o', markersize=10)
        self.position_courante, = self.ax.plot([], [], color='green', marker='o', markersize=10)

        # ---------------------------------------------------------------------
        # CREATION DES GRAPHES
        # ---------------------------------------------------------------------
        self.plot_image = self.ax.plot(animated=True)
        self.plot_robot = self.ax.plot(animated=True)

        # ---------------------------------------------------------------------
        # MISE EN FORME
        # ---------------------------------------------------------------------
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # -------------------------------------------------------------------------
        # MISE A JOUR DE LA FIGURE
        # -------------------------------------------------------------------------

    def refresh_robot(self, position_initiale, position_courante):
        # point consigne
        self.position_initiale.set_xdata(position_initiale[0])
        self.position_initiale.set_ydata(position_initiale[1])

        # point courant
        self.position_courante.set_xdata(position_courante[0])
        self.position_courante.set_ydata(position_courante[1])

        self.canvas.draw()


# ------------------------------------------------------------------------------
#
# Classe :
#
#   Hérite de la classe QMainWindow
#
# ------------------------------------------------------------------------------


class Fenetre(QMainWindow):

    #   -----------------------------------------------------------------------
    #   Initialisation de la fenetre
    #   -----------------------------------------------------------------------

    def __init__(self, parent=None):
        super(Fenetre, self).__init__(parent)

        #   ------------------------------------------------------------------
        #   Variables
        #   ------------------------------------------------------------------

        # Declenchement du controleur et de l'affichage des donnees

        self.period_control = 50  # ms
        self.period_gui = 50  # ms

        self.timer_gui = QTimer()
        self.timer_gui.timeout.connect(self.refresh_gui)

        self.timer_control = QTimer()
        self.timer_control.timeout.connect(self.visual_servoing)

        self.setGeometry(30, 30, 1500, 500)

        # Paramètres réels
        self.focale = 20e-3
        self.dim_x = 10e-6
        self.dim_y = 10e-6
        self.distance = 0.4

        # Parametres estimés
        self.focale_e = Parametre(
            val_label="Focale estimée [mm] :",
            val_min=0.0,
            val_max=50.0,
            val_step=1.0,
            default=20.0)

        self.distance_e = Parametre(
            val_label="Distance estimée [m] :",
            val_min=0.0,
            val_max=1.0,
            val_step=0.1,
            default=0.4)

        self.angle_e = Parametre(
            val_label="Angle estimé [deg] :",
            val_min=0.0,
            val_max=90.0,
            val_step=2.0,
            default=0.0)

        self.dim_x_e = Parametre(
            val_label="Taille estimée du pixel /x [μm] :",
            val_min=0.0,
            val_max=50.0,
            val_step=0.5,
            default=10.0)

        self.dim_y_e = Parametre(
            val_label="Taille estimée du pixel /y [μm] :",
            val_min=0.0,
            val_max=50.0,
            val_step=0.5,
            default=10.0)

        self.gain = Parametre(
            val_label="Gain :",
            val_min=0,
            val_max=20,
            val_step=0.5,
            default=5)

        self.consigne_x = Parametre(
            val_label="Consigne /x [pixel] :",
            val_min=-400.0,
            val_max=400.0,
            val_step=10.0,
            default=0.0)

        self.consigne_y = Parametre(
            val_label="Consigne /y [pixel] :",
            val_min=-400.0,
            val_max=400.0,
            val_step=10,
            default=0.0)

        # Figures
        self.fig_image = Figure_Image()
        self.fig_robot = Figure_Robot()

        # Boutons
        self.bouton_run = QPushButton("Démarrer")
        self.bouton_stop = QPushButton("Arrêter")
        self.bouton_stop.setEnabled(False)

        # Asservissement visuel
        self.count = 0

        self.image_point_consigne = np.array([[0.0], [0.0]])
        self.image_point_courant = np.array([[0.0], [0.0]])

        self.robot_position_initiale = np.array([[0.0], [0.0]])
        self.robot_position_courante = np.array([[0.0], [0.0]])

        #   -------------------------------------------------------------------
        #   Creation de l'interface graphique
        #   -------------------------------------------------------------------

        # Parametres
        # -----------
        param_box = QGroupBox("Paramètres")

        layout_param = QVBoxLayout()
        layout_param.addWidget(self.focale_e)
        layout_param.addWidget(self.distance_e)
        layout_param.addWidget(self.angle_e)
        layout_param.addWidget(self.dim_x_e)
        layout_param.addWidget(self.dim_y_e)
        layout_param.addWidget(self.gain)

        param_box.setLayout(layout_param)

        # Consigne
        # -----------
        consigne_box = QGroupBox("Consigne")

        layout_consigne = QVBoxLayout()
        layout_consigne.addWidget(self.consigne_x)
        layout_consigne.addWidget(self.consigne_y)

        consigne_box.setLayout(layout_consigne)

        # Boutons
        # -----------
        layout_boutons = QHBoxLayout()
        layout_boutons.addWidget(self.bouton_run)
        layout_boutons.addWidget(self.bouton_stop)

        # Control
        # -----------
        layout_control = QVBoxLayout()
        layout_control.addWidget(param_box)
        layout_control.addWidget(consigne_box)
        layout_control.addLayout(layout_boutons)

        # Figures
        # -----------
        layout_fig = QHBoxLayout()
        layout_fig.addWidget(self.fig_image)
        layout_fig.addWidget(self.fig_robot)

        # Main Layout
        # -----------
        main_layout = QHBoxLayout()
        main_layout.addLayout(layout_control)
        main_layout.addLayout(layout_fig)

        # Widget Central
        # -----------
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Titre/Icone/etc. de la fenêtre
        # -----------
        self.setWindowTitle("Asservissement visuel")
        self.setWindowIcon(QIcon("./logo_polytech.png"))

        #   -------------------------------------------------------------------
        #   Comportement des boutons
        #   -------------------------------------------------------------------
        self.bouton_run.clicked.connect(self.start_timers)
        self.bouton_stop.clicked.connect(self.stop_timers)

        #   -----------------------------------------------------------------------

    #   Asservissement visuel
    #   -----------------------------------------------------------------------

    # Cette méthode est appelée lors d'un appui sur le bouton "Démarrer"
    # Elle met en route les deux timers.

    def start_timers(self):
        # lancement des timers
        self.timer_gui.start(self.period_gui)
        self.timer_control.start(self.period_control)

        # etat des boutons
        self.bouton_run.setEnabled(False)
        self.bouton_stop.setEnabled(False)

        self.angle_e.setEnabled(False)
        self.gain.setEnabled(False)
        self.dim_x_e.setEnabled(False)
        self.dim_y_e.setEnabled(False)
        self.gain.setEnabled(False)
        self.consigne_x.setEnabled(False)
        self.consigne_y.setEnabled(False)
        self.distance_e.setEnabled(False)
        self.focale_e.setEnabled(False)

        self.count = 0

    # Cette méthode est appelée lors d'un appui sur le bouton "Arrêter"
    # Elle arrête les deux timers.

    def stop_timers(self):
        global store_pos_robot_x
        global store_pos_robot_y
        global store_ref_x_pixel
        global store_ref_y_pixel
        global store_image_x_pixel
        global store_image_y_pixel
        global store_temps_s

        store_ref_x_pixel = self.image_point_consigne[0] * np.ones((max_count, 1))
        store_ref_y_pixel = self.image_point_consigne[1] * np.ones((max_count, 1))

        # Arret des timers
        self.timer_control.stop()

        # etat des boutons
        self.bouton_run.setEnabled(True)
        self.bouton_stop.setEnabled(False)

        self.angle_e.setEnabled(True)
        self.gain.setEnabled(True)
        self.dim_x_e.setEnabled(True)
        self.dim_y_e.setEnabled(True)
        self.gain.setEnabled(True)
        self.consigne_x.setEnabled(True)
        self.consigne_y.setEnabled(True)
        self.distance_e.setEnabled(True)
        self.focale_e.setEnabled(True)

        self.image_point_consigne = np.array([[0.0], [0.0]])
        self.image_point_courant = np.array([[0.0], [0.0]])

        self.robot_position_intiale = np.array([[0.0], [0.0]])
        self.robot_position_courante = np.array([[0.0], [0.0]])

        for i in range(max_count):
            store_temps_s[i] = i * self.period_control * 1e-3

        fig1, ax1 = plt.subplots()
        fig1.canvas.draw()
        ax1.plot(store_temps_s[:max_count - 1, 0], store_pos_robot_x[:max_count - 1, 0], 'r-', linewidth=2,
                 label='End effector x position')
        ax1.plot(store_temps_s[:max_count - 1, 0], store_pos_robot_y[:max_count - 1, 0], 'b-', linewidth=2,
                 label='End effector y position')
        ax1.set_facecolor('w')
        plt.legend(facecolor='white', framealpha=0)
        plt.xlabel('time(seconds)')
        plt.ylabel('m')
        plt.grid()
        fig1.suptitle('Robot end effector position', fontsize=13)
        plt.show()

        fig2, ax2 = plt.subplots()
        fig2.canvas.draw()
        ax2.plot(store_temps_s[:max_count - 2, 0], store_ref_x_pixel[:max_count - 2, 0], 'r--', linewidth=2,
                 label='Image x reference position')
        ax2.plot(store_temps_s[:max_count - 2, 0], store_ref_y_pixel[:max_count - 2, 0], 'b--', linewidth=2,
                 label='Image y reference position')
        ax2.plot(store_temps_s[:max_count - 2, 0], store_image_x_pixel[:max_count - 2, 0], 'r-', linewidth=2,
                 label='Image x current position')
        ax2.plot(store_temps_s[:max_count - 2, 0], store_image_y_pixel[:max_count - 2, 0], 'b-', linewidth=2,
                 label='Image y current position')

        ax2.set_facecolor('w')
        plt.legend(facecolor='white', framealpha=0)
        plt.xlabel('time(seconds)')
        plt.ylabel('pixels')
        plt.grid()
        fig2.suptitle('Image point position', fontsize=13)
        plt.show()

        fig3, ax3 = plt.subplots()
        fig3.canvas.draw()
        ax3.plot(store_image_x_pixel[:max_count - 2, 0], store_image_y_pixel[:max_count - 2, 0], 'k-', linewidth=2)
        ax3.set_facecolor('w')
        plt.xlabel('pixels')
        plt.ylabel('pixels')
        plt.grid()
        fig3.suptitle('Image point trajectory in the image plane', fontsize=13)
        plt.show()

        # print(store_image_x_pixel[0])

    # Cette méthode est appelée à chaque coup d'horloge de timer_control
    #

    def visual_servoing(self):
        global mutex
        global max_count
        global store_pos_robot_x
        global store_pos_robot_y
        global store_ref_x_pixel
        global store_ref_y_pixel
        global store_image_x_pixel
        global store_image_y_pixel
        global store_temps_s

        self.count += 1
        # print(self.count)

        if self.count == max_count - 1:
            self.stop_timers()
        else:

            mutex.acquire()
            pos_image_courante = self.image_point_courant
            pos_rob_courante = self.robot_position_courante
            pos_image_desiree = self.image_point_consigne
            d_e = self.distance_e.value()
            f_e = self.focale_e.value() * 1e-3
            dim_x_e = self.dim_x_e.value() * 1e-6
            dim_y_e = self.dim_y_e.value() * 1e-6
            gain = self.gain.value()
            angle_e = self.angle_e.value()
            # print(pos_rob_courante)
            mutex.release()

            '''''''COMPLETER EN DESSOUS DE CETTE LIGNE AUX ENDROITS INDIQUES''''

            ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            '''' Ici se situe le coeur de votre TP : Vous devez compléter ce qui manque '''
            ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

            "calcul erreur dans l'image : utiliser pos_image_desiree et pos_image_courante" \
            "qui sont deux np.array (2,1)"
            # erreur_image = ...

            "Calcul matrice des paramètres intrinsèques : A1 : un np.array (2,2)" \
            "Les paramètres à utiliser sont : dim_x_e : dimension estimée du pixel selon l'axe" \
            "x, dim_y_e : la dimension du pixel selon l'axe y, f_e : l'estimée de la focale"
            # A1 = ...

            "Calcul du jacobien image sans les paramètres intrinsèques : un np.array dont" \
            "vous déterminerez la taille. Les paramètres à utliser sont d_e : la distance" \
            "estimée de la distance à la cible"
            # J_im = ...

            "Calcul du jacobien image complet : un np.array dont vous déterminerez la taille"
            # J_image = ...

            " Jacobien naturel du robot : un np.array dont vous déterminerez la taille"
            # J_robot = ...

            "loi de commande visuelle : un np.array dont vous déterminerez la taille " \
            "si vous avez des inversions utiliser np.linalg.inv "
            # V_vis = ...

            "Rotation du repère de l'organe terminal au repère caméra"
            angle_e = math.radians(angle_e)
            Rnc_e = np.array([[cos(angle_e), sin(angle_e)], [-sin(angle_e), cos(angle_e)]])

            "loi de commande du robot à écrire"
            V_robot = np.array([[0.0], [0.0]])

            ''''''''''''''''''''''''''''''''''''''''''''''''''
            ''' NE RIEN MODIFIER AU DESSOUS DE CETTE LIGNE '''
            ''''''''''''''''''''''''''''''''''''''''''''''''''

            # print(V_robot)
            "simulation robot"
            pos_rob_courante += self.period_control * 1.0e-3 * V_robot

            "simulation acquisition de l'image"
            'Position du point dans le repère monde'
            P_0 = np.array([[0.0], [0.0], [0.0], [1.0]])

            'Matrice de transformation homogène du rèpère caméra vers le repère monde'
            M_c0 = np.array([[1.0, 0.0, 0.0, -pos_rob_courante[0]],
                             [0.0, 1.0, 0.0, -pos_rob_courante[1]],
                             [0.0, 0.0, 1.0, self.distance],
                             [0.0, 0.0, 0.0, 1.0]],dtype="object")

            'Position du point d''inérêt dans le repère caméra'
            P_c = M_c0 @ P_0

            x_random = 1.2 * random.random()
            y_random = 1.2 * random.random()

            # print(x_random)
            'position courante du point en pixels dans l''image'
            pos_image_courante[0] = (self.focale / (self.dim_x * self.distance)) * P_c[0] + x_random
            pos_image_courante[1] = (self.focale / (self.dim_y * self.distance)) * P_c[1] + y_random

            # print(pos_image_courante)

            mutex.acquire()

            self.image_point_courant = pos_image_courante
            self.robot_position_courante = pos_rob_courante
            mutex.release()

            '''Stockage '''
            store_pos_robot_x[self.count] = pos_rob_courante[0]
            store_pos_robot_y[self.count] = pos_rob_courante[1]
            # store_ref_x_pixel[self.count] = pos_image_desiree[0]
            # store_ref_y_pixel[self.count] = pos_image_desiree[1]
            store_image_x_pixel[self.count] = self.image_point_courant[0]
            store_image_y_pixel[self.count] = self.image_point_courant[1]
            store_temps_s[self.count] = (self.count) * self.period_control * 1.0e-3

    #   -----------------------------------------------------------------------
    #   Affichage des donnees
    #   -----------------------------------------------------------------------

    def refresh_gui(self):
        global mutex
        self.image_point_consigne[0] = self.consigne_x.value()
        self.image_point_consigne[1] = self.consigne_y.value()

        mutex.acquire()
        self.fig_image.refresh_image(self.image_point_consigne, self.image_point_courant)
        self.fig_robot.refresh_robot(self.robot_position_initiale, self.robot_position_courante)
        mutex.release()


#   -----------------------------------------------------------------------
#   Programme principal
#   -----------------------------------------------------------------------

def run():
    app = QApplication(sys.argv)
    fen = Fenetre()
    fen.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
