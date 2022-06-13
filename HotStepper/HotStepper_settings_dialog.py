# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HotStepperDialog
                                 A QGIS plugin
 stepping like a pro
                             -------------------
        begin                : 2015-02-02
        git sha              : $Format:%H$
        copyright            : (C) 2015 by GST
        email                : anfla@gst.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import absolute_import

import os

from qgis.PyQt import QtWidgets, uic
from .qgissettingmanager import SettingManager
from .qgissettingmanager.types import String
from .qgissettingmanager.setting import Scope

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_HotStepper_settings.ui'))


class HotStepper_settings(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(HotStepper_settings, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


class HotStepperDBSettings(SettingManager):
    '''
    Use QGIS internals to keep track of user supplied database credentials.
    '''

    def __init__(self):
        SettingManager.__init__(self, 'HotStepper')
        self.add_setting(String('db_name', Scope.Global, ''))
        self.add_setting(String('db_host', Scope.Global, ''))
        self.add_setting(String('db_user', Scope.Global, ''))
        self.add_setting(String('db_password', Scope.Global, ''))
        self.add_setting(String('db_port', Scope.Global, '5432'))

