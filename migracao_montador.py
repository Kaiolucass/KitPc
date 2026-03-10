from app import app, db
from sqlalchemy import text

def run_migration():
    with app.app_context():
        try:
            print("🚀 Iniciando migração do banco de dados do montador...")
            
            # Adicionando TDP em Processadores
            try:
                db.session.execute(text("ALTER TABLE processadores ADD COLUMN tdp INT DEFAULT 65"))
                print("✅ Coluna 'tdp' adicionada em 'processadores'")
            except Exception as e:
                print(f"⚠️ Aviso ao alterar 'processadores' (talvez já exista): {e}")

            # Adicionando colunas em Placas-Mãe
            try:
                db.session.execute(text("ALTER TABLE placas_mae ADD COLUMN tipo_memoria VARCHAR(20) DEFAULT 'DDR4'"))
                db.session.execute(text("ALTER TABLE placas_mae ADD COLUMN tamanho VARCHAR(20) DEFAULT 'Micro-ATX'"))
                print("✅ Colunas 'tipo_memoria' e 'tamanho' adicionadas em 'placas_mae'")
            except Exception as e:
                print(f"⚠️ Aviso ao alterar 'placas_mae': {e}")
                
            # Adicionando TDP em Placas de Vídeo
            try:
                db.session.execute(text("ALTER TABLE placas_video ADD COLUMN tdp INT DEFAULT 0"))
                print("✅ Coluna 'tdp' adicionada em 'placas_video'")
            except Exception as e:
                print(f"⚠️ Aviso ao alterar 'placas_video': {e}")

            # Adicionando tamanho suportado em Gabinetes
            try:
                db.session.execute(text("ALTER TABLE gabinetes ADD COLUMN tamanho_suportado VARCHAR(50) DEFAULT 'ATX, Micro-ATX, Mini-ITX'"))
                print("✅ Coluna 'tamanho_suportado' adicionada em 'gabinetes'")
            except Exception as e:
                print(f"⚠️ Aviso ao alterar 'gabinetes': {e}")

            db.session.commit()
            print("\n🎉 Migração concluída com sucesso! Fique tranquilo, seus dados não foram perdidos.")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Erro geral na migração: {e}")

if __name__ == '__main__':
    run_migration()
