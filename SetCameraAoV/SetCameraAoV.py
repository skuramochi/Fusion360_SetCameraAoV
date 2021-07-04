# Author-skuramochi
# Description-Set the camera's angle of view or focal length.

# -*- coding: utf-8 -*-

# Copyright 2021 Satoshi KURAMOCHI <skuramochi@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import math
import traceback
import adsk.core
import adsk.fusion
from adsk.core import CameraTypes

app = adsk.core.Application.cast(None)
ui = adsk.core.UserInterface.cast(None)
design = adsk.fusion.Design.cast(None)
title = 'SetCameraAoV'


def run(context):
    global app, ui, design, title
    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox('No active design', title)
            return

        view = app.activeViewport
        cam = view.camera  # Get the camera from the active viewport.
        cam.isSmoothTransition = True
        # cam.isSmoothTransition = False

        aov = cam.perspectiveAngle   # [radian]
        d = 36.0        # image size (horizontal) [mm]
        # f = 90.0      # (35mm film equivalent) focal length [mm]
        # aov = math.degrees(2 * math.atan(d / 2 / f))    # angle of view (horizontal) [degree]
        f = 1 / math.tan(aov / 2) * d / 2   # (35mm film equivalent) focal length [mm]

        if cam.cameraType not in (CameraTypes.PerspectiveWithOrthoFacesCameraType, CameraTypes.PerspectiveCameraType):
            ui.messageBox("This script doesn't work in Orthographic view.\n"
                          "Please switch the view to Perspective or Perspective with Ortho Faces first.")
            return

        result = ui.messageBox(
            'Yes = angle of view\nNo = focal length\nCancel = abort',
            'Set the camera\'s angle of view or focal length?',
            adsk.core.MessageBoxButtonTypes.YesNoCancelButtonType, adsk.core.MessageBoxIconTypes.QuestionIconType)

        if result == adsk.core.DialogResults.DialogYes:
            (returnValue, cancelled) = ui.inputBox("Input the camera's angle of view [degree].", title, str(math.degrees(aov)))
            if cancelled:
                return
            try:
                aov = math.radians(float(returnValue))
            except ValueError as e:
                ui.messageBox(str(e), "Error", adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)
                return
        elif result == adsk.core.DialogResults.DialogNo:
            (returnValue, cancelled) = ui.inputBox("Input the camera's (35mm film equivalent) focal length [mm]. (the default is 90mm.)", title, str(f))
            if cancelled:
                return
            try:
                f = float(returnValue)
                aov = 2 * math.atan(d / 2 / f)
            except ValueError as e:
                ui.messageBox(str(e), "Error", adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)
                return
        else:
            return

        cam.perspectiveAngle = aov
        view.camera = cam
        if not cam.isSmoothTransition:
            view.refresh()
        adsk.doEvents()

    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), "Critical",
                      adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)
