import qrcode
import io
import base64

class QRCode:

    def __init__(self, data):
        self.img = qrcode.make(data)

    @property
    def bin(self):
        output = io.BytesIO()
        self.img.save(output)
        return output.getvalue()

    @property
    def base64(self):
        return base64.b64encode(self.bin)