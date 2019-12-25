# coding=utf-8
from __future__ import division  # this causes interger division to return a floating point (decimal)
                                 # number instead of throwing away the remainder, if any.
import traceback
import datetime
pyside2 = False
try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    pyside2 = True
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *


import os.path
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

thisDir = os.path.dirname(__file__)
VERSION_FILE_PATH = os.path.join(thisDir, 'version.txt')

PROGRAM_VERSION = ""
try:
    with open(VERSION_FILE_PATH, 'r') as f:
        PROGRAM_VERSION = f.read().strip()
except IOError:
    pass

entry_width = 4
app = F = M = C = P = icon = None
err_string = "Bad Input"

connect = QObject.connect

# set to an object holding config data for the application
config = None

class SingleEntryDialog(QDialog):
    def __init__(self, caption, description, default):
        self.description = description
        QDialog.__init__(self)
        self.setFont(F.std)

        self.setWindowTitle(caption)
        self.setWindowIcon(icon)

        vbox_layout = QVBoxLayout(self)

        # first row
        hbox = QWidget(self)
        hbox_layout = QHBoxLayout(hbox)
        hbox.setLayout(hbox_layout)
        vbox_layout.addWidget(hbox)

        self.label = QLabel(description, self)
        hbox_layout.addWidget(self.label)

        self.entry = AutoEntry(hbox)
        self.entry.setText(default)
        hbox_layout.addWidget(self.entry)

        # second row
        hbox = QWidget(self)
        hbox_layout = QHBoxLayout(hbox)
        hbox.setLayout(hbox_layout)
        vbox_layout.addWidget(hbox)

        btn = QPushButton("OK", hbox)
        hbox_layout.addWidget(btn)
        btn.setFixedSize(btn.sizeHint())
        connect(btn, SIGNAL("clicked()"), self, SLOT("accept()"))

        btn = QPushButton("Cancel", hbox)
        hbox_layout.addWidget(btn)
        btn.setFixedSize(btn.sizeHint())
        connect(btn, SIGNAL("clicked()"), self, SLOT("reject()"))

        self.setLayout(vbox_layout)

        self.setFixedHeight(self.sizeHint().height())
        self.setMaximumWidth(self.sizeHint().width() + 50)


class MsgBox(QMessageBox):
    def __init__(self, *args):
        QMessageBox.__init__(self, *args)
        self.setFont(F.std)
        self.setWindowIcon(icon)


class Configuration(object):
    section = "EngUtils"
    floatPrecision = 3
    def __init__(self):
        """
        Initialize config from INI file
        """
        appData = os.getenv('APPDATA')
        if appData:
            self.configPath = os.path.join(appData, 'EngUtils', 'config.ini')
        else:
            self.configPath = os.path.expanduser(os.path.join('~', '.EngUtils', 'config.ini'))

        if not os.path.exists(self.configPath):
            return

        with open(self.configPath, 'r') as f:
            cfg = ConfigParser()
            cfg.readfp(f)

            if cfg.has_section(self.section):
                self.floatPrecision = cfg.getint(self.section, "floatPrecision")

            f.close()

    def save(self):
        """
        Save config to INI file
        """

        # ensure config dir exists
        dirPath = os.path.dirname(self.configPath)
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)

        with open(self.configPath, 'w') as f:
            cfg = ConfigParser()
            if not cfg.has_section(self.section):
                cfg.add_section(self.section)

            cfg.set(self.section, "floatPrecision", self.floatPrecision)

            cfg.write(f)
            f.close()

    def promptFloatPrecision(self):
        """
        Prompt user to enter how many decimal places they would like to be shown
        for floating-point results.
        """
        dialog = SingleEntryDialog("Set Option", "Number of decimal-places to show: ",
                                   str(self.floatPrecision))
        result = dialog.exec_()

        if result == QDialog.Accepted:
            try:
                self.floatPrecision = int(str(dialog.entry.text()))
            except ValueError:
                msgBox = MsgBox(MsgBox.NoIcon, u"Error", u"Invalid Input. Integer only please.")
                msgBox.exec_()
                return

            self.save()


