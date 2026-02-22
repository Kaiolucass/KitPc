from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        print("🚀 Aumentando capacidade da coluna 'conteudo'...")
        
        # Comando para mudar de TEXT para LONGTEXT
        db.session.execute(text("ALTER TABLE posts MODIFY COLUMN conteudo LONGTEXT"))
        db.session.commit()
        
        print("\n✅ SUCESSO! Agora você pode postar textos e imagens gigantes.")
    except Exception as e:
        print(f"\n❌ Erro ao atualizar: {e}")