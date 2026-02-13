-- Inserir sockets de CPU
INSERT INTO sockets_cpu (id, nome)
VALUES
  (1, 'Intel LGA‑1200/1700'),
  (2, 'AMD AM4/AM5');

-- PROCESSADORES INTEL
INSERT INTO processadores (nome, preco, imagem_url, link_loja, socket_id)
VALUES
  ('Intel Core i3-10100F', 499.99, 'https://images0.kabum.com.br/produtos/fotos/129960/processador-intel-core-i3-10100f-cache-6mb-4-30-ghz-lga-1200-i3-10100f_1603394030_gg.jpg', 'https://www.kabum.com.br/produto/129960/processador-intel-core-i3-10100f-3-6ghz-4-3ghz-max-boost-cache-6mb-quad-core-8-threads-lga-1200-bx8070110100f?utm_source=chatgpt.com', 1),
  ('Intel Core i3-12100F', 1100.00, 'https://img.kabum.com.br/i3-12100f.jpg', 'https://kabum.com.br/produto/i3-12100f', 1),
  ('Intel Core i5-12400F', 1800.00, 'https://img.kabum.com.br/i5-12400f.jpg', 'https://kabum.com.br/produto/i5-12400f', 1),
  ('Intel Core i7-12700F', 3500.00, 'https://img.kabum.com.br/i7-12700f.jpg', 'https://kabum.com.br/produto/i7-12700f', 1),
  ('Intel Core i9-12900K', 6500.00, 'https://img.kabum.com.br/i9-12900k.jpg', 'https://kabum.com.br/produto/i9-12900k', 1);

-- PROCESSADORES AMD
INSERT INTO processadores (nome, preco, imagem_url, link_loja, socket_id)
VALUES
  ('AMD Ryzen 3 4100', 800.00, 'https://img.kabum.com.br/ryzen-4100.jpg', 'https://kabum.com.br/produto/ryzen-4100', 2),
  ('AMD Ryzen 5 5600G', 1100.00, 'https://img.kabum.com.br/ryzen-5600g.jpg', 'https://kabum.com.br/produto/ryzen-5600g', 2),
  ('AMD Ryzen 7 5700', 2200.00, 'https://img.kabum.com.br/ryzen-5700.jpg', 'https://kabum.com.br/produto/ryzen-5700', 2),
  ('AMD Ryzen 7 7800X3D', 4500.00, 'https://img.kabum.com.br/ryzen-7800x3d.jpg', 'https://kabum.com.br/produto/ryzen-7800x3d', 2),
  ('AMD Ryzen 9 7950X', 6800.00, 'https://img.kabum.com.br/ryzen-7950x.jpg', 'https://kabum.com.br/produto/ryzen-7950x', 2);

-- PLACAS‑MÃE (Intel/AMD)
INSERT INTO placas_mae (nome, preco, imagem_url, link_loja, socket_id)
VALUES
  ('ASUS Prime H510M‑E', 400.00, 'https://img.kabum.com.br/h510m.jpg', 'https://kabum.com.br/produto/h510m', 1),
  ('ASRock A520M‑HVS', 400.00, 'https://img.kabum.com.br/a520m.jpg', 'https://kabum.com.br/produto/a520m', 2),
  ('Gigabyte B550M DS3H', 600.00, 'https://img.kabum.com.br/b550m.jpg', 'https://kabum.com.br/produto/b550m', 2),
  ('ASUS B660M‑K D4', 700.00, 'https://img.kabum.com.br/b660m.jpg', 'https://kabum.com.br/produto/b660m', 1),
  ('ASUS X670‑P WiFi', 1400.00, 'https://img.kabum.com.br/x670.jpg', 'https://kabum.com.br/produto/x670', 2);

-- MEMÓRIAS RAM
INSERT INTO memorias_ram (nome, preco, imagem_url, link_loja, tipo)
VALUES
  ('Crucial Ballistix 8GB 2666MHz', 120.00, 'https://img.kabum.com.br/ballistix2666.jpg', 'https://kabum.com.br/produto/ram1', 'DDR4'),
  ('Kingston Fury Beast 8GB 3200MHz', 140.00, 'https://img.kabum.com.br/fury3200.jpg', 'https://kabum.com.br/produto/ram2', 'DDR4'),
  ('Corsair Vengeance LPX 16GB 3200MHz', 240.00, 'https://img.kabum.com.br/lpx3200.jpg', 'https://kabum.com.br/produto/ram3', 'DDR4'),
  ('XPG D41 RGB 16GB 3600MHz', 290.00, 'https://img.kabum.com.br/d41.jpg', 'https://kabum.com.br/produto/ram4', 'DDR4'),
  ('G.Skill Trident Z RGB 32GB 3600MHz', 600.00, 'https://img.kabum.com.br/tridentz.jpg', 'https://kabum.com.br/produto/ram5', 'DDR4');

