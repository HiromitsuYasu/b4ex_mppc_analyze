from typing import List
import numpy as np
import ROOT as r
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .Rhombus import Rhombus
from .HitArrayGen import HitArrayGen
r.gROOT.SetBatch()


class TrackReconstructorBase:
    SHOWING_RANGE = (-100, 100)
    X_LEN = Rhombus(0, [0, 0, 0]).x_len
    Y_LEN = Rhombus(0, [0, 0, 0]).y_len

    def __init__(self, rootfile_path: str, threshold_s: List[int]) -> None:
        if len(threshold_s) != 64:
            print("invalid threshold list length")
            exit()
        self._rootfile_path = rootfile_path
        self._hit_array_gen = HitArrayGen(self._rootfile_path)
        for ch in range(64):
            self._hit_array_gen.set_threshold(ch, threshold_s[ch])
        self._hit_array_gen.generate_hit_array()
        self._hit_array = self._hit_array_gen.get_hit_array()

    def fit_track(self, i_event):
        self._i_event = i_event
        self.pixels = []
        self.pix_color = []
        self.pix_index = 0
        for i_layer in range(-4, 4):
            for i in range(-2, 2):
                for j in range(-2, 2):
                    pix = Rhombus(
                        self.pix_index,
                        [self.X_LEN * (i - j), self.Y_LEN * (i + j), 8 * i_layer]
                    )
                    if self._hit_array[i_event][i_layer + 4][i + 2, j + 2] == 1.0:
                        self.pix_color.append("black")
                    else:
                        self.pix_color.append("cyan")
                    self.pixels.append(pix)
                    self.pix_index += 1

    def show(self, i_event):
        self._i_event = i_event
        self.data_scinti_mesh = []
        self.index = 0
        self.fit_track(i_event)
        for pix in self.pixels:
            x, y, z = pix.get_vertices().T
            i, j, k = pix.get_faces().T

            self.data_scinti_mesh.append(
                go.Mesh3d(
                    x=x, y=y, z=z, i=i, j=j, k=k,
                    color=self.pix_color[self.index],
                    opacity=0.05 if self.pix_color[self.index] == "cyan" else 1
                )
            )
            self.index += 1
        layout = go.Layout(
            scene=dict(
                xaxis=dict(nticks=1, range=self.SHOWING_RANGE,),
                yaxis=dict(nticks=1, range=self.SHOWING_RANGE,),
                zaxis=dict(nticks=1, range=self.SHOWING_RANGE,),
            )
        )

        fig = make_subplots(rows=2, cols=2, specs=[[{'type': 'mesh3d'}, {'type': 'mesh3d'}], [{'type': 'mesh3d'}, {}]])
        for i in range(len(self.data_scinti_mesh)):
            fig.add_trace(self.data_scinti_mesh[i], row=1, col=1)
            fig.add_trace(self.data_scinti_mesh[i], row=1, col=2)
            fig.add_trace(self.data_scinti_mesh[i], row=2, col=1)

        fig.update_layout(layout)
        fig.update_layout(height=900, width=1500)

        fig.update_layout(scene2_aspectmode='data')

        fig.update_layout(scene3_aspectmode='data')
        fig.update_scenes(camera=dict(
            eye=dict(x=0.7, y=0, z=0)
        ),
            xaxis_showticklabels=False,
            yaxis_showticklabels=False,
            zaxis_showticklabels=False,
            row=1, col=1)

        fig.update_scenes(camera=dict(
            eye=dict(x=0, y=3.0, z=0)
        ),
            camera_projection_type="orthographic",
            xaxis_showticklabels=False,
            yaxis_showticklabels=False,
            zaxis_showticklabels=False,
            row=2, col=1)

        fig.update_scenes(camera=dict(
            eye=dict(x=0, y=0, z=2.7)
        ),
            camera_projection_type="orthographic",
            xaxis_showticklabels=False,
            yaxis_showticklabels=False,
            zaxis_showticklabels=False,
            row=1, col=2)

        fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False)
        fig.update_layout(title_text="{} event {}".format(self._rootfile_path, self._i_event))

        filename_short = self._rootfile_path.split('/')[-1]
        os.makedirs("img_{}".format(filename_short), exist_ok=True)
        fig.write_image("img_{}/event{}.png".format(filename_short, i_event), scale=10)
        fig.write_html("img_{}/event{}.html".format(filename_short, i_event))
