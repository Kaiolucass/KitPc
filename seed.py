from app import app, db
from models import Processador, PlacaMae, MemoriaRAM, PlacaVideo, Armazenamento, Fonte, Gabinete,Notebook

def popular_banco_seguro():
    with app.app_context():
        print("🚀 Expandindo o catálogo de peças do KitPC...")

        # --- 1. PROCESSADORES (CPUs) ---
        cpus_data = [
            # Entrada
            {"nome": "Intel Core i3-12100F", "preco": 580.00, "socket": "LGA1700", "tdp": 65},
            {"nome": "AMD Ryzen 5 4500", "preco": 490.00, "socket": "AM4", "tdp": 65},
            # Intermediário
            {"nome": "AMD Ryzen 5 5500", "preco": 650.00, "socket": "AM4", "tdp": 65},
            {"nome": "AMD Ryzen 5 5600", "preco": 820.00, "socket": "AM4", "tdp": 65},
            {"nome": "Intel Core i5-12400F", "preco": 890.00, "socket": "LGA1700", "tdp": 65},
            {"nome": "Intel Core i5-13400F", "preco": 1250.00, "socket": "LGA1700", "tdp": 65},
            # High-End / Nova Geração
            {"nome": "AMD Ryzen 7 5700X", "preco": 1150.00, "socket": "AM4", "tdp": 65},
            {"nome": "AMD Ryzen 5 7600", "preco": 1390.00, "socket": "AM5", "tdp": 65},
            {"nome": "Intel Core i7-13700K", "preco": 2600.00, "socket": "LGA1700", "tdp": 125},
            {"nome": "AMD Ryzen 7 7800X3D", "preco": 2800.00, "socket": "AM5", "tdp": 120}
        ]

        for data in cpus_data:
            if not Processador.query.filter_by(nome=data["nome"]).first():
                db.session.add(Processador(nome=data["nome"], preco=data["preco"], socket_id=data["socket"], tdp=data["tdp"], link_loja="#", imagem_url="#"))

        # --- 2. PLACAS-MÃE ---
        mobos_data = [
            # AM4 (DDR4)
            {"nome": "MSI A520M-A Pro", "preco": 420.00, "sock": "AM4", "mem": "DDR4", "tam": "Micro-ATX"},
            {"nome": "Gigabyte B450M DS3H V2", "preco": 520.00, "sock": "AM4", "mem": "DDR4", "tam": "Micro-ATX"},
            {"nome": "ASUS TUF Gaming B550M-Plus", "preco": 950.00, "sock": "AM4", "mem": "DDR4", "tam": "Micro-ATX"},
            # LGA1700 (DDR4)
            {"nome": "ASRock H610M-HVS", "preco": 510.00, "sock": "LGA1700", "mem": "DDR4", "tam": "Micro-ATX"},
            {"nome": "Gigabyte B660M Gaming X", "preco": 980.00, "sock": "LGA1700", "mem": "DDR4", "tam": "Micro-ATX"},
            # AM5 (DDR5)
            {"nome": "ASRock B650M-HDV/M.2", "preco": 1100.00, "sock": "AM5", "mem": "DDR5", "tam": "Micro-ATX"}
        ]

        for data in mobos_data:
            if not PlacaMae.query.filter_by(nome=data["nome"]).first():
                db.session.add(PlacaMae(nome=data["nome"], preco=data["preco"], socket_id=data["sock"], tipo_memoria=data["mem"], tamanho=data["tam"], link_loja="#", imagem_url="#"))

        # --- 3. PLACAS DE VÍDEO (GPUs) ---
        gpus_data = [
            {"nome": "NVIDIA GTX 1650 4GB", "preco": 850.00, "tdp": 75},
            {"nome": "AMD Radeon RX 6600 8GB", "preco": 1350.00, "tdp": 132},
            {"nome": "NVIDIA GeForce RTX 3060 12GB", "preco": 1850.00, "tdp": 170},
            {"nome": "NVIDIA GeForce RTX 4060 8GB", "preco": 1950.00, "tdp": 115},
            {"nome": "AMD Radeon RX 6750 XT 12GB", "preco": 2400.00, "tdp": 250},
            {"nome": "NVIDIA GeForce RTX 4070 12GB", "preco": 3950.00, "tdp": 200},
            {"nome": "NVIDIA GeForce RTX 4080 Super", "preco": 7500.00, "tdp": 320}
        ]

        for data in gpus_data:
            if not PlacaVideo.query.filter_by(nome=data["nome"]).first():
                db.session.add(PlacaVideo(nome=data["nome"], preco=data["preco"], tdp=data["tdp"], link_loja="#", imagem_url="#"))

        # --- 4. MEMÓRIA RAM ---
        rams_data = [
            {"nome": "Mancer Danto 8GB 3200MHz", "preco": 140.00, "tipo": "DDR4"},
            {"nome": "Kingston Fury Beast 8GB 3200MHz", "preco": 165.00, "tipo": "DDR4"},
            {"nome": "XPG Spectrix D41 16GB (2x8) 3200MHz", "preco": 340.00, "tipo": "DDR4"},
            {"nome": "Corsair Vengeance 32GB (2x16) 3600MHz", "preco": 650.00, "tipo": "DDR4"},
            {"nome": "Kingston Fury Renegade 16GB 6000MHz", "preco": 550.00, "tipo": "DDR5"}
        ]

        for data in rams_data:
            if not MemoriaRAM.query.filter_by(nome=data["nome"]).first():
                db.session.add(MemoriaRAM(nome=data["nome"], preco=data["preco"], tipo=data["tipo"], link_loja="#", imagem_url="#"))

        # --- 5. FONTES (Com foco em TDP variado) ---
        fontes_data = [
            {"nome": "Mancer Thunder 500W 80 Plus", "preco": 230.00, "pot": 500},
            {"nome": "MSI MAG A650BN 650W", "preco": 295.00, "pot": 650},
            {"nome": "XPG Pylon 650W 80 Plus Bronze", "preco": 350.00, "pot": 650},
            {"nome": "Corsair RM750e 750W Gold", "preco": 680.00, "pot": 750},
            {"nome": "XPG Core Reactor 850W Gold", "preco": 850.00, "pot": 850}
        ]

        for data in fontes_data:
            if not Fonte.query.filter_by(nome=data["nome"]).first():
                db.session.add(Fonte(nome=data["nome"], preco=data["preco"], potencia=data["pot"], link_loja="#", imagem_url="#"))

        # --- 6. ARMAZENAMENTO ---
        ssds_data = [
            {"nome": "SSD Mancer Reaper 240GB SATA", "preco": 130.00},
            {"nome": "SSD Kingston NV2 500GB M.2 NVMe", "preco": 260.00},
            {"nome": "SSD Crucial P3 1TB M.2 NVMe", "preco": 430.00},
            {"nome": "SSD Kingston NV2 2TB M.2 NVMe", "preco": 780.00}
        ]

        for data in ssds_data:
            if not Armazenamento.query.filter_by(nome=data["nome"]).first():
                db.session.add(Armazenamento(nome=data["nome"], preco=data["preco"], link_loja="#", imagem_url="#"))

        # --- 7. GABINETES ---
        gab_data = [
            {"nome": "Mancer Goblin (Preto)", "preco": 160.00, "tam": "Micro-ATX"},
            {"nome": "Pichau Apus Black", "preco": 190.00, "tam": "Micro-ATX, ATX"},
            {"nome": "Montech Air 903 Base", "preco": 350.00, "tam": "Micro-ATX, ATX, E-ATX"},
            {"nome": "Lian Li Lancool 216", "preco": 750.00, "tam": "Micro-ATX, ATX"}
        ]

        # --- 8. NOTEBOOKS (Opções prontas para quem não quer montar PC) ---
        notebooks_data = [
            {
                "nome": "Samsung Book (i3-1115G4, 8GB, SSD 256GB)", 
                "preco": 2450.00, 
                "uso": "Estudos/Escritório",
                "link": "https://amzn.to/3P4"
            },
            {
                "nome": "Lenovo Ideapad Gaming 3i (i5-11300H, GTX 1650, 8GB)", 
                "preco": 3800.00, 
                "uso": "Jogos Leves/Edição",
                "link": "https://amzn.to/3P5"
            },
            {
                "nome": "Acer Nitro 5 (Ryzen 5 7535HS, RTX 3050, 8GB)", 
                "preco": 4500.00, 
                "uso": "Jogos/Profissional",
                "link": "https://amzn.to/3P6"
            },
            {
                "nome": "Dell G15 (i5-13450HX, RTX 3050, 16GB)", 
                "preco": 5400.00, 
                "uso": "Jogos Pesados",
                "link": "https://amzn.to/3P7"
            },
            {
                "nome": "MacBook Air M2 (8GB RAM, 256GB SSD)", 
                "preco": 7900.00, 
                "uso": "Premium/Trabalho",
                "link": "https://amzn.to/3P8"
            },
            {
                "nome": "Avell Storm (i7-13700HX, RTX 4060, 16GB)", 
                "preco": 9200.00, 
                "uso": "Ultra Performance",
                "link": "https://amzn.to/3P9"
            }
        ]

        for data in gab_data:
            if not Gabinete.query.filter_by(nome=data["nome"]).first():
                db.session.add(Gabinete(nome=data["nome"], preco=data["preco"], tamanho_suportado=data["tam"], link_loja="#", imagem_url="#"))

        db.session.commit()
        print(f"✅ Catálogo finalizado! Seus posts e usuários estão seguros.")

if __name__ == "__main__":
    popular_banco_seguro()