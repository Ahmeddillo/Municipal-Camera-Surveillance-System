import os
import time
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import Json, RealDictCursor
from psycopg2.pool import SimpleConnectionPool

# .env dosyasındaki gizli değişkenleri yükle
load_dotenv()


class DatabaseManager:

  def __init__(self):
    # Hassas bilgiler koda yazılmaz, ortam değişkenlerinden (Environment Variables) çekilir.
    self.config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "database": os.getenv("DB_NAME", "belediye_kamera_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "port": os.getenv("DB_PORT", "5432"),
    }
    self.pool = None
    self.max_retry = 3
    self.retry_delay = 2

  def connect(self):
    for i in range(self.max_retry):
      try:
        self.pool = SimpleConnectionPool(minconn=1, maxconn=10, **self.config)
        print("✅ PostgreSQL bağlantı havuzu oluşturuldu")
        self.create_tables()
        return True
      except Exception as e:
        print(f"⚠️ Bağlantı hatası ({i+1}/{self.max_retry}): {e}")
        time.sleep(self.retry_delay)
    return False

  def get_connection(self):
    if not self.pool:
      if not self.connect():
        raise Exception("PostgreSQL bağlantısı kurulamadı")
    return self.pool.getconn()

  def return_connection(self, conn):
    if self.pool and conn:
      self.pool.putconn(conn)

  def create_tables(self):
    conn = self.get_connection()
    try:
      with conn.cursor() as cur:
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS kameralar (
                        id SERIAL PRIMARY KEY,
                        ad VARCHAR(255) NOT NULL,
                        konum VARCHAR(255),
                        rtsp_url VARCHAR(500),
                        aktif BOOLEAN DEFAULT true,
                        olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS dakikalik_olculer (
                        id SERIAL PRIMARY KEY,
                        kamera_id INTEGER REFERENCES kameralar(id),
                        baslangic_zamani TIMESTAMP,
                        bitis_zamani TIMESTAMP,
                        toplam_kisi INTEGER,
                        ortalama_kisi FLOAT,
                        maksimum_kisi INTEGER,
                        minimum_kisi INTEGER,
                        fps_ortalamasi FLOAT,
                        detaylar JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
        # Diğer tablo oluşturma sorguların aynı kalabilir...
        conn.commit()
        print("✅ Veritabanı tabloları oluşturuldu")
    except Exception as e:
      print(f"⚠️ Tablo oluşturma hatası: {e}")
      conn.rollback()
    finally:
      self.return_connection(conn)

  # Diğer fonksiyonların (dakikalik_kaydet, anlik_kaydet vb.) aynen kalabilir...

  def close(self):
    if self.pool:
      self.pool.closeall()
      print("🔒 PostgreSQL bağlantıları kapatıldı")