def showAboutDialog():
    # thwart scrapers
    import base64
    email = base64.decodestring(b'dGVyYXRvcm5Aem9oby5jb20=\n').decode('utf-8')
    msgBox = MsgBox(MsgBox.NoIcon, u"Engineering Utilities - About",
                    u"Written by Eric P. Mangold  --  {}\n\n"
                    u"Version: {}\n\n"
                    u"Please contact for commercial licensing."
                    .format(email, PROGRAM_VERSION))
    msgBox.exec_()


if not pyside2:
    class Cleanlooks(QCleanlooksStyle):
        def styleHint(self, hint, option, widget, returnData):
            # change the color of table grid lines
            if hint == QStyle.SH_Table_GridLineColor:
                return int(C.grid_line.rgba() - 2**31)
            return QCleanlooksStyle.styleHint(self, hint, option, widget, returnData)

        def standardPixmap(self, *args):
            """
            Just a hack to prevent crash because calling menuBar() on the QMainWindow
            results in a call to this method, for some reason, which if unimplemented,
            results in error:

            NotImplementedError: pure virtual method 'QCleanlooksStyle.standardPixmap()' not implemented.
            """
            # just give it any old QPixmap to make it happy... doesn't appear
            # to actually be displayed anywhere.
            return QPixmap()


class CalculatorApp(QApplication):
    def __init__(self, title):
        QApplication.__init__(self, [])

        if pyside2:
            QApplication.setStyle('Fusion')
        else:
            style = Cleanlooks()
            QApplication.setStyle(style)
        global app, F, M, C, P, icon
        app = self
        F = Fonts()
        M = Metrics()
        C = Colors()
        P = Palettes()

        global config
        config = Configuration()

        main = self.main = QMainWindow()
        main.setFont( F.std )
        main.setWindowTitle(title)

        iconPath = os.path.join(os.path.dirname(__file__), "icon.png")
        icon = QIcon(iconPath)
        main.setWindowIcon(icon)

        self.top = QTabWidget()
        self.top.sizeHint = lambda: QSize(1280, 900)

        main.setCentralWidget(self.top)

        menuBar = main.menuBar()
        menuBar.setFont(F.std)

        fileMenu = menuBar.addMenu("&File")
        quitAction = fileMenu.addAction("&Quit")
        quitAction.setFont(F.std)

        connect(quitAction, SIGNAL("triggered()"), main.close)

        optMenu = menuBar.addMenu("&Options")
        floatPrecisionAction = optMenu.addAction("&Floating-point display precision...")
        floatPrecisionAction.setFont(F.std)
        connect(floatPrecisionAction, SIGNAL("triggered()"), config.promptFloatPrecision)

        helpMenu = menuBar.addMenu("&Help")
        aboutAction = helpMenu.addAction("&About...")
        aboutAction.setFont(F.std)
        connect(aboutAction, SIGNAL("triggered()"), showAboutDialog)


    def exec_(self):
        QTimer.singleShot(1000, self.checkFathersDay)
        QTimer.singleShot(1000, self.checkBirthday)

        self.main.show()
        QApplication.exec_()


    def checkBirthday(self):
        today = datetime.date.today()
        birthday = datetime.date(today.year, 9, 11)

        if today == birthday:
            msgBox = MsgBox(MsgBox.NoIcon, u"Eng Utils", u"Happy Birthday!")
            msgBox.exec_()


    def checkFathersDay(self):
        #testData = [ (2010, datetime.date(2010, 6, 20)),
        #             (2011, datetime.date(2011, 6, 19)),
        #             (2012, datetime.date(2012, 6, 17)) ]

        #for year, expectedDate in testData:
        #    print year
        #    got = self.getFathersDay(year)
        #    if got != expectedDate:
        #        print "Got %s but expected %s" % (got, expectedDate)

        today = datetime.date.today()
        fathersDay = self.getFathersDay(today.year)

        if today == fathersDay:
            msgBox = MsgBox(MsgBox.NoIcon, u"Eng Utils", u"Happy Fathers Day!")
            msgBox.exec_()


    def getFathersDay(self, year):
        june1 = datetime.date(year, 6, 1)
        june1dow = june1.weekday() # day of week integer for june1

        # how far from sunday?
        daysBeforeSunday = 6 - june1dow # will be 0 if june1 is a Sunday

        fathersDay = datetime.date(year, 6, 1 + daysBeforeSunday + 14) # 3rd Sunday in June
        return fathersDay


