# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'consulta_menor_preco_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)
class Ui_ConsultaMenorPrecoWindow(object):
    def setupUi(self, ConsultaMenorPrecoWindow):
        if not ConsultaMenorPrecoWindow.objectName():
            ConsultaMenorPrecoWindow.setObjectName(u"ConsultaMenorPrecoWindow")
        self.mainLayout = QVBoxLayout(ConsultaMenorPrecoWindow)
        self.mainLayout.setSpacing(10)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(12, 12, 12, 12)
        self.filtroGroup = QGroupBox(ConsultaMenorPrecoWindow)
        self.filtroGroup.setObjectName(u"filtroGroup")
        self.filtroLayout = QHBoxLayout(self.filtroGroup)
        self.filtroLayout.setSpacing(8)
        self.filtroLayout.setObjectName(u"filtroLayout")
        self.filtroLayout.setContentsMargins(12, 10, 12, 10)
        self.idcotacaoLabel = QLabel(self.filtroGroup)
        self.idcotacaoLabel.setObjectName(u"idcotacaoLabel")

        self.filtroLayout.addWidget(self.idcotacaoLabel)

        self.idcotacaoInput = QLineEdit(self.filtroGroup)
        self.idcotacaoInput.setObjectName(u"idcotacaoInput")
        self.idcotacaoInput.setMaximumSize(QSize(60, 16777215))

        self.filtroLayout.addWidget(self.idcotacaoInput)

        self.idconcorrenteLabel = QLabel(self.filtroGroup)
        self.idconcorrenteLabel.setObjectName(u"idconcorrenteLabel")

        self.filtroLayout.addWidget(self.idconcorrenteLabel)

        self.idconcorrenteInput = QLineEdit(self.filtroGroup)
        self.idconcorrenteInput.setObjectName(u"idconcorrenteInput")
        self.idconcorrenteInput.setMaximumSize(QSize(60, 16777215))

        self.filtroLayout.addWidget(self.idconcorrenteInput)

        self.searchButton = QPushButton(self.filtroGroup)
        self.searchButton.setObjectName(u"searchButton")

        self.filtroLayout.addWidget(self.searchButton)

        self.atualizarButton = QPushButton(self.filtroGroup)
        self.atualizarButton.setObjectName(u"atualizarButton")

        self.filtroLayout.addWidget(self.atualizarButton)

        self.filtroSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.filtroLayout.addItem(self.filtroSpacer)


        self.mainLayout.addWidget(self.filtroGroup)

        self.resultadoTable = QTableWidget(ConsultaMenorPrecoWindow)
        if (self.resultadoTable.columnCount() < 5):
            self.resultadoTable.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.resultadoTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.resultadoTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.resultadoTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.resultadoTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.resultadoTable.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.resultadoTable.setObjectName(u"resultadoTable")
        self.resultadoTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resultadoTable.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.mainLayout.addWidget(self.resultadoTable)


        self.retranslateUi(ConsultaMenorPrecoWindow)

        QMetaObject.connectSlotsByName(ConsultaMenorPrecoWindow)
    # setupUi

    def retranslateUi(self, ConsultaMenorPrecoWindow):
        self.filtroGroup.setTitle(QCoreApplication.translate("ConsultaMenorPrecoWindow", u"Filtros", None))
        self.idcotacaoLabel.setText(QCoreApplication.translate("ConsultaMenorPrecoWindow", u"ID Cota\u00e7\u00e3o:", None))
        self.idcotacaoInput.setText(QCoreApplication.translate("ConsultaMenorPrecoWindow", u"35", None))
        self.idconcorrenteLabel.setText(QCoreApplication.translate("ConsultaMenorPrecoWindow", u"ID Concorrente:", None))
        self.idconcorrenteInput.setText(QCoreApplication.translate("ConsultaMenorPrecoWindow", u"36", None))
        self.searchButton.setText(QCoreApplication.translate("ConsultaMenorPrecoWindow", u"Pesquisar", None))
        self.atualizarButton.setText(QCoreApplication.translate("ConsultaMenorPrecoWindow", u"Atualizar Cota\u00e7\u00e3o", None))
        ___qtablewidgetitem = self.resultadoTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("ConsultaMenorPrecoWindow", u"ID", None))
        ___qtablewidgetitem1 = self.resultadoTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("ConsultaMenorPrecoWindow", u"C\u00f3d. Bar", None))
        ___qtablewidgetitem2 = self.resultadoTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("ConsultaMenorPrecoWindow", u"Desc. Prod.", None))
        ___qtablewidgetitem3 = self.resultadoTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("ConsultaMenorPrecoWindow", u"Pre\u00e7o Concorrente", None))
        ___qtablewidgetitem4 = self.resultadoTable.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("ConsultaMenorPrecoWindow", u"Concorrente", None))
        pass
    # retranslateUi

