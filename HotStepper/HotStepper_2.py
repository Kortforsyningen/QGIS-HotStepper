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
from PyQt4.QtCore import * #QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import * #QAction, QIcon
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from datetime import datetime
#from osgeo import ogr

# Initialize Qt resources from file resources.py
import resources_rc

# Import the code for the dialog
from HotStepper_dialog import HotStepperDialog
from HotStepper_settings_dialog import HotStepper_settings
import os.path
import ftools_utils
import psycopg2
import getpass



#set global attributes
ccdb_svar = '1'
DB_name = "oeffegris"
DB_host = "localhost"
DB_port = "5432"
DB_user = "postgres"
DB_pass = "postgres"

DB_schema = "public"
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

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&HotStepper')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'HotStepper')
        self.toolbar.setObjectName(u'HotStepper')
        
	#set user
	CHKuser = getpass.getuser()

        
        #setup DB connection
	dbname = 'oeffegris'
	user = 'postgres'
	host = 'localhost'
	password = 'postgres'
	
	#conn = psycopg2.connect("dbname="+dbname+" user="+user+" host="+host+" password="+password)
	#cur = conn.cursor()
        
        # Setup keyboard shortcuts
        def short_ok():
            self.qc_ok()
            
        short = QShortcut(QKeySequence(Qt.ALT + Qt.Key_1), iface.mainWindow())
        short.setContext(Qt.ApplicationShortcut)
        short.activated.connect(short_ok)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
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
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

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
            text=self.tr(u'Go to next'),
            callback=self.qc_nextstep,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/HotStepper/ok.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Mark OK and go to next'),
            callback=self.qc_ok,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/HotStepper/fail.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Mark fail'),
            callback=self.qc_fejl,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/HotStepper/reset.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Reset check state'),
            callback=self.qc_reset,
            parent=self.iface.mainWindow())
            
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&HotStepper'),action)
            self.iface.removeToolBarIcon(action)

    def qc_setup(self):
        global DB_name
	global DB_host
	global DB_port
	global DB_user
	global DB_pass
	
	global DB_schema
	global DB_table
	global DB_geom
	global ccdb_svar
	global FailCodes
	    
        """Run method that performs all the real work"""
        # show the dialog
        self.qcs.show()
        self.qcs.radioButton.toggle()
        layers = ftools_utils.getLayerNames([QGis.Point, QGis.Line, QGis.Polygon])
        self.qcs.inShapeA.clear()
        self.qcs.inShapeA.addItems(layers)
        QObject.connect(self.qcs.inShapeA, SIGNAL("currentIndexChanged(QString)" ), self.update1 )
        QObject.connect(self.qcs.inShapeA, SIGNAL("currentIndexChanged(QString)" ), self.checkA )

        self.qcs.textEdit.clear()
        FailCodes = ['Clouds\nBridge\nBuilding'] 
        self.qcs.textEdit.insertPlainText(''.join(FailCodes))

        #list available PostgreSQL tables
        conn = psycopg2.connect("dbname="+DB_name+" user="+DB_user+" host="+DB_host+" password="+DB_pass)
        cur = conn.cursor()
        cur.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")    
        rows = cur.fetchall()

        tableList = []
        for e in rows:
            if "chk_" in e[0]: 
                tableList.append(e[0])

        #QMessageBox.information(None, "test input", os.path.dirname(__file__))        
        
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

                uri = QgsDataSourceURI()
                uri.setConnection(DB_host, DB_port, DB_name, DB_user, DB_pass)
                uri.setDataSource(DB_schema, DB_table, DB_geom,"")
                uri.uri()
                iface.addVectorLayer(uri.uri(), DB_table, "postgres")

                #set styling
                DBlaget = self.iface.activeLayer()
                
                DBlaget.loadNamedStyle(os.path.dirname(__file__)+"\\Polygons.qml")


                ccdb_svar = 1  

                dbkald = "SELECT failcodes FROM "+DB_table.replace("chk_", "err_")+" WHERE id_0 = 1"
                cur.execute(dbkald)
                FailCodes = str(cur.fetchone()[0]).split("\n")
                
                        
            if self.qcs.radioButton_2.isChecked():
                inputFilNavn = self.qcs.inShapeA.currentText()
                inputField = self.qcs.inField1.currentText()
                FailCodes = self.qcs.textEdit.toPlainText() 
                QMessageBox.information(None, "test input", FailCodes)

                try:
                    conn = psycopg2.connect("dbname="+DB_name+" user="+DB_user+" host="+DB_host+" password="+DB_pass)
                    cur = conn.cursor()
                    
                    DB_table ="chk_"+self.qcs.inTableName.text()
                    ligenu = str(datetime.now()) 
                    
                    #her arbejdes
                    cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (DB_table,))
                    if cur.fetchone()[0]:
                        DB_table = DB_table+str(1)
                    
                    #Create failcodes DB
                    cur.execute("CREATE TABLE "+DB_table.replace("chk_", "err_")+"(Id_0 INTEGER PRIMARY KEY,failcodes text)")
                    conn.commit()
                    cur.execute("INSERT INTO "+DB_table.replace("chk_", "err_")+" VALUES( 1 , \'"+FailCodes+"\' );")
                    conn.commit()


                    cur.execute("CREATE TABLE "+DB_table+"(Id_0 INTEGER PRIMARY KEY,JoinID text, check_status text, check_user text, chk_date timestamp without time zone, chk_comment text, fail_code text, geom geometry)")
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
                               geom = feat.geometry()
                               JoinID = feat[inputField]
                               cur.execute("INSERT INTO "+DB_table+" VALUES("+str(tableID)+",'"+JoinID+"','pending',null,null,null,null,ST_GeomFromText('"+geom.exportToWkt()+"'));")
                               tableID = tableID+1
                    
                    conn.commit()

                    uri = QgsDataSourceURI()
                    uri.setConnection(DB_host, DB_port, DB_name, DB_user, DB_pass)
                    uri.setDataSource(DB_schema, DB_table, DB_geom,"")
                    uri.uri()
                    iface.addVectorLayer(uri.uri(), DB_table, "postgres")
                    ccdb_svar = 1
               
                except psycopg2.DatabaseError, e:
                    
                    if conn:
                        conn.rollback()
                    
                    print 'Error %s' % e    
                    sys.exit(1)
                    
                finally:
                    
                    if conn:
                        conn.close()

            pass

    def qc_nextstep(self):
        conn = psycopg2.connect("dbname="+DB_name+" user="+DB_user+" host="+DB_host+" password="+DB_pass)
        cur = conn.cursor()
        global ccdb_svar

        try:
            dbkald = "SELECT id_0 FROM "+DB_table+" WHERE \"check_status\" = \'pending\' OR (\"check_status\" = \'locked\' AND \"check_user\" = \'"+CHKuser+"\') ORDER BY \"chk_date\""
            cur.execute(dbkald)
            ccdb_svar = str(cur.fetchone())
            ccdb_svar = ccdb_svar.strip("(").strip(")").strip(",")

            dbkald = "update "+DB_table+" set \"check_status\" = \'locked\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)            
            conn.commit()
            dbkald = "update "+DB_table+" set \"check_user\" = \'"+CHKuser+"\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)            
            conn.commit()
            dbkald = "update "+DB_table+" set \"chk_date\" = \'"+str(datetime.now())+"\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)            
            conn.commit()

            #zoom til feature
            dbkald = "SELECT st_astext(geom) FROM "+DB_table+" WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)
            geometri = str(cur.fetchone()[0])
        
            gem = QgsGeometry.fromWkt(geometri)
            box = gem.boundingBox()
            iface.mapCanvas().setExtent(box)
            iface.mapCanvas().refresh()
        except(psycopg2.ProgrammingError):
            QMessageBox.information(None, "QC info", 'All done, nothing to check')
        pass

    def qc_ok(self):
        conn = psycopg2.connect("dbname="+DB_name+" user="+DB_user+" host="+DB_host+" password="+DB_pass)
        cur = conn.cursor()
        global ccdb_svar
        #set aktuelle feature til ok
        dbkald = "update "+DB_table+" set \"check_status\" = \'OK\' WHERE id_0 = "+ccdb_svar
        cur.execute(dbkald)
        conn.commit()
        
        self.iface.mapCanvas().refresh()
        self.qc_nextstep()
        pass

    def qc_fejl(self):
        conn = psycopg2.connect("dbname="+DB_name+" user="+DB_user+" host="+DB_host+" password="+DB_pass)
        cur = conn.cursor()
        global ccdb_svar
        #set aktuelle feature til fail
        self.dlg.show()

        #FailCodes = ['Clouds\nBridge\nBuilding']
        self.dlg.comboBox.clear()
        self.dlg.comboBox.addItems(FailCodes)

        result = self.dlg.exec_()

	if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.


           #dbkald = "update tiletest_kontrol set \"check_status\" = \'Fail\' WHERE id_0 = "+self.ccdb_svar
            dbkald = "update "+DB_table+" set \"check_status\" = \'Fail\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)
            conn.commit()

           #dbkald = "update tiletest_kontrol set \"fail_code\" = \'" + self.dlg.comboBox.currentText() +"\' WHERE id_0 = "+self.ccdb_svar
            dbkald = "update "+DB_table+" set \"fail_code\" = \'" + self.dlg.comboBox.currentText() +"\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)
            conn.commit()

            dbkald = "update "+DB_table+" set \"chk_date\" = \'"+str(datetime.now())+"\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)            
            conn.commit()

           #dbkald = "update tiletest_kontrol set \"chk_comment\" = \'" + self.dlg.textEdit.toPlainText() +"\' WHERE id_0 = "+self.ccdb_svar
            dbkald = "update "+DB_table+" set \"chk_comment\" = \'" + self.dlg.textEdit.toPlainText() +"\' WHERE id_0 = "+ccdb_svar
            cur.execute(dbkald)
            conn.commit()   
        
            self.iface.mapCanvas().refresh()
            self.qc_nextstep()
            pass
            
    def qc_genlaes(self):
        global ccdb_svar

        dbkald = "update "+DB_table+" set \"check_status\" = \'Fail\' WHERE id_0 = "+ccdb_svar
        cur.execute(dbkald)
        conn.commit()
        
        self.iface.mapCanvas().refresh()
            
        pass

    def qc_reset(self):
        conn = psycopg2.connect("dbname="+DB_name+" user="+DB_user+" host="+DB_host+" password="+DB_pass)
        cur = conn.cursor()

        #canvas = self.iface.mapCanvas()
        #allLayers = canvas.layers()
        
        cLayer = self.iface.activeLayer()
        selection = cLayer.selectedFeatures()

        for feat in selection:
            fID = feat["Id_0"]
            #QMessageBox.information(None, "test input", "+str(tableID)+",'pending',null,null,null,ST_GeomFromText('"+geom.exportToWkt()+"'));")
            dbkald = "update "+DB_table+" set \"check_status\" = \'pending\' WHERE id_0 = "+str(fID)
            cur.execute(dbkald)
        conn.commit()

        self.iface.mapCanvas().refresh()
            
        pass

        
    def update1(self, inputLayer):
        self.qcs.inField1.clear()
        changedLayer = ftools_utils.getVectorLayerByName(unicode(inputLayer))
        changedField = ftools_utils.getFieldList(changedLayer)
        for f in changedField:
            if f.type() == QVariant.Int or f.type() == QVariant.String:
                self.qcs.inField1.addItem(unicode(f.name()))
        pass

    def checkA(self):
        inputLayer = unicode( self.qcs.inShapeA.currentText() )
        if inputLayer != "":
            changedLayer = ftools_utils.getVectorLayerByName( inputLayer )
        if changedLayer.selectedFeatureCount() != 0:
            self.qcs.useSelectedA.setCheckState( Qt.Checked )
        else:
            self.qcs.useSelectedA.setCheckState( Qt.Unchecked )
        pass