class NotebookPage(QTabWidget):
    def __init__(self, parent, name, caption=None):
        QTabWidget.__init__(self)

        w = self
        w_layout = QVBoxLayout(w)

        if caption:
            cw = QWidget(w)
            w_layout.addWidget(cw)
            cl = QVBoxLayout(cw)
            lbl = QLabel(caption, cw)
            cl.addWidget(lbl, 0, Qt.AlignCenter|Qt.AlignTop)
            cw.setLayout(cl)

        w.setLayout(w_layout)

        parent.addTab(w, name)


class CalculatorPage(QWidget):
    def __init__(self, parent, name, caption, *args):
        QWidget.__init__(self)
        self.setParent(parent)
        layout = QVBoxLayout(self)

        self._name = name
        self._caption = caption

        self._entries = []
        self._outputs = []

        for a in args:
            if isinstance(a, Entry):
                self._entries.append(a)
            elif isinstance(a, Output):
                self._outputs.append(a)
            elif type(a) == type(smartEval):
                self.calcFunction = a

        if isinstance(caption, QWidget):
            caption.postInit(self)
            layout.addWidget(caption, 0, Qt.AlignTop|Qt.AlignLeft)
        else:
            lbl = QLabel(caption, self)
            layout.addWidget(lbl, 0, Qt.AlignTop|Qt.AlignCenter)

        scroll = QScrollArea(self)
        # don't give the scroll an alignment within the layout,
        # so that it will expand to fill available space
        layout.addWidget(scroll, 1)

        hbox = QWidget()
        hbox_layout = QHBoxLayout()

        # a widget to hold the grid of entry and output widgets for the calculation
        gridw = QWidget(hbox)
        hbox_layout.addWidget(gridw)

        gridl = QGridLayout(gridw)
        gridl.setVerticalSpacing(0)

        row = 0
        col = 0
        for entry in self._entries:
            entry.postInit(gridw, gridl, row)
            row += 1

        # a widget to hold the horizontal set of buttons
        # "Calculate", "New", and "Clear"
        btnfrm = QWidget(gridw)
        btnfrm_layout = QHBoxLayout()
        btnfrm_layout.setSpacing(5)
        gridl.addWidget(btnfrm, row, col+1, 1, 2, Qt.AlignLeft)
        row += 1

        btn = QPushButton("Calculate", btnfrm)
        btnfrm_layout.addWidget(btn)
        btn.setFixedSize(btn.sizeHint())
        connect(btn, SIGNAL("clicked()"), self.doCalculation)

        btn = QPushButton("New", btnfrm)
        btnfrm_layout.addWidget(btn)
        btn.setFixedSize(btn.sizeHint())
        connect(btn, SIGNAL("clicked()"), self.newProblem)

        btn = QPushButton("Clear", btnfrm)
        btnfrm_layout.addWidget(btn)
        btn.setFixedSize(btn.sizeHint())
        connect(btn, SIGNAL("clicked()"), self.clear)

        # add widgets for output lines
        lbl = QLabel("Output:", gridw)
        lbl.setFont(F.big)
        lbl.setPalette(P.ready_text)
        gridl.addWidget(lbl, row, col)

        row += 1

        for output in self._outputs:
            # if there are more than 13 total rows so far
            # in the current grid, then start a new grid
            # adjacent (to the right of) the current grid.
            if row > 13:
                row = 0

                gridw = QWidget(hbox)
                hbox_layout.addWidget(gridw)
                gridl = QGridLayout(gridw)

            output.postInit(gridw, gridl, row)
            row += 1

        gridl.setColumnStretch(0,0)
        gridl.setColumnStretch(1,0)
        gridl.setColumnStretch(2,1)

        self.statusLine = QLabel("Ready", self)
        layout.addWidget(self.statusLine, 0, Qt.AlignBottom|Qt.AlignLeft)
        self.statusLine.setFont(F.big)
        self.statusLine.setPalette(P.ready_text)

        hbox.setLayout(hbox_layout)
        btnfrm.setLayout(btnfrm_layout)

        scroll.setWidget(hbox)
        self.setLayout(layout)
        parent.addTab(self, name)

    def doCalculation(self):
        entry_values = []

        try:
            for entry in self._entries:
                entry_values.append( entry.getValue() )

            results = self.calcFunction(*entry_values)


            #if results is not a tuple(ie, the function only returned one value),
            #change it into one to fit the processing code below
            if type(results) != tuple:
                results = (results,)
            #check the lenght of results to ensure we got a value for each output box
            if len(results) != len(self._outputs):
                raise TypeError("Error: Calculation function returned %s values (expected %s)" % (len(results), len(self._outputs)))

            #tell the output objects to display the results
            for i in range(len(results)):
                self._outputs[i].setValue( results[i] )
                self._outputs[i].enableCopyButton()

        except Exception as e:
            self.statusLine.setText(e.__class__.__name__+": "+str(e))
            self.statusLine.setPalette(P.err_text)
            print(traceback.format_exc())
            return

        #disable the entry boxes until the New button is clicked
        for entry in self._entries:
            entry.disable()

        #were done
        self.statusLine.setText("Done")
        self.statusLine.setPalette(P.ready_text)

    def newProblem(self):
        for entry in self._entries:
            entry.enable()
        self._entries[0].focus()
        for output in self._outputs:
            output.clear()
            # disable Copy buttons
            output.disableCopyButton()

        self.statusLine.setText("Ready")
        self.statusLine.setPalette(P.ready_text)

    def clear(self):
        self.newProblem()
        for entry in self._entries:
            entry.clear()


