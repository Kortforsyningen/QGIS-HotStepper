# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HotStepper
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
from __future__ import print_function
from builtins import str
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtWidgets import QShortcut
from qgis.PyQt.QtGui import QKeySequence
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from datetime import datetime
#from osgeo import ogr

# Initialize Qt resources from file resources.py
from . import resources_rc

# Import the code for the dialog
from .HotStepper_dialog import HotStepperDialog
from .HotStepper_settings_dialog import HotStepper_settings, HotStepperDBSettings

import os.path
import psycopg2
import getpass
import math

#set global attributes
ccdb_svar = '1'

DB_schema = "check_tables"
DB_table = "tiletest_kontrol"
DB_geom = "geom"
CHKuser = ""
FailCodes = []

class HotStepper(QDialog):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        global CHKuser
        QDialog.__init__(self, iface.mainWindow())
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.settings = HotStepperDBSettings()

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'HotStepper_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = HotStepperDialog()
        self.qcs = HotStepper_settings()

        # populate line edits in HotStepper_settings dialog
        self.qcs.db_name.insert(self.settings.value('db_name'))
        self.qcs.db_host.insert(self.settings.value('db_host'))
        self.qcs.db_user.insert(self.settings.value('db_user'))
        self.qcs.db_password.insert(self.settings.value('db_password'))
        self.qcs.db_port.insert(self.settings.value('db_port'))

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&HotStepper')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'HotStepper')
        self.toolbar.setObjectName(u'HotStepper')

        self.qcs.textEdit.clear()
        FailCodes = ['Clouds\nBridge\nBuilding']
        self.qcs.textEdit.insertPlainText(''.join(FailCodes))

        #set user
        CHKuser = getpass.getuser()

        # Setup keyboard shortcuts
        # def short_ok():
        #     QMessageBox.information(None, "HotButton", "Enter pressed")
        #     self.qc_ok()
        # def short_gcp():
        #     QMessageBox.information(None, "HotButton", "Key_0 pressed")
        #     self.gcp_mapclick()

        #short1 = QShortcut(QKeySequence(Qt.Key_F5), self.iface.mainWindow())
        #short1.setContext(Qt.ApplicationShortcut)
        #short1.activated.connect(self.qc_ok)

        #short2 = QShortcut(QKeySequence(Qt.Key_F4), self.iface.mainWindow())
        #short2.setContext(Qt.ApplicationShortcut)
        #short2.activated.connect(self.gcp_measure)

        #short3 = QShortcut(QKeySequence(Qt.Key_X), iface.mainWindow())
        #short3.setContext(Qt.ApplicationShortcut)
        #short3.activated.connect(self.qc_fejl)

        #short4 = QShortcut(QKeySequence(Qt.Key_F2), iface.mainWindow())
        #short4.setContext(Qt.ApplicationShortcut)
        #short4.activated.connect(self.qc_nextstep)

        #set mapclicktool
        self.canvas = self.iface.mapCanvas()
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        self.clickTool.canvasClicked.connect(self.gcp_mapclick)


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        return QCoreApplication.translate('HotStepper', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/HotStepper/setup.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Setup'),
            callback=self.qc_setup,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/HotStepper/reload.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Go to next (r)'),
            callback=self.qc_nextstep,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/HotStepper/ok.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Mark OK and go to next (v)'),
            callback=self.qc_ok,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/HotStepper/fail.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Mark fail and go to next (x)'),
            callback=self.qc_fejl,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/HotStepper/reset.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Reset check state for selected'),
            callback=self.qc_reset,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/HotStepper/multiok.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Set OK for selected'),
            callback=self.qc_multiok,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/HotStepper/lock.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Lock tiles'),
            callback=self.qc_lock,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/HotStepper/target.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Measure GCP (g)'),
            callback=self.gcp_measure,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&HotStepper'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def qc_setup(self):
        global DB_schema
        global DB_table
        global DB_geom
        global ccdb_svar
        global FailCodes

        """Run method that performs all the real work"""
        # show the dialog
        self.qcs.show()
        self.qcs.inShapeA.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.qcs.inShapeA.layerChanged.connect(self.update1)
        self.qcs.checkBoxGCP.clicked.connect(self.fillFailCodes)
        self.qcs.radioButton.toggle()
        self.qcs.inTableA.currentIndexChanged.connect(self.tableChanged)

        # lyrs = self.iface.legendInterface().layers()
        # lyr_list = []
        # for layer in lyrs:
        #     lyr_list.append(layer.name())
        # self.qcs.inShapeA.clear()
        # self.qcs.inShapeA.addItems(lyr_list)

        self.settings.set_value('db_name', self.qcs.db_name.text())
        self.settings.set_value('db_host', self.qcs.db_host.text())
        self.settings.set_value('db_user', self.qcs.db_user.text())
        self.settings.set_value('db_password', self.qcs.db_password.text())
        self.settings.set_value('db_port', self.qcs.db_port.text())

        #list available PostgreSQL tables
        try:
            conn = psycopg2.connect(
                "dbname={name} user={user} host={host} password={pswd}".format(
                    name=self.settings.value('db_name'),
                    user=self.settings.value('db_user'),
                    host=self.settings.value('db_host'),
                    pswd=self.settings.value('db_password'),
                )
            )
            cur = conn.cursor()
            cur.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = '"""+DB_schema+"""'""")
            rows = cur.fetchall()
        except(psycopg2.OperationalError):
            QMessageBox.information(None, "DB connection", "Cannot connect to database")
            return

        tableList = []
        for e in rows:
            if ("chk_" in e[0])or("gcp_" in e[0]):
                tableList.append(e[0])

        self.qcs.inTableA.clear()
        self.qcs.inTableA.addItems(tableList)

        # Run the dialog event loop
        result = self.qcs.exec_()
        # See if OK was pressed

        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            if self.qcs.radioButton.isChecked():
                DB_table = self.qcs.inTableA.currentText()

                uri = QgsDataSourceUri()
                uri.setConnection(
                    self.settings.value('db_host'),
                    self.settings.value('db_port'),
                    self.settings.value('db_name'),
                    self.settings.value('db_user'),
                    self.settings.value('db_password')
                )
                uri.setDataSource(DB_schema, DB_table, DB_geom,"")
                uri.uri()
                iface.addVectorLayer(uri.uri(), DB_table, "postgres")

                #set styling
                DBlaget = self.iface.activeLayer()

                if "gcp" in DB_table:
                    DBlaget.loadNamedStyle(os.path.dirname(__file__)+"\\GCP.qml")
                else:
                    dbkald = "SELECT ST_GeometryType(st_astext(geom)) FROM "+DB_schema+"."+DB_table+" WHERE id_0 = 1"
                    print(dbkald)
                    cur.execute(dbkald)
                    #print(str(cur.fetchone()[0]))
                    typen = str(cur.fetchone()[0])
                    print(typen + " set legend")
                    #QMessageBox.information(None, "geometritype", typen)
                    if typen == "ST_Polygon" or typen == "ST_MultiPolygon":
                        DBlaget.loadNamedStyle(os.path.dirname(__file__)+"\\Polygons.qml")
                    elif typen == "ST_Point" or typen == "ST_MultiPoint":
                        DBlaget.loadNamedStyle(os.path.dirname(__file__)+"\\Points.qml")
                    elif typen == "ST_LineString":
                        DBlaget.loadNamedStyle(os.path.dirname(__file__)+"\\Lines.qml")

                ccdb_svar = 1

                dbkald = "SELECT failcodes FROM "+DB_schema+"."+DB_table.replace("chk_", "err_").replace("gcp_", "err_")+" WHERE id_0 = 1"
                cur.execute(dbkald)
                FailCodes = str(cur.fetchone()[0]).split("\n")


            if self.qcs.radioButton_2.isChecked():
                inputFilNavn = self.qcs.inShapeA.currentText()
                inputField = self.qcs.inField1.currentText()
                FailCodes = self.qcs.textEdit.toPlainText()

                try:
                    conn = psycopg2.connect(
                        "dbname={name} user={user} host={host} password={pswd}".format(
                            name=self.settings.value('db_name'),
                            user=self.settings.value('db_user'),
                            host=self.settings.value('db_host'),
                            pswd=self.settings.value('db_password'),
                        )
                    )
                    cur = conn.cursor()

                    if self.qcs.checkBoxGCP.isChecked():
                        DB_table ="gcp_"+self.qcs.inTableName.text().lower()
                    else:
                        DB_table ="chk_"+self.qcs.inTableName.text().lower()

                    ligenu = str(datetime.now())

                    #her arbejdes
                    cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (DB_table,))
                    if cur.fetchone()[0]:
                        DB_table = DB_table+str(1)

                    #Create failcodes DB
                    cur.execute("CREATE TABLE "+DB_schema+"."+DB_table.replace("chk_", "err_").replace("gcp_", "err_")+"(Id_0 INTEGER PRIMARY KEY,failcodes text)")
                    conn.commit()
                    cur.execute("INSERT INTO "+DB_schema+"."+DB_table.replace("chk_", "err_").replace("gcp_", "err_")+" VALUES( 1 , \'"+FailCodes+"\' );")
                    conn.commit()


                    if self.qcs.checkBoxGCP.isChecked():
                        #cur.execute("CREATE TABLE "+DB_schema+"."+DB_table+"(Id_0 INTEGER PRIMARY KEY,JoinID text, check_status text, check_user text, chk_date timestamp without time zone, chk_comment text, fail_code text, g_x real, g_y real, m_x real, m_y real, diff_x real, diff_y real, diff real,qcorto text, geom geometry)")
                        cur.execute("CREATE TABLE "+DB_schema+"."+DB_table+"(Id_0 INTEGER PRIMARY KEY,JoinID text, check_status text, check_user text, chk_date timestamp without time zone, chk_comment text, fail_code text, g_x real, g_y real, m_x real, m_y real, diff_x real, diff_y real, diff real, geom geometry)")
                    else:
                        cur.execute("CREATE TABLE "+DB_schema+"."+DB_table+"(Id_0 INTEGER PRIMARY KEY,JoinID text, check_status text, check_user text, chk_date timestamp without time zone, chk_comment text, fail_code text, geom geometry)")
                    conn.commit()

                    canvas = self.iface.mapCanvas()
                    allLayers = canvas.layers()

                    for i in allLayers:

                        if(i.name() == inputFilNavn):
                            layer=i
                            if self.qcs.useSelectedA.isChecked():
                                selection = layer.selectedFeatures()
                                QMessageBox.information(None, "status", "eksporterer valgte")
                            else:
                                selection = layer.getFeatures()
                                QMessageBox.information(None, "status", "eksporterer alt")

                            tableID = 1
                            for feat in selection:
                                # QCorto = ''
                                # try:
                                #     QCorto = feat[self.qcs.ortonamefield.currentText()]
                                #     QCorto = 'c:/temp/COWStemp/jpeg/O'+ QCorto + '.tif'
                                # except:
                                #     QCorto = ''
                                geom = feat.geometry()
                                JoinID = feat[inputField]

                                if self.qcs.checkBoxGCP.isChecked():
                                    typen = "punkt"
                                    geom = geom.centroid()
                                    #cur.execute("INSERT INTO "+DB_schema+"."+DB_table+" VALUES("+str(tableID)+",'"+str(JoinID)+"','pending',null,null,null,null,0.0,0.0,0.0,0.0,0.0,0.0,-99.0,'"+QCorto+"',ST_GeomFromText('"+geom.asWkt()+"'));")
                                    cur.execute("INSERT INTO "+DB_schema+"."+DB_table+" VALUES("+str(tableID)+",'"+str(JoinID)+"','pending',null,null,null,null,0.0,0.0,0.0,0.0,0.0,0.0,-99.0,ST_GeomFromText('"+geom.asWkt()+"'));")
                                else:

                                    if (layer.geometryType() == 2):
                                        typen = "polygon"
                                    elif (layer.geometryType() == 0):
                                        typen = "punkt"
                                    elif (layer.geometryType() == 1):
                                        typen = "linie"

                                    cur.execute("INSERT INTO "+DB_schema+"."+DB_table+" VALUES("+str(tableID)+",'"+str(JoinID)+"','pending',null,null,null,null,ST_GeomFromText('"+geom.asWkt()+"'));")
                                tableID = tableID+1

                    conn.commit()

                    #QMessageBox.information(None, "test input", "her2")
                    time.sleep(4)

                    uri = QgsDataSourceUri()
                    uri.setConnection(self.settings.value('db_host'), self.settings.value('db_port'), self.settings.value('db_name'), self.settings.value('db_user'), self.settings.value('db_password'))
                    uri.setDataSource(DB_schema, DB_table, DB_geom,"")
                    uri.uri()
                    iface.addVectorLayer(uri.uri(), DB_table, "postgres")
                    ccdb_svar = 1

                    #set styling
                    DBlaget = self.iface.activeLayer()
                    if self.qcs.checkBoxGCP.isChecked():
                        DBlaget.loadNamedStyle(os.path.dirname(__file__)+"\\GCP.qml")
                    elif typen == "polygon":
                        DBlaget.loadNamedStyle(os.path.dirname(__file__)+"\\Polygons.qml")
                    elif typen == "punkt":
                        DBlaget.loadNamedStyle(os.path.dirname(__file__)+"\\Points.qml")
                    elif typen == "linie":
                        DBlaget.loadNamedStyle(os.path.dirname(__file__)+"\\Lines.qml")

                    dbkald = "SELECT failcodes FROM "+DB_schema+"."+DB_table.replace("chk_", "err_").replace("gcp_", "err_")+" WHERE id_0 = 1"
                    cur.execute(dbkald)
                    FailCodes = str(cur.fetchone()[0]).split("\n")

                except psycopg2.DatabaseError as e:

                    if conn:
                        conn.rollback()

                    print('Error %s' % e)
                    sys.exit(1)

                finally:

                    if conn:
                        conn.close()

            pass

    def qc_nextstep(self):
        conn = psycopg2.connect(
            "dbname={name} user={user} host={host} password={pswd}".format(
                name=self.settings.value('db_name'),
                user=self.settings.value('db_user'),
                host=self.settings.value('db_host'),
                pswd=self.settings.value('db_password'),
            )
        )
        cur = conn.cursor()
        global ccdb_svar

        if(1>0):
        #try:
            ## Her unloades tidligere QC-orto
            lyrs = [layer for layer in QgsProject.instance().mapLayers().values()]
            for layer in lyrs:
                if layer.name()[:3] == 'qco':
                    # print layer.name()
                    QgsMapLayerRegistry.instance().removeMapLayers([layer.id()])
            ##

            dbkald = "SELECT id_0 FROM "+DB_schema+"."+DB_table+" WHERE \"check_status\" = \'pending\' OR (\"check_status\" = \'locked\' AND \"check_user\" = \'"+CHKuser+"\') ORDER BY \"check_status\" || reverse(joinid) || \"id_0\"     "
            cur.execute(dbkald)
            ccdb_svar = str(cur.fetchone())
            print(ccdb_svar)
            if (ccdb_svar == "None"):
                QMessageBox.information(None, "QC info", 'All done, nothing to check')
                return

            ccdb_svar = ccdb_svar.strip("(").strip(")").strip(",")

            dbkald = "update "+DB_schema+"."+DB_table+" set \"check_status\" = \'locked\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)
            conn.commit()
            dbkald = "update "+DB_schema+"."+DB_table+" set \"check_user\" = \'"+CHKuser+"\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)
            conn.commit()
            dbkald = "update "+DB_schema+"."+DB_table+" set \"chk_date\" = \'"+str(datetime.now())+"\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)
            conn.commit()

            #zoom til feature
            dbkald = "SELECT st_astext(geom) FROM "+DB_schema+"."+DB_table+" WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)
            geometri = str(cur.fetchone()[0])

            gem = QgsGeometry.fromWkt(geometri)
            box = gem.boundingBox()
            iface.mapCanvas().setExtent(box)
            iface.mapCanvas().refresh()

            ## Her loades QC-orto
            # dbkald = "SELECT qcorto FROM "+DB_schema+"."+DB_table+" WHERE id_0 = "+ccdb_svar
            # print(dbkald)
            # cur.execute(dbkald)

            # QCo_path = str(cur.fetchone()[0])
            # root = QgsProject.instance().layerTreeRoot()

            # layer_qco = QgsRasterLayer(QCo_path, 'qco')
            # layer_qco.setCrs(QgsCoordinateReferenceSystem(25832, QgsCoordinateReferenceSystem.EpsgCrsId))

            # QgsMapLayerRegistry.instance().addMapLayer(layer_qco, False)
            # root.addLayer(layer_qco)


            #QgsMapLayerRegistry.instance().addMapLayer(layer_qco)
            ##


        #except(psycopg2.ProgrammingError):
        #    QMessageBox.information(None, "QC info", 'All done, nothing to check')
        #pass

    def qc_ok(self):
        conn = psycopg2.connect(
            "dbname={name} user={user} host={host} password={pswd}".format(
                name=self.settings.value('db_name'),
                user=self.settings.value('db_user'),
                host=self.settings.value('db_host'),
                pswd=self.settings.value('db_password'),
            )
        )
        cur = conn.cursor()
        global ccdb_svar
        #set aktuelle feature til ok
        dbkald = "update "+DB_schema+"."+DB_table+" set \"check_status\" = \'OK\' WHERE id_0 = "+ccdb_svar
        cur.execute(dbkald)
        conn.commit()

        self.iface.mapCanvas().refresh()
        self.qc_nextstep()
        pass

    def qc_fejl(self):
        conn = psycopg2.connect(
            "dbname={name} user={user} host={host} password={pswd}".format(
                name=self.settings.value('db_name'),
                user=self.settings.value('db_user'),
                host=self.settings.value('db_host'),
                pswd=self.settings.value('db_password'),
            )
        )
        cur = conn.cursor()
        global ccdb_svar
        #set aktuelle feature til fail
        self.dlg.show()

        self.dlg.comboBox.clear()
        self.dlg.comboBox.addItems(FailCodes)

        result = self.dlg.exec_()

        if result:

            dbkald = "update "+DB_schema+"."+DB_table+" set \"check_status\" = \'Fail\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)
            conn.commit()

            dbkald = "update "+DB_schema+"."+DB_table+" set \"fail_code\" = \'" + self.dlg.comboBox.currentText() +"\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)
            conn.commit()

            dbkald = "update "+DB_schema+"."+DB_table+" set \"chk_date\" = \'"+str(datetime.now())+"\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)
            conn.commit()

            dbkald = "update "+DB_schema+"."+DB_table+" set \"chk_comment\" = \'" + self.dlg.textEdit.toPlainText() +"\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)
            conn.commit()

            self.iface.mapCanvas().refresh()
            self.qc_nextstep()
            pass

    def qc_genlaes(self):
        global ccdb_svar

        dbkald = "update "+DB_schema+"."+DB_table+" set \"check_status\" = \'Fail\' WHERE id_0 = "+ccdb_svar
        cur.execute(dbkald)
        conn.commit()

        self.iface.mapCanvas().refresh()

        pass

    def qc_lock(self):
        conn = psycopg2.connect(
            "dbname={name} user={user} host={host} password={pswd}".format(
                name=self.settings.value('db_name'),
                user=self.settings.value('db_user'),
                host=self.settings.value('db_host'),
                pswd=self.settings.value('db_password'),
            )
        )
        cur = conn.cursor()

        cLayer = self.iface.activeLayer()
        selection = cLayer.selectedFeatures()

        for feat in selection:
            fID = feat["Id_0"]
            dbkald = "update "+DB_schema+"."+DB_table+" set \"check_status\" = \'locked\' WHERE id_0 = "+str(fID)
            cur.execute(dbkald)
            dbkald = "update "+DB_schema+"."+DB_table+" set \"check_user\" = \'"+CHKuser+"\' WHERE id_0 = "+str(fID)
            cur.execute(dbkald)
            dbkald = "update "+DB_schema+"."+DB_table+" set \"chk_date\" = \'"+str(datetime.now())+"\' WHERE id_0 = "+str(fID)
            cur.execute(dbkald)
        conn.commit()

        self.iface.mapCanvas().refresh()

        pass

    def qc_reset(self):
        conn = psycopg2.connect(
            "dbname={name} user={user} host={host} password={pswd}".format(
                name=self.settings.value('db_name'),
                user=self.settings.value('db_user'),
                host=self.settings.value('db_host'),
                pswd=self.settings.value('db_password'),
            )
        )
        cur = conn.cursor()

        cLayer = self.iface.activeLayer()
        selection = cLayer.selectedFeatures()

        for feat in selection:
            fID = feat["Id_0"]
            dbkald = "update "+DB_schema+"."+DB_table+" set \"check_status\" = \'pending\' WHERE id_0 = "+str(fID)
            cur.execute(dbkald)
            dbkald = "update "+DB_schema+"."+DB_table+" set \"chk_date\" = null WHERE id_0 = "+str(fID)
            cur.execute(dbkald)
            conn.commit()
        conn.commit()

        self.iface.mapCanvas().refresh()

        pass

    def qc_multiok(self):
        conn = psycopg2.connect(
            "dbname={name} user={user} host={host} password={pswd}".format(
                name=self.settings.value('db_name'),
                user=self.settings.value('db_user'),
                host=self.settings.value('db_host'),
                pswd=self.settings.value('db_password'),
            )
        )
        cur = conn.cursor()

        cLayer = self.iface.activeLayer()
        selection = cLayer.selectedFeatures()

        for feat in selection:
            fID = feat["Id_0"]
            dbkald = "update "+DB_schema+"."+DB_table+" set \"check_status\" = \'OK\' WHERE id_0 = "+str(fID)
            cur.execute(dbkald)
            dbkald = "update "+DB_schema+"."+DB_table+" set \"check_user\" = \'"+CHKuser+"\' WHERE id_0 = "+str(fID)
            cur.execute(dbkald)
            dbkald = "update "+DB_schema+"."+DB_table+" set \"chk_date\" = \'"+str(datetime.now())+"\' WHERE id_0 = "+str(fID)
            cur.execute(dbkald)
            conn.commit()
        conn.commit()

        self.iface.mapCanvas().refresh()

        pass

    def gcp_measure(self):

        self.canvas.setMapTool(self.clickTool)

        pass

    def gcp_mapclick(self, point, button):
        self.canvas.setMapTool(QgsMapToolPan(self.canvas))

        conn = psycopg2.connect(
            "dbname={name} user={user} host={host} password={pswd}".format(
                name=self.settings.value('db_name'),
                user=self.settings.value('db_user'),
                host=self.settings.value('db_host'),
                pswd=self.settings.value('db_password'),
            )
        )
        cur = conn.cursor()
        global ccdb_svar

        # QMessageBox.information(None, "type", DB_table)
        dbkald = "SELECT ST_AsText(ST_Centroid(geom)) FROM "+ DB_schema+"."+DB_table +" where id_0 = " +ccdb_svar
        cur.execute(dbkald)

        g_cent = str(cur.fetchone()[0])
        g_x = QgsGeometry.fromWkt(g_cent).asPoint().x()
        g_y = QgsGeometry.fromWkt(g_cent).asPoint().y()
        diff = math.sqrt((point.x()-g_x)*(point.x()-g_x)+(point.y()-g_y)*(point.y()-g_y))

        dbkald = "update "+DB_schema+"."+DB_table+" set \"g_x\" = \'"+str(g_x)+"\' WHERE id_0 = "+ccdb_svar
        cur.execute(dbkald)
        conn.commit()

        dbkald = "update "+DB_schema+"."+DB_table+" set \"g_y\" = \'"+str(g_y)+"\' WHERE id_0 = "+ccdb_svar
        cur.execute(dbkald)
        conn.commit()

        dbkald = "update "+DB_schema+"."+DB_table+" set \"m_x\" = \'"+str(point.x())+"\' WHERE id_0 = "+ccdb_svar
        cur.execute(dbkald)
        conn.commit()

        dbkald = "update "+DB_schema+"."+DB_table+" set \"m_y\" = \'"+str(point.y())+"\' WHERE id_0 = "+ccdb_svar
        cur.execute(dbkald)
        conn.commit()

        dbkald = "update "+DB_schema+"."+DB_table+" set \"diff_x\" = \'"+str(point.x()-g_x)+"\' WHERE id_0 = "+ccdb_svar
        cur.execute(dbkald)
        conn.commit()

        dbkald = "update "+DB_schema+"."+DB_table+" set \"diff_y\" = \'"+str(point.y()-g_y)+"\' WHERE id_0 = "+ccdb_svar
        cur.execute(dbkald)
        conn.commit()

        dbkald = "update "+DB_schema+"."+DB_table+" set \"diff\" = \'"+str(diff)+"\' WHERE id_0 = "+ccdb_svar
        cur.execute(dbkald)
        conn.commit()

        dbkald = "update "+DB_schema+"."+DB_table+" set \"check_status\" = \'OK\' WHERE id_0 = "+ccdb_svar
        cur.execute(dbkald)
        conn.commit()

        self.iface.mapCanvas().refresh()
        self.qc_nextstep()
        pass

    def update1(self):
        #if not self.isVisible():
        #    return
        layer = self.qcs.inShapeA.currentLayer()
        #self.qcs.inField1.clear()
        self.qcs.inField1.setLayer(layer)
        self.qcs.ortonamefield.setLayer(layer)
        #if layer:
        #    self.inField1.setField('description')
        self.qcs.radioButton_2.toggle()
        self.checkA()
        pass

    # def update_ortonamefield(self, inputLayer):
    #     changedLayer = ftools_utils.getVectorLayerByName(str(inputLayer))
    #     changedField = ftools_utils.getFieldList(changedLayer)
    #     self.qcs.ortonamefield.clear()
    #     for f in changedField:
    #         #if f.type() == QVariant.Int or f.type() == QVariant.String:
    #         self.qcs.ortonamefield.addItem(str(f.name()))
    #     pass

    def tableChanged(self):
        self.qcs.radioButton.toggle()
        pass

    def checkA(self):
        inputLayer = self.qcs.inShapeA.currentLayer()
        if inputLayer.selectedFeatureCount() != 0:
            print ("set checked")
            self.qcs.useSelectedA.setChecked(True)
        else:
            print ("set unchecked")
            self.qcs.useSelectedA.setChecked(False)
        pass

    def fillFailCodes(self):
        self.qcs.textEdit.clear()
        FailCodes = ['Ikke synlig\nIkke egnet\nTabtgaaet\nZ punkt']
        self.qcs.textEdit.insertPlainText(''.join(FailCodes))
