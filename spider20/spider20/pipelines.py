# pipelines.py

from itemadapter import ItemAdapter
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.mysql import insert
from scrapy.pipelines.images import ImagesPipeline
from spider20.models.models import Product, Productimages, Productcolors

class SpiderPipeline:
    def __init__(self, db_url, batch_size=100):


        # load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
        self.db_url = db_url

        self.batch_size = batch_size
        self.items_buffer = []
        self.engine = create_engine(
            # f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@"
            # f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
            db_url,
            echo=False
        )
        try:
            with self.engine.connect() as conn:
                result = conn.execute((text("SELECT 1")))
                print("✅ DB connection successful:", result.fetchone())
        except Exception as e:
            print("❌ DB connection failed:", e)
        self.session = None
        # Keep in-memory cache of product-color pairs to avoid duplicates in one run
        self.existing_colors_cache = set()

    @classmethod
    def from_crawler(cls, crawler):
        # Pull from settings.py instead of os.getenv directly
        settings = crawler.settings
        user = settings.get('DB_USER')
        password = settings.get('DB_PASS')
        host = settings.get('DB_HOST')
        port = settings.get('DB_PORT')
        db = settings.get('DB_NAME')
        
        # Build the URL safely
        db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
        return cls(db_url)
    
    def open_spider(self, spider):
        print("🚀 SpiderPipeline INITIALIZED")
        self.session = Session(self.engine)

    def process_item(self, item, spider):
        try:
            with self.session.no_autoflush:
                existing = self.session.query(Product).filter_by(
                    productLink=item["productLink"]
                ).first()

            if existing:
                # --- UPDATE EXISTING PRODUCT ---
                existing.name = item["name"]
                existing.price = item["price"]
                existing.salePrice = item["salePrice"]
                existing.type = item["type"]
                existing.gender = item["gender"]
                existing.storeId = item["storeId"]

                existing_image_urls = {img.URL for img in existing.productimages}
                if item["imageLink"] and item["imageLink"] not in existing_image_urls:
                    existing.productimages.append(Productimages(URL=item["imageLink"]))

                # # Update image if new
                # if item["imageLink"]:
                #     existing.productimages.append(Productimages(URL=item["imageLink"]))

                # Prepare colors to insert
                colors_to_add = []
                existing_colors = {c.color for c in existing.productcolors}
                for color in item.get("colors", []):
                    key = (existing.productId, color)
                    if color not in existing_colors and key not in self.existing_colors_cache:
                        colors_to_add.append({"productId": existing.productId, "color": color})
                        self.existing_colors_cache.add(key)

                # Bulk insert colors using INSERT IGNORE
                if colors_to_add:
                    stmt = insert(Productcolors).values(colors_to_add).prefix_with("IGNORE")
                    self.session.execute(stmt)

            else:
                # --- INSERT NEW PRODUCT ---
                product = Product(
                    name=item["name"],
                    price=item["price"],
                    salePrice=item["salePrice"],
                    type=item["type"],
                    gender=item["gender"],
                    storeId=item["storeId"],
                    productLink=item["productLink"]
                )

                # Add image
                if item["imageLink"]:
                    product.productimages.append(Productimages(URL=item["imageLink"]))

                self.session.add(product)
                self.session.flush()  # assigns productId from DB

                colors_to_add = []
                for color in item.get("colors", []):
                    key = (product.productId, color)  # <-- use productId, not id
                    if key not in self.existing_colors_cache:
                        colors_to_add.append({"productId": product.productId, "color": color})
                        self.existing_colors_cache.add(key)

                if colors_to_add:
                    stmt = insert(Productcolors).values(colors_to_add).prefix_with("IGNORE")
                    self.session.execute(stmt)


            self.items_buffer.append(item)

            # Batch commit
            if len(self.items_buffer) >= self.batch_size:
                self.flush_to_db()

            return item

        except IntegrityError as e:
            self.session.rollback()
            spider.logger.error(f"❌ IntegrityError: {e}")
            return item

        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"❌ Pipeline error: {e}")
            return item

    def flush_to_db(self):
        if not self.items_buffer:
            return
        try:
            print(f"💾 COMMITTING {len(self.items_buffer)} items")
            self.session.commit()
            self.items_buffer.clear()
            print("✅ COMMIT OK")
        except Exception as e:
            print("❌ COMMIT FAILED:", e)
            self.session.rollback()

    def close_spider(self, spider):
        # Commit remaining items
        if self.items_buffer:
            self.flush_to_db()
        self.session.close()


# ------------------------
# Images pipeline
# ------------------------
class MyImagesPipeline(ImagesPipeline):

    def item_completed(self, results, item, info):
        # results = list of tuples (success, image_info)
        image_paths = [x['path'] for ok, x in results if ok]
        if image_paths:
            item['imageLink'] = image_paths[0]  # use first downloaded image
        else:
            item['imageLink'] = None
        return item