def smartEval(s):

    if not s:
        raise ValueError(err_string)

    if "d" in s or "'" in s or "\"" in s:
        # Parse AutoCAD-style degree/minute/second notation in to a floating-point value
        # that contains whole and fractional degrees.

        degs = 0.0
        mins = 0.0
        secs = 0.0

        parts = s.split("d")
        if len(parts) > 2:
            raise ValueError(err_string)

        if len(parts) == 2:
            # yes there is a degrees portion
            try:
                degs = float(parts[0])
            except ValueError:
                raise ValueError(err_string)

            if "." in parts[0]:
                # degrees was given as a decimal - so nothing else is allowed after the "d"
                if len(parts[1]) != 0:
                    raise ValueError(err_string)

            parts = parts[1].split("'")
        else:
            # no degrees portion given
            parts = parts[0].split("'")

        if len(parts) > 2:
            raise ValueError(err_string)

        if len(parts) == 2:
            # yes there is a minutes portion
            try:
                mins = float(parts[0])
            except ValueError:
                raise ValueError(err_string)

            parts = parts[1].split("\"")
        else:
            parts = parts[0].split("\"")

        if len(parts) > 2:
            raise ValueError(err_string)

        if len(parts) == 2:
            try:
                secs = float(parts[0])
            except ValueError:
                raise ValueError(err_string)

            # nothing should follow the ' char
            if len(parts[1]) != 0:
                raise ValueError(err_string)

        else:
            # should not be anything left at this point
            if len(parts[0]) != 0:
                raise ValueError(err_string)

        result = degs
        result += mins / 60
        result += secs / 60 / 60
        if result > 360:
            raise ValueError(err_string)

        return result

    else:
        try:
            return eval(s)
        except:
            raise ValueError(err_string)


