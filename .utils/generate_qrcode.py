"""
Génère un QR code pour accéder à Homeflix depuis le réseau local
"""
import qrcode
import socket

def get_local_ip():
    """Récupère l'adresse IP locale"""
    try:
        # Crée une connexion fictive pour obtenir l'IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "192.168.1.5"  # IP par défaut si erreur

def generate_qr_code():
    """Génère un QR code pour l'URL de Homeflix"""
    # Récupère l'IP locale
    ip = get_local_ip()
    url = f"http://{ip}:5173"
    
    # Crée le QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Génère l'image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Sauvegarde l'image
    output_file = "homeflix_qrcode.png"
    img.save(output_file)
    
    print("="*60)
    print("🎬 QR CODE HOMEFLIX GÉNÉRÉ !")
    print("="*60)
    print(f"📱 URL : {url}")
    print(f"💾 Fichier : {output_file}")
    print("")
    print("👉 Scannez ce QR code avec votre smartphone pour")
    print("   accéder à Homeflix depuis votre réseau WiFi !")
    print("="*60)
    
    # Affiche le QR code en ASCII dans le terminal
    print("\n📲 QR CODE (version texte) :\n")
    qr.print_ascii(invert=True)

if __name__ == "__main__":
    try:
        generate_qr_code()
    except ImportError:
        print("❌ Module 'qrcode' manquant.")
        print("📦 Installation : pip install qrcode[pil]")
    except Exception as e:
        print(f"❌ Erreur : {e}")
