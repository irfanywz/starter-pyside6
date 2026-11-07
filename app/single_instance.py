"""Single instance PER FOLDER (cocok untuk aplikasi portable).

Kunci = APP_ID + hash path folder aplikasi, jadi dua salinan portable di folder berbeda
tetap bisa jalan bersamaan, tapi salinan yang sama tidak akan ganda. Klik exe kedua hanya
memunculkan window yang sudah berjalan.
"""

import hashlib
import logging

from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket

from .meta import APP_ID
from .paths import BASE_DIR

log = logging.getLogger("app.single_instance")


def _server_name() -> str:
    digest = hashlib.sha1(str(BASE_DIR).lower().encode("utf-8")).hexdigest()[:10]
    return f"{APP_ID}-{digest}"


class SingleInstance(QObject):
    activated = Signal()  # instance lain mencoba start -> tampilkan window

    def __init__(self) -> None:
        super().__init__()
        self._name = _server_name()
        self._server: QLocalServer | None = None

    def try_acquire(self) -> bool:
        """True = instance ini yang utama. False = sudah ada instance lain (sudah diberi sinyal)."""
        sock = QLocalSocket(self)
        sock.connectToServer(self._name)
        if sock.waitForConnected(300):
            sock.write(b"show")
            sock.flush()
            sock.waitForBytesWritten(300)
            sock.disconnectFromServer()
            return False
        QLocalServer.removeServer(self._name)  # bersihkan sisa crash
        self._server = QLocalServer(self)
        if not self._server.listen(self._name):
            log.warning("Gagal membuat server single-instance: %s", self._server.errorString())
        self._server.newConnection.connect(self._on_connection)
        return True

    def _on_connection(self) -> None:
        conn = self._server.nextPendingConnection()
        if conn is not None:
            conn.disconnectFromServer()
            conn.deleteLater()
        self.activated.emit()