class AutoEntry(QLineEdit):  #a line entry that has a minimum width (in characters), and expands when that is exceeded by typed in text
    def __init__(self, *args, **kwargs): # width=default, font=BoxFont
        QLineEdit.__init__(self, *args)

        if "width" in kwargs:
            self._minwidth_chars = kwargs["width"]
        else:
            self._minwidth_chars = entry_width

        self._minwidth = M.box.width("M"*self._minwidth_chars+"M") #just use any char that takes up the max char width of the font
        self._curwidth = self._minwidth

        self.setFont(F.box)
        self.setFixedWidth(self._minwidth)
        connect(self, SIGNAL("textChanged(const QString &)"), self.onTextChanged)
    def onTextChanged(self, string): #get's passed a QString of the new contents of the entry box when it changes
        string = str(string) #make it into a python string to save my sanity
        if len(string) > self._minwidth_chars: #no need to check width if it can't be too wide
            w = M.box.width(string+"M")
            if w > self._minwidth:
                self.setFixedWidth(w)
                self._curwidth = w
                return
        if self._minwidth != self._curwidth:
            self.setFixedWidth(self._minwidth)
            self._curwidth = self._minwidth


class Entry(object):
    pass


class EntryLine(Entry):
    def __init__(self, label, units="", default=""):
        self.label = label
        self.units = units
        self.default = default

    def postInit(self, parent, layout, row):
        lbl = QLabel(self.label, parent)
        layout.addWidget(lbl, row, 0, Qt.AlignLeft)

        frmw = QWidget(parent)
        #frml = QHBoxLayout(frmw, 1, 1)
        frml = QHBoxLayout(frmw)

        layout.addWidget(frmw, row, 1, 1, 2, Qt.AlignLeft|Qt.AlignBottom)

        self.box = AutoEntry(frmw)
        self.box.setText(self.default)
        frml.addWidget(self.box, 0, Qt.AlignLeft)

        lbl = QLabel(self.units, frmw)
        frml.addWidget(lbl, 0, Qt.AlignLeft)
        self.enable()

    def getValue(self):
        return smartEval(str(self.box.text()))

    def enable(self):
        self.box.setReadOnly(0)
        self.box.setPalette(P.normal)

    def disable(self):
        self.box.setReadOnly(1)
        self.box.setPalette(P.entry_disabled)

    def focus(self):
        self.box.setFocus()
        self.box.setSelection(0, len(self.box.text()))

    def clear(self):
        self.box.clear()


class FixedEntryTable(object):
    def __init__(self, name, num_rows, *args):
        pass


class Output(object):
    pass


class OutputLine(Output):
    def __init__(self, label, units=""):
        self.label = label
        self.units = units

    def postInit(self, parent, layout, row):
        lbl = QLabel(self.label, parent)
        layout.addWidget(lbl, row, 0, Qt.AlignRight)

        frmw = QWidget(parent)
        frml = QHBoxLayout(frmw)

        layout.addWidget(frmw, row, 1, Qt.AlignLeft|Qt.AlignBottom)

        self.box = OutputBox(frmw)
        frml.addWidget(self.box, 0, Qt.AlignLeft)

        lbl = QLabel(self.units, frmw)
        frml.addWidget(lbl, 0, Qt.AlignLeft)

        self.copyButton = btn = QPushButton("Copy", frmw)
        layout.addWidget(btn, row, 2, Qt.AlignLeft|Qt.AlignVCenter)
        btn.setFixedSize(btn.sizeHint())
        connect(btn, SIGNAL("clicked()"), self.copyToClipboard)
        self.disableCopyButton()

    def setValue(self, value): #this should get the value as an interger or float, or whatever. we're responsible for sensable formatting
        if type(value) == float:
            fmt = "%%0.%df" % (config.floatPrecision,)
            r = fmt % value
        else:
            r = str(value)
        self.box.setText(r)

    def clear(self):
        self.box.clear()

    def enableCopyButton(self):
        self.copyButton.setEnabled(True)

    def disableCopyButton(self):
        self.copyButton.setEnabled(False)

    def copyToClipboard(self):
        text = self.box.text()
        clip = QApplication.clipboard()
        clip.setText(text)