-- PLACAS DE VÍDEO
INSERT INTO placas_video (nome, preco, imagem_url, link_loja)
VALUES
  ('Radeon RX 6400', 800.00, 'https://img.kabum.com.br/rx6400.jpg', 'https://kabum.com.br/produto/rx6400'),
  ('GeForce GTX 1650', 900.00, 'https://img.kabum.com.br/gtx1650.jpg', 'https://kabum.com.br/produto/gtx1650'),
  ('Radeon RX 6600', 1200.00, 'https://img.kabum.com.br/rx6600.jpg', 'https://kabum.com.br/produto/rx6600'),
  ('GeForce RTX 3060', 1800.00, 'https://img.kabum.com.br/rtx3060.jpg', 'https://kabum.com.br/produto/rtx3060'),
  ('GeForce RTX 4070 Ti Super', 3900.00, 'https://img.kabum.com.br/rtx4070ti.jpg', 'https://kabum.com.br/produto/rtx4070ti');

-- SSDs
INSERT INTO armazenamentos (nome, preco, imagem_url, link_loja, tipo)
VALUES
  ('Kingston A400 240GB', 120.00, 'https://img.kabum.com.br/a400.jpg', 'https://kabum.com.br/produto/a400', 'SATA'),
  ('Crucial BX500 480GB', 200.00, 'https://img.kabum.com.br/bx500.jpg', 'https://kabum.com.br/produto/bx500', 'SATA'),
  ('WD Green SN350 480GB', 240.00, 'https://img.kabum.com.br/sn350.jpg', 'https://kabum.com.br/produto/sn350', 'NVMe'),
  ('Kingston NV2 1TB', 330.00, 'https://img.kabum.com.br/nv2.jpg', 'https://kabum.com.br/produto/nv2', 'NVMe'),
  ('Samsung 980 PRO 1TB', 600.00, 'https://img.kabum.com.br/980pro.jpg', 'https://kabum.com.br/produto/980pro', 'NVMe');

-- FONTES
INSERT INTO fontes (nome, preco, imagem_url, link_loja, potencia)
VALUES
  ('PCYes Electro V2 400W', 150.00, 'https://img.kabum.com.br/electro.jpg', 'https://kabum.com.br/produto/electro', 400),
  ('Cougar STX 500W', 200.00, 'https://img.kabum.com.br/stx500.jpg', 'https://kabum.com.br/produto/stx500', 500),
  ('Corsair CV550 550W', 260.00, 'https://img.kabum.com.br/cv550.jpg', 'https://kabum.com.br/produto/cv550', 550),
  ('Corsair CX650M 650W', 390.00, 'https://img.kabum.com.br/cx650m.jpg', 'https://kabum.com.br/produto/cx650m', 650),
  ('Corsair RM750x 750W', 580.00, 'https://img.kabum.com.br/rm750x.jpg', 'https://kabum.com.br/produto/rm750x', 750);

-- GABINETES
INSERT INTO gabinetes (nome, preco, imagem_url, link_loja)
VALUES
  ('Bluecase BG-009', 150.00, 'https://img.kabum.com.br/bg009.jpg', 'https://kabum.com.br/produto/bg009'),
  ('PCYes Tiger', 200.00, 'https://img.kabum.com.br/tiger.jpg', 'https://kabum.com.br/produto/tiger'),
  ('Cooler Master Q300L', 250.00, 'https://img.kabum.com.br/q300l.jpg', 'https://kabum.com.br/produto/q300l'),
  ('Gamemax Expedition', 300.00, 'https://img.kabum.com.br/expedition.jpg', 'https://kabum.com.br/produto/expedition'),
  ('NZXT H510 Elite', 700.00, 'https://img.kabum.com.br/h510elite.jpg', 'https://kabum.com.br/produto/h510elite');

