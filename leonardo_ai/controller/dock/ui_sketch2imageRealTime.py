import hashlib
import time

from PyQt5 import QtCore
from PyQt5.QtCore import QByteArray
from PyQt5.QtGui import QImage

from .ui_sketch2image import Sketch2Image
from ...util.threads import GeneralThread

SKETCH_PAINT_LAYER_NAME = "AI - Sketch -> Image RealTime"

SKETCH_WIDTH = 512
SKETCH_HEIGHT = 512

STYLE_VALUES = [
    "ANIME",
    "CINEMATIC",
    "DIGITAL_ART",
    "DYNAMIC",
    "ENVIRONMENT",
    "FANTASY_ART",
    "ILLUSTRATION",
    "PHOTOGRAPHY",
    "RENDER_3D",
    "RAYTRACED",
    "SKETCH_BW",
    "SKETCH_COLOR",
    "VIBRANT",
    "NONE",
]

class Sketch2ImageRealTime(Sketch2Image):
    sigLcmImageDone = QtCore.pyqtSignal(QImage)

    def __init__(self):
        super().__init__()

        self.sigLcmImageDone.connect(self._onLcmImageLoaded)

        def onStrengthChanged():
            self.ui.lblSketch2ImageRTStrength.setText(str(self.creativityStrength))

        self.ui.slSketch2ImageRTStrenth.valueChanged.connect(onStrengthChanged)

        def onGuidanceChanged():
            self.ui.lblSketch2ImageRTGuidance.setText(str(self.guidanceStrength))

        self.ui.slSketch2ImageRTGuidance.valueChanged.connect(onGuidanceChanged)

        def onModeChange():
            if self.ui.cmbMode.currentIndex() == 5:
                self.onSketch2ImageRealTimeActive()
            else:
                self.onSketch2ImageRealTimeInactive()

        self.ui.cmbMode.currentIndexChanged.connect(onModeChange)
        self.layerWatcherThread = None

    def onSketch2ImageRealTimeActive(self):
        document = Krita.instance().activeDocument()

        nodes = document.rootNode().findChildNodes(SKETCH_PAINT_LAYER_NAME)
        if nodes:
            self.sketchLayer = nodes[0]
        else:
            self.sketchLayer = document.createNode(SKETCH_PAINT_LAYER_NAME, "paintlayer")
            self.sketchLayer.cropNode(0, 0, SKETCH_WIDTH * 2, SKETCH_HEIGHT)
            document.crop(0, 0, max(document.width(), SKETCH_WIDTH * 2), max(document.height(), SKETCH_HEIGHT))
            document.rootNode().addChildNode(self.sketchLayer, None)

        self.layerWatcherThread = GeneralThread(self._layerWatcherRun)
        self.layerWatcherThread.start()

    def onSketch2ImageRealTimeInactive(self):
        if self.layerWatcherThread:
            self.layerWatcherThread.requestInterruption()

    def _layerWatcherRun(self, t: GeneralThread):
        lastHash = ""
        lastSettings = {
            "prompt": None,
            "negativePrompt": None,
            "strength": None,
            "guidance": None,
            "style": None,
            "refine": None,
            "seed": None,
        }

        while not t.isInterruptionRequested():
            pixelData = self.sketchLayer.pixelData(0, 0, SKETCH_WIDTH, SKETCH_HEIGHT)
            curHash = hashlib.md5(pixelData).hexdigest().upper()
            curSettings = {
                "prompt": self.prompt,
                "negativePrompt": self.negativePrompt,
                "strength": self.creativityStrength,
                "guidance": self.guidanceStrength,
                "style": self._style,
                "refine": self.instantRefine,
                "seed": self.seed,
            }

            if curHash != lastHash or lastSettings != curSettings:
                image = QImage(pixelData, SKETCH_WIDTH, SKETCH_HEIGHT, QImage.Format_ARGB32)
                generatedImage = self.getLeonardoAI().createLcmSketch2Image(
                    curSettings["prompt"],
                    image,
                    curSettings["negativePrompt"],
                    curSettings["strength"],
                    curSettings["guidance"],
                    curSettings["style"],
                    curSettings["refine"],
                    curSettings["seed"],
                )
                lastSettings = curSettings

                self.sigLcmImageDone.emit(generatedImage)
            else:
                time.sleep(1)

            lastHash = curHash

    @QtCore.pyqtSlot(QImage)
    def _onLcmImageLoaded(self, image: QImage):
        ptr = image.bits()
        ptr.setsize(image.byteCount())
        self.sketchLayer.setPixelData(
            QByteArray(ptr.asstring()),
            SKETCH_WIDTH,
            0,
            image.width(),
            image.height(),
        )

        document = Krita.instance().activeDocument()
        document.crop(0, 0, max(document.width(), SKETCH_WIDTH + image.width()), max(document.height(), SKETCH_HEIGHT, image.height()))
        document.refreshProjection()

    @property
    def creativityStrength(self):
        return self.ui.slSketch2ImageRTStrenth.value() / 100

    @property
    def guidanceStrength(self):
        return self.ui.slSketch2ImageRTGuidance.value() / 10

    @property
    def instantRefine(self):
        return self.ui.chkSketch2ImageRTRefine.isChecked()

    @property
    def _style(self):
        return STYLE_VALUES[self.ui.cmbSketch2ImageRTStyle.currentIndex()]