class MyEditorFilter(QObject):
    def __init__(self, table):
        QObject.__init__(self)
        self._table = table

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            table = self._table
            row = table.currentRow()
            col = table.currentColumn()
            key = event.key()
            if key in (Qt.Key_Return, Qt.Key_Enter):
                # if on last row
                if row == table.rowCount()-1:
                    table.appendRow()
                table.setCurrentCell(row+1, col)
            elif key == Qt.Key_Tab:
                pass

            return True
        else:
            # standard event processing
            return QObject.eventFilter(self, obj, event)


class MyLineEdit(QLineEdit):
    def __init__(self, parent, table):
        QLineEdit.__init__(self, parent)
        self._table = table

    def keyPressEvent(self, event):
        if event.type() == QEvent.KeyPress:
            key = event.key()
            return QLineEdit.keyPressEvent(self, event)

            table = self._table
            row = table.currentRow()
            col = table.currentColumn()
            if key in (Qt.Key_Return, Qt.Key_Enter):
                # if on last row
                if row == table.rowCount()-1:
                    table.appendRow()
                table.setCurrentCell(row+1, col)
                return
            elif key == Qt.Key_Tab:
                return

        return QLineEdit.keyPressEvent(self, event)

    def focusNextPrevChild(self, next):
        return QLineEdit.focusNextPrevChild(self, next)


class MyStringEditorCreator(QItemEditorCreatorBase):
    def __init__(self, table):
        self._table = table
        QItemEditorCreatorBase.__init__(self)

    def createWidget(self, parent):
        parent.installEventFilter(MyEditorFilter(self._table))
        return MyLineEdit(parent, self._table)

    def valuePropertyName(self):
        name = QItemEditorCreatorBase.valuePropertyName(self)
        return name


class MyItemEditorFactory(QItemEditorFactory):
    def __init__(self, table):
        self._table = table
        QItemEditorFactory.__init__(self)

        if pyside2:
            self.registerEditor(0, MyStringEditorCreator(self._table))
            self.registerEditor(1, MyStringEditorCreator(self._table))
        else:
            self.registerEditor(str, MyStringEditorCreator(self._table))
            self.registerEditor(unicode, MyStringEditorCreator(self._table))


