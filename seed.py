from app import app, db
from models import Processador, PlacaMae, MemoriaRAM, PlacaVideo, Armazenamento, Fonte, Gabinete, Notebook

def popular_banco_seguro():
    with app.app_context():
        print("🚀 Expandindo o catálogo de peças do KitPC...")

        # --- 1. PROCESSADORES (CPUs) ---
        cpus_data = [
            # Entrada
            {"nome": "Intel Core i3-12100F", "preco": 580.00, "socket": "LGA1700", "tdp": 65, "img": "https://images9.kabum.com.br/produtos/fotos/283719/processador-intel-core-i3-12100f-cache-xmb-xghz-xghz-max-turbo-lga-1700-bx8071512100f_1640095096_gg.jpg"},
            {"nome": "AMD Ryzen 5 4500", "preco": 490.00, "socket": "AM4", "tdp": 65, "img": "https://images4.kabum.com.br/produtos/fotos/333154/processador-amd-ryzen-5-4500-cache-11mb-3-6ghz-4-1ghz-max-turbo-am4-sem-video-100-100000644box_1652381901_gg.jpg"},
            # Intermediário
            {"nome": "AMD Ryzen 5 5500", "preco": 650.00, "socket": "AM4", "tdp": 65, "img": "https://images5.kabum.com.br/produtos/fotos/sync_mirakl/356695/xlarge/Processador-AMD-Ryzen-5-5500-3-6GHz-Cache-16MB-Hexa-Core-12-Threads-AM4-100-100000457BOX_1772046526.jpg"},
            {"nome": "AMD Ryzen 5 5600", "preco": 820.00, "socket": "AM4", "tdp": 65, "img": "https://images5.kabum.com.br/produtos/fotos/sync_mirakl/356695/xlarge/Processador-AMD-Ryzen-5-5500-3-6GHz-Cache-16MB-Hexa-Core-12-Threads-AM4-100-100000457BOX_1772046526.jpg"},
            {"nome": "Intel Core i5-12400F", "preco": 890.00, "socket": "LGA1700", "tdp": 65, "img": "https://images8.kabum.com.br/produtos/fotos/283718/processador-intel-core-i5-12400f-cache-xmb-xghz-xghz-max-turbo-lga-1700-bx8071512400f_1640094446_gg.jpg"},
            {"nome": "Intel Core i5-13400F", "preco": 1250.00, "socket": "LGA1700", "tdp": 65, "img": "https://images8.kabum.com.br/produtos/fotos/283718/processador-intel-core-i5-12400f-cache-xmb-xghz-xghz-max-turbo-lga-1700-bx8071512400f_1640094446_gg.jpg"},
            # High-End / Nova Geração
            {"nome": "AMD Ryzen 7 5700X", "preco": 1150.00, "socket": "AM4", "tdp": 65, "img": "https://images7.kabum.com.br/produtos/fotos/320797/processador-amd-ryzen-7-5700x-cache-36mb-3-8ghz-4-6ghz-max-turbo-am4-100-100000926wof_1647636511_gg.jpg"},
            {"nome": "AMD Ryzen 5 7600", "preco": 1390.00, "socket": "AM5", "tdp": 65, "img": "https://images7.kabum.com.br/produtos/fotos/320797/processador-amd-ryzen-7-5700x-cache-36mb-3-8ghz-4-6ghz-max-turbo-am4-100-100000926wof_1647636511_gg.jpg"},
            {"nome": "Intel Core i7-13700K", "preco": 2600.00, "socket": "LGA1700", "tdp": 125, "img": "https://images0.kabum.com.br/produtos/fotos/sync_mirakl/400720/xlarge/Processador-Intel-Core-I7-13700k-Lga-1700-3-4ghz-5-4ghz-Max-Turbo-Cache-30MB-16-N-cleos-24-Threads-Bx8071513700k_1773170913.jpg"},
            {"nome": "AMD Ryzen 7 7800X3D", "preco": 2800.00, "socket": "AM5", "tdp": 120, "img": "https://images2.kabum.com.br/produtos/fotos/426262/processador-amd-ryzen-7-7800x3d-5-0ghz-max-turbo-cache-104mb-am5-8-nucleos-video-integrado-100-100000910wof_1680784502_gg.jpg"}
        ]

        for data in cpus_data:
            if not Processador.query.filter_by(nome=data["nome"]).first():
                db.session.add(Processador(nome=data["nome"], preco=data["preco"], socket_id=data["socket"], tdp=data["tdp"], link_loja="#", imagem_url=data["img"]))

        # --- 2. PLACAS-MÃE ---
        mobos_data = [
            # AM4 (DDR4)
            {"nome": "MSI A520M-A Pro", "preco": 420.00, "sock": "AM4", "mem": "DDR4", "tam": "Micro-ATX", "img": "https://images0.kabum.com.br/produtos/fotos/280890/placa-mae-msi-a520m-a-pro-amd-am4-matx-ddr4_1722881948_gg.jpg"},
            {"nome": "Gigabyte B450M DS3H V2", "preco": 520.00, "sock": "AM4", "mem": "DDR4", "tam": "Micro-ATX", "img": "https://images8.kabum.com.br/produtos/fotos/457818/placa-mae-gigabyte-a520m-ds3h-v2-amd-micro-atx-ddr4-a520m-ds3h-v2_1689160435_gg.jpg"},
            {"nome": "ASUS TUF Gaming B550M-Plus", "preco": 950.00, "sock": "AM4", "mem": "DDR4", "tam": "Micro-ATX", "img": "https://images6.kabum.com.br/produtos/fotos/sync_mirakl/172706/xlarge/Placa-M-e-Asus-TUF-Gaming-B550M-PLUS-AMD-AM4-mATX-DDR4-M-2-Aura-para-fita-RGB-90MB14A0-C1BAY0_1772769212.jpg"},
            # LGA1700 (DDR4)
            {"nome": "ASRock H610M-HVS", "preco": 510.00, "sock": "LGA1700", "mem": "DDR4", "tam": "Micro-ATX", "img": "https://images4.kabum.com.br/produtos/fotos/sync_mirakl/483054/xlarge/Placa-M-e-Asrock-H610m-P-Intel-LGA-1700-Intel-13-E-12-Gera-o-Matx-DDR4-H610m-Hvs-M-2-R2-0_1770332969.jpg"},
            {"nome": "Gigabyte B660M Gaming X", "preco": 980.00, "sock": "LGA1700", "mem": "DDR4", "tam": "Micro-ATX", "img": "https://images5.kabum.com.br/produtos/fotos/723245/placa-mae-gigabyte-b860m-gaming-x-wifi6e-intel-micro-atx-ddr5-rgb-wi-fi-6e-bluetooth-preto-b86mgm6-00_1751026656_gg.jpg"},
            # AM5 (DDR5)
            {"nome": "ASRock B650M-HDV/M.2", "preco": 1100.00, "sock": "AM5", "mem": "DDR5", "tam": "Micro-ATX", "img": "https://images0.kabum.com.br/produtos/fotos/525050/placa-mae-asrock-b650m-hdv-m-2-amd-b650-matx-ddr5-90-mxbla-_1718733505_gg.jpg"}
        ]

        for data in mobos_data:
            if not PlacaMae.query.filter_by(nome=data["nome"]).first():
                db.session.add(PlacaMae(nome=data["nome"], preco=data["preco"], socket_id=data["sock"], tipo_memoria=data["mem"], tamanho=data["tam"], link_loja="#", imagem_url=data["img"]))

        # --- 3. PLACAS DE VÍDEO (GPUs) ---
        gpus_data = [
            {"nome": "NVIDIA GTX 1650 4GB", "preco": 850.00, "tdp": 75, "img": "https://ae-pic-a1.aliexpress-media.com/kf/S46c8f05545564419bb7290b20399f037Z.jpg_720x720q75.jpg_.avif"},
            {"nome": "AMD Radeon RX 6600 8GB", "preco": 1350.00, "tdp": 132, "img": "https://images7.kabum.com.br/produtos/fotos/695107/placa-de-video-asrock-rx-6600-challenger-white-amd-radeon-8gb-gddr6-directx-12-ultimate-rdna-2-90-ga4uzz-00uanf_1742841360_gg.jpg"},
            {"nome": "NVIDIA GeForce RTX 3060 12GB", "preco": 1850.00, "tdp": 170, "img": "https://images0.kabum.com.br/produtos/fotos/sync_mirakl/927060/xlarge/Placa-De-Video-Gpu-Nvidia-Geforce-RTX-3060-12gb-Ddr6-192-Bits-PCyes-Projeto-Edge-Pgs3060pe2f_1771616318.png"},
            {"nome": "NVIDIA GeForce RTX 4060 8GB", "preco": 1950.00, "tdp": 115, "img": "https://images.kabum.com.br/produtos/fotos/777075/placa-de-video-gigabyte-rtx-5060-eagle-oc-8g-nvidia-geforce-8gb-gddr7-128bits-dlss-ray-tracing-gv-n5060eagle-oc-8gd_1747328059_m.jpg"},
            {"nome": "AMD Radeon RX 6750 XT 12GB", "preco": 2400.00, "tdp": 250, "img": "https://m.media-amazon.com/images/I/81QItJufypL._AC_SY450_.jpg"},
            {"nome": "NVIDIA GeForce RTX 4070 12GB", "preco": 3950.00, "tdp": 200, "img": "https://m.media-amazon.com/images/I/61pM3J9hGoL._AC_SY300_SX300_QL70_ML2_.jpg"},
            {"nome": "NVIDIA GeForce RTX 4080 Super", "preco": 7500.00, "tdp": 320, "img": "https://images9.kabum.com.br/produtos/fotos/sync_mirakl/894989/xlarge/Placa-De-V-deo-Nvidia-Geforce-Asus-Prime-RTX5060ti-Oc-16gb-Gddr7-128-Bits-Prime-RTX5060ti-o16g-90yv0mh2-m0na00_1770928365.jpg"}
        ]

        for data in gpus_data:
            if not PlacaVideo.query.filter_by(nome=data["nome"]).first():
                db.session.add(PlacaVideo(nome=data["nome"], preco=data["preco"], tdp=data["tdp"], link_loja="#", imagem_url=data["img"]))

        # --- 4. MEMÓRIA RAM ---
        rams_data = [
            {"nome": "Mancer Danto 8GB 3200MHz", "preco": 140.00, "tipo": "DDR4", "img": "https://ae-pic-a1.aliexpress-media.com/kf/S6f68763480424437801adb1fb2c52b9e5.jpg_720x720q75.jpg_.avif"},
            {"nome": "Kingston Fury Beast 8GB 3200MHz", "preco": 165.00, "tipo": "DDR4", "img": "https://images5.kabum.com.br/produtos/fotos/172365/memoria-kingston-fury-beast-8gb-3200mhz-ddr4-cl16-preto-kf432c16bb-8_1626270524_gg.jpg"},
            {"nome": "XPG Spectrix D41 8GB (2x8) 3200MHz", "preco": 548.00, "tipo": "DDR4", "img": "https://images4.kabum.com.br/produtos/fotos/156594/memoria-xpg-gammix-d41-8gb-3200mhz-ddr4-rgb-cl-16-cinza-ax4u32008g16a-st41_1627065811_gg.jpg"},
            {"nome": "Corsair Vengeance 32GB (2x16) 3600MHz", "preco": 3999.00, "tipo": "DDR4", "img": "https://images.kabum.com.br/produtos/fotos/922206/memoria-ram-corsair-vengeance-32gb-2x16gb-6000mhz-ddr5-cl40-preta-cmk32gx5m2b6000c40_1758205397_m.jpg"},
            {"nome": "Kingston Fury Renegade 16GB 6000MHz", "preco": 1999.90, "tipo": "DDR5", "img": "https://images0.kabum.com.br/produtos/fotos/506150/memoria-kingston-fury-renegade-16gb-7600mt-s-ddr5-cl38-dimm-prata-xmp-kf576c38rs-16_1720625027_gg.jpg"}
        ]

        for data in rams_data:
            if not MemoriaRAM.query.filter_by(nome=data["nome"]).first():
                db.session.add(MemoriaRAM(nome=data["nome"], preco=data["preco"], tipo=data["tipo"], link_loja="#", imagem_url=data["img"]))

        # --- 5. FONTES (Com foco em TDP variado) ---
        fontes_data = [
            {"nome": "Mancer Thunder 500W 80 Plus", "preco": 230.00, "pot": 500, "img": "https://m.media-amazon.com/images/G/32/apparel/rcxgs/tile._CB483369971_.gif"},
            {"nome": "MSI MAG A650BN 650W", "preco": 295.00, "pot": 650, "img": "https://images8.kabum.com.br/produtos/fotos/369658/fonte-msi-mag-a650bn-atx-650w-80-plus-bronze-pfc-ativo-entrada-bivolt-preto-306-7zp2b22-ce0_1665770996_gg.jpg"},
            {"nome": "XPG Pylon 650W 80 Plus Bronze", "preco": 350.00, "pot": 650, "img": "https://images6.kabum.com.br/produtos/fotos/516056/fonte-corsair-cx-series-cx650-650w-80-plus-bronze-sem-cabo-preto-cp-9020278-br_1714483460_gg.jpg"},
            {"nome": "Corsair RM750e 750W Gold", "preco": 680.00, "pot": 750, "img": "https://http2.mlstatic.com/D_NQ_NP_2X_661120-MLA99509647484_112025-F.webp"},
            {"nome": "XPG Core Reactor 850W Gold", "preco": 850.00, "pot": 850, "img": "https://images6.kabum.com.br/produtos/fotos/514896/fonte-xpg-core-reactor-ii-ve-850w-75261436_1721238617_gg.jpg"}
        ]

        for data in fontes_data:
            if not Fonte.query.filter_by(nome=data["nome"]).first():
                db.session.add(Fonte(nome=data["nome"], preco=data["preco"], potencia=data["pot"], link_loja="#", imagem_url=data["img"]))

        # --- 6. ARMAZENAMENTO ---
        ssds_data = [
            {"nome": "SSD Mancer Reaper 240GB SATA", "preco": 130.00, "img": "https://mancer.com.br/wp-content/uploads/2023/02/MCR-RPRF-240-1.jpg"},
            {"nome": "SSD Kingston NV2 500GB M.2 NVMe", "preco": 260.00, "img": "https://http2.mlstatic.com/D_Q_NP_2X_990970-MLA101922220577_122025-E.webp"},
            {"nome": "SSD Crucial P3 1TB M.2 NVMe", "preco": 430.00, "img": "https://assets.micron.com/adobe/assets/urn:aaid:aem:6a66cf55-2ffa-4947-b2f4-1c57f00bfcd5/renditions/transformpng-1024-1024.png/as/crucial-p3-ssd-flat-front-image.png"},
            {"nome": "SSD Kingston NV2 2TB M.2 NVMe", "preco": 780.00, "img": "https://m.media-amazon.com/images/G/32/apparel/rcxgs/tile._CB483369971_.gif"}
        ]

        for data in ssds_data:
            if not Armazenamento.query.filter_by(nome=data["nome"]).first():
                db.session.add(Armazenamento(nome=data["nome"], preco=data["preco"], link_loja="#", imagem_url=data["img"]))
        # --- 7. GABINETES ---
        gab_data = [
            {"nome": "Mancer Goblin (Preto)", "preco": 160.00, "tam": "Micro-ATX", "img": "https://media.pichau.com.br/media/catalog/product/cache/2f958555330323e505eba7ce930bdf27/m/c/mcr-gbnv2-bk4.jpg"},
            {"nome": "Pichau Apus Black", "preco": 190.00, "tam": "Micro-ATX, ATX", "img": "https://media.pichau.com.br/media/catalog/product/cache/2f958555330323e505eba7ce930bdf27/p/g/pg-aps-blk0123.jpg"},
            {"nome": "Montech Air 903 Base", "preco": 350.00, "tam": "Micro-ATX, ATX, E-ATX", "img": "https://img.terabyteshop.com.br/produto/g/gabinete-gamer-montech-air-903-base-mid-tower-e-atx-black-sem-fonte-com-3-fans_172737.jpg"},
            {"nome": "Lian Li Lancool 216", "preco": 750.00, "tam": "Micro-ATX, ATX", "img": "https://lian-li.com/wp-content/uploads/2022/11/1007_136-b.jpg"}
        ]
        for data in gab_data:
            if not Gabinete.query.filter_by(nome=data["nome"]).first():
                db.session.add(Gabinete(nome=data["nome"], preco=data["preco"], tamanho_suportado=data["tam"], link_loja="#", imagem_url=data["img"]))

        # --- 8. NOTEBOOKS (Opções prontas para quem não quer montar PC) ---
        notebooks_data = [
            {"nome": "Samsung Book i3", "preco": 2450.00, "uso": "Estudos/Escritório", "img": "https://samsungbrshop.vtexassets.com/arquivos/ids/180101-1000-auto?v=637558607985000000&width=1000&height=auto&aspect=true"},
            {"nome": "Lenovo Ideapad Gaming 3i", "preco": 3800.00, "uso": "Jogos Leves/Edição", "img": "https://p1-ofp.static.pub/medias/23809986225_IdeaPad115ADA7Cloud_Grey_202108120307091751053200811.png?width=400&height=400"},
            {"nome": "Acer Nitro 5", "preco": 4500.00, "uso": "Jogos/Profissional", "img": "https://http2.mlstatic.com/D_NQ_NP_2X_924349-MLA97662433070_112025-F.webp"},
            {"nome": "Dell G15 RTX 3050", "preco": 5400.00, "uso": "Jogos Pesados", "img": "https://benchpromos.com.br/_next/image?url=https%3A%2F%2Fi.ibb.co%2FqMCqVwtB%2F9e88f8f1-4313-43b5-b5e0-69dc4b56e112.png&w=3840&q=75"},
            {"nome": "MacBook Air M2", "preco": 7900.00, "uso": "Premium/Trabalho", "img": "https://images2.kabum.com.br/produtos/fotos/954432/macbook-air-apple-13-6-chip-m2-cpu-8-nucleos-gpu-10-nucleos-24gb-ssd-512gb-meia-noite-z1hn0bz-a_1769544448_gg.jpg"}
        ]

        for data in notebooks_data:
            if not Notebook.query.filter_by(nome=data["nome"]).first():
                db.session.add(Notebook(
                    nome=data["nome"], 
                    preco=data["preco"], 
                    link_loja="#", 
                    imagem_url=data["img"]
        ))
        db.session.commit()
        print(f"✅ Catálogo finalizado! Seus posts e usuários estão seguros.")

if __name__ == "__main__":
    popular_banco_seguro()