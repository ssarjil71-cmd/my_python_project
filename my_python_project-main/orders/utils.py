import qrcode
import os
from flask import url_for

def generate_qr_code(table_number, qr_code_no):
    try:
        # Create QR data with guest menu URL
        qr_data = f"http://localhost:5000/orders/menu/{qr_code_no}"
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Ensure upload directory exists
        upload_dir = "static/uploads/qr"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save QR image
        qr_path = f"{upload_dir}/table_{table_number}.png"
        img.save(qr_path)
        
        return qr_path
    except Exception as e:
        print(f"QR generation error: {e}")
        return None