class EntryTable(Entry, QTableWidget):
    """
    represents a spreadsheet like table for taking input, will auto create new rows as needed
    """
    # ----- Begin overloaded methods -----
    def __init__(self, name, *args):
        self._name = name
        self._col_names = args
        self._num_cols = len(args)
        QTableWidget.__init__(self, 0, self._num_cols)

        self._read_only_flag = 0
        self._header_height = 27 #record these the first time we add a row. used later to ensure sizeHint is accurate.
        self._row_height = 20

    def sizeHint(self):
        h = QTableWidget.sizeHint(self)
        hi = h.height()
        if ((self._header_height+self._row_height*self._num_cols) - hi ) > 20: #compensate if there if there is a horizontal scroll bar taking up space
            h.setHeight( h.height() + 40 )
        h.setWidth(h.width() + 256)
        return h

    def keyPressEvent(self, event):
        #import pdb;pdb.set_trace()

        row = self.currentRow()
        col = self.currentColumn()

        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            # if on last row
            if row == self.rowCount()-1:
                self.appendRow()
            self.setCurrentCell(row+1, col)
            return
        elif key == Qt.Key_Tab:
            if col == self.columnCount()-1:
                if row == self.rowCount()-1:
                    self.appendRow()
                self.setCurrentCell(row+1, 0)
                return
        elif key in (Qt.Key_Backspace, Qt.Key_Delete):
            for i in range(self.columnCount()):
                if str(self.item(row,i).text()):
                    # found some text in this row, so we aren't going to remove the row
                    # Just clear the current cell (current cell might be empty, but that's OK)
                    self.item(row,col).setText(u'')
                    return
            # all cells in row are empty; delete the row unless it's the only row in the table
            if self.rowCount() > 1:
                self.removeRow(row)
                if row <= self.rowCount()-1:
                    self.setCurrentCell(row, col)
                else:
                    self.setCurrentCell(row-1, col)
                return
        return QTableWidget.keyPressEvent(self, event)

    # ----- Begin personal methods
    def setCurrentCell(self, row, col):
        QTableWidget.setCurrentCell(self, row, col)

    def setReadOnly(self, b):
        if b:
            self.currentItem().setSelected(False)
            self.setEnabled(False)
            self._read_only_flag = 1
        else:
            self.setEnabled(True)
            self._read_only_flag = 0

    def appendRow(self):
        rows = self.rowCount()
        self.setRowCount(rows+1)
        for i in range(self._num_cols):
            self.setItem(rows, i, QTableWidgetItem() )
        self.updateGeometry()

    def clearLastRow(self):
        row = self.rowCount()-1
        for col in range(self.numCols()):
            self.clearCell(row, col)
        self.setRowCount( row )
        self.updateGeometry()
        self.setCurrentCell(row-1, 0)
        self.ensureCellVisible(row-1, 0)
        self.verticalHeader().repaint() #erase the header buttons that were getting left behind

    def headerResized(self, section, oldSize, newSize):
        self.updateGeometry()

    # ----- Begin Entry interfaces -----

    def postInit(self, parent, layout, row):
        #self.setGridStyle(Qt.DashDotDotLine)
        self.setFont(F.box)

        self.installEventFilter(MyEditorFilter(self))

        if not self.itemDelegate().itemEditorFactory():
            fac = MyItemEditorFactory(self)
            self.itemDelegate().setItemEditorFactory(fac)

        mainw = QWidget(parent)
        mainl = QVBoxLayout()

        mainl.addWidget(QLabel(self._name, mainw))


        self.setParent(mainw)

        width = 0
        for i in range(self.columnCount()):
            width += self.columnWidth(i)
        width += 22

        self.setFixedSize( QSize(width, self.sizeHint().height()) )
        mainl.addWidget(self)
        mainw.setLayout(mainl)

        h = self.horizontalHeader()
        if pyside2:
            h.setSectionsMovable(False)
        else:
            h.setMovable(False)

        # TODO - fix this if it's actually necessary
        #connect(h, SIGNAL("sizeChange(int,int,int)"), self.headerResized)

        self.setHorizontalHeaderLabels(self._col_names)

        h = self.verticalHeader()
        if pyside2:
            h.setSectionsMovable(False)
        else:
            h.setMovable(False)

        self.appendRow()

        layout.addWidget(mainw, row, 0, 1, 3, Qt.AlignLeft|Qt.AlignTop)

        self.enable()

    def getValue(self): #return the evaluated contents of the widget, or raise an exception on error
        rows = self.rowCount()
        r = []

        for row in range(rows):
            l = []
            for col in range(self._num_cols):
                item = self.item(row,col)
                if not item: raise ValueError(err_string)
                l.append( smartEval( str(item.text()) ) )
            r.append( tuple(l) )
        return tuple(r)

    def enable(self):
        self.setPalette(P.normal)
        self.setReadOnly(0)
        self.repaint()

    def disable(self):
        self.setReadOnly(1)
        self.setPalette(P.entry_disabled)
        self.repaint()

    def focus(self):
        pass

    def clear(self):
        self.setRowCount(1)
        for i in range(self.columnCount()):
            self.item(0, i).setText("")


