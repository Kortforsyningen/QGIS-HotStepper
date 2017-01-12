# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HotStepper
                                 A QGIS plugin
 stepping like a pro
                             -------------------
        begin                : 2015-02-02
        copyright            : (C) 2015 by GST
        email                : anfla@gst.dk
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load HotStepper class from file HotStepper.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .HotStepper import HotStepper
    return HotStepper(iface)
