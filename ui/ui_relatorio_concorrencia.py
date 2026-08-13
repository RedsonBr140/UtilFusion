# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'relatorio_concorrencia.ui'
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
class Ui_RelatorioConcorrenciaWindow(object):
    def setupUi(self, RelatorioConcorrenciaWindow):
        if not RelatorioConcorrenciaWindow.objectName():
            RelatorioConcorrenciaWindow.setObjectName(u"RelatorioConcorrenciaWindow")
        self.mainLayout = QVBoxLayout(RelatorioConcorrenciaWindow)
        self.mainLayout.setSpacing(8)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.filtroGroup = QGroupBox(RelatorioConcorrenciaWindow)
        self.filtroGroup.setObjectName(u"filtroGroup")
        self.filtroLayout = QHBoxLayout(self.filtroGroup)
        self.filtroLayout.setSpacing(6)
        self.filtroLayout.setObjectName(u"filtroLayout")
        self.idcotacaoLabel = QLabel(self.filtroGroup)
        self.idcotacaoLabel.setObjectName(u"idcotacaoLabel")

        self.filtroLayout.addWidget(self.idcotacaoLabel)

        self.idcotacaoInput = QLineEdit(self.filtroGroup)
        self.idcotacaoInput.setObjectName(u"idcotacaoInput")
        self.idcotacaoInput.setMaximumSize(QSize(50, 16777215))

        self.filtroLayout.addWidget(self.idcotacaoInput)

        self.idempresaLabel = QLabel(self.filtroGroup)
        self.idempresaLabel.setObjectName(u"idempresaLabel")

        self.filtroLayout.addWidget(self.idempresaLabel)

        self.idempresaInput = QLineEdit(self.filtroGroup)
        self.idempresaInput.setObjectName(u"idempresaInput")
        self.idempresaInput.setMaximumSize(QSize(50, 16777215))

        self.filtroLayout.addWidget(self.idempresaInput)

        self.gerarButton = QPushButton(self.filtroGroup)
        self.gerarButton.setObjectName(u"gerarButton")

        self.filtroLayout.addWidget(self.gerarButton)

        self.filtroSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.filtroLayout.addItem(self.filtroSpacer)


        self.mainLayout.addWidget(self.filtroGroup)

        self.resultadoTable = QTableWidget(RelatorioConcorrenciaWindow)
        if (self.resultadoTable.columnCount() < 6):
            self.resultadoTable.setColumnCount(6)
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
        __qtablewidgetitem5 = QTableWidgetItem()
        self.resultadoTable.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.resultadoTable.setObjectName(u"resultadoTable")
        self.resultadoTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.resultadoTable.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.mainLayout.addWidget(self.resultadoTable)


        self.retranslateUi(RelatorioConcorrenciaWindow)

        QMetaObject.connectSlotsByName(RelatorioConcorrenciaWindow)
    # setupUi

    def retranslateUi(self, RelatorioConcorrenciaWindow):
        self.filtroGroup.setTitle(QCoreApplication.translate("RelatorioConcorrenciaWindow", u"Filtros", None))
        self.idcotacaoLabel.setText(QCoreApplication.translate("RelatorioConcorrenciaWindow", u"ID Cotacao:", None))
        self.idempresaLabel.setText(QCoreApplication.translate("RelatorioConcorrenciaWindow", u"ID Empresa:", None))
        self.gerarButton.setText(QCoreApplication.translate("RelatorioConcorrenciaWindow", u"Gerar Relatorio", None))
        ___qtablewidgetitem = self.resultadoTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("RelatorioConcorrenciaWindow", u"Descricao", None))
        ___qtablewidgetitem1 = self.resultadoTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("RelatorioConcorrenciaWindow", u"Custo Gerencial", None))
        ___qtablewidgetitem2 = self.resultadoTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("RelatorioConcorrenciaWindow", u"Varejo (Nosso)", None))
        ___qtablewidgetitem3 = self.resultadoTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("RelatorioConcorrenciaWindow", u"Atacado (Nosso)", None))
        ___qtablewidgetitem4 = self.resultadoTable.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("RelatorioConcorrenciaWindow", u"Concorrente (API)", None))
        ___qtablewidgetitem5 = self.resultadoTable.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("RelatorioConcorrenciaWindow", u"Preco Conc.", None))
        pass
    # retranslateUi