class Picture(QWidget):
    """
    For displaying images - currently unused and may be broken
    """
    def __init__(self, file_name, caption=None, orient="left"):
        QWidget.__init__(self)
        self.file_name = file_name
        self.caption = caption
        self.orient = orient

    def postInit(self, parent):
        self.setParent(parent)

        pix = QPixmap()
        if not pix.load(self.file_name):
            if not pix.load( "images/" + self.file_name ):
                print("Load of image, %s, failed!" % self.file_name)
                return
        pic = QLabel(self)
        pic.setPixmap(pix)

        if self.caption:
            lbl = QLabel(self.caption, self)
            if self.orient == "top" or self.orient == "bottom":
                box = QVBoxLayout(self)
                if self.orient == "top":
                    box.addWidget(lbl)
                    box.addWidget(pic)
                else:
                    box.addWidget(pic)
                    box.addWidget(lbl)
            if self.orient == "left" or self.orient == "right":
                box = QHBoxLayout(self)
                if self.orient == "left":
                    box.addWidget(lbl)
                    box.addWidget(pic)
                else:
                    box.addWidget(pic)
                    box.addWidget(lbl)

        else:
            box = QHBoxLayout(self)
            box.addWidget(pic)


class OutputBox(AutoEntry):
    def __init__(self, parent):
        AutoEntry.__init__(self, parent)
        self.setPalette(P.output_box)
        self.setReadOnly(1)


class Fonts(object): #custom Fonts
    def __init__(self):
        self.std = QFont("Arial", 12)
        self.big = QFont("Arial", 14)
        self.small = QFont("Verdana", 10)
        self.box = QFont("Courier New", 12, QFont.Bold)
        self.status = QFont("Arial", 12)


class Metrics(object): #custom font Metrics
    def __init__(self):
        self.box = QFontMetrics(F.box)


class Colors(object): #custom Colors
    def __init__(self):
        self.std = QColor("blue")
        self.err = QColor("red")
        self.enabled = QColor("lightsteelblue")
        self.disabled = QColor("lightslategray")

        self.highlight_fore = QColor("white")
        self.highlight_back = QColor("darkblue")

        self.grid_line = QColor("blue")


class Palettes(object): #custom Palettes
    def __init__(self):
        self.normal = app.palette()

        self.normal.setColor(QPalette.Base, C.enabled)
        self.normal.setColor(QPalette.Highlight, C.highlight_back)
        self.normal.setColor(QPalette.HighlightedText, C.highlight_fore)

        self.test = QPalette(self.normal)
        self.test.setColor(QPalette.Base, QColor("red"))
        self.test.setColor(QPalette.Highlight, QColor("red"))
        self.test.setColor(QPalette.HighlightedText, QColor("red"))


        self.test.setColor(QPalette.AlternateBase, QColor("red"))
        self.test.setColor(QPalette.Light, QColor("red"))
        self.test.setColor(QPalette.Midlight, QColor("red"))
        self.test.setColor(QPalette.Dark, QColor("red"))
        self.test.setColor(QPalette.Mid, QColor("red"))
        self.test.setColor(QPalette.Shadow, QColor("red"))


        self.normal.setColor(QPalette.HighlightedText, C.highlight_fore)

        self.normal.setColor(QPalette.HighlightedText, C.highlight_fore)

        self.output_box = QPalette(self.normal) # copy normal palette
        self.output_box.setColor(QPalette.Base, C.disabled)

        self.ready_text = QPalette(self.normal) # copy normal palette
        self.ready_text.setColor(QPalette.Foreground, C.std)
        self.ready_text.setColor(QPalette.Text, C.std)

        self.err_text = QPalette(self.normal) # copy normal palette
        self.err_text.setColor(QPalette.Foreground, C.err)
        self.err_text.setColor(QPalette.Text, C.err)

        self.entry_disabled = QPalette(self.normal) # copy normal palette
        self.entry_disabled.setColor(QPalette.Base, C.disabled)
        self.entry_disabled.setColor(QPalette.Text, QColor("black"))

