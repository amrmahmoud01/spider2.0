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
from sqlalchemy import select

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
            # STEP 1: Just collect the data. 
            # We REMOVED the query().first() here. This eliminates the 2-second lag per item.
            self.items_buffer.append(dict(item))

            # Only talk to the database when the buffer is full
            if len(self.items_buffer) >= self.batch_size:
                self.flush_to_db(spider)
            return item

    def flush_to_db(self, spider):
            if not self.items_buffer:
                return

            # 1. SAFETY CHECK: Ensure the session exists before proceeding
            if self.session is None:
                spider.logger.error("❌ Database Session is None. check open_spider logic.")
                return

            try:
                # --- STAGE 1: CLEAN DATA FOR THE PRODUCT TABLE ---
                # We must remove 'colors' and 'imageLink' because they don't exist in the Product table
                product_data = []
                for item in self.items_buffer:
                    d = dict(item) # Create a copy to preserve original data for the color stage
                    d.pop('colors', None)
                    d.pop('imageLink', None)
                    product_data.append(d)

                # --- STAGE 2: THE PRODUCT UPSERT ---
                # This tells MySQL: "Insert these 100 items. If the productLink already exists, update the prices/names."
                stmt = insert(Product).values(product_data)
                upsert_stmt = stmt.on_duplicate_key_update(
                    name=stmt.inserted.name,
                    price=stmt.inserted.price,
                    salePrice=stmt.inserted.salePrice,
                    type=stmt.inserted.type,
                    gender=stmt.inserted.gender,
                    storeId=stmt.inserted.storeId
                )
                
                self.session.execute(upsert_stmt)
                # flush() tells the DB to process the upserts so we can fetch the IDs in Stage 3
                self.session.flush()

                # --- STAGE 3: FETCH IDs FOR THE COLORS ---
                # We need the database-generated 'productId' to link colors to products
                links = [i['productLink'] for i in self.items_buffer]
                result = self.session.execute(
                    select(Product.productId, Product.productLink).where(Product.productLink.in_(links))
                )
                
                # Create a "Lookup Table" (Dictionary Mapping)
                # link_to_id = { "https://site.com/p1": 12345, ... }
                link_to_id = {row.productLink: row.productId for row in result}

                # --- STAGE 4: PREPARE AND INSERT COLORS ---
                colors_to_upsert = []
                for item in self.items_buffer:
                    p_id = link_to_id.get(item['productLink'])
                    if p_id:
                        for color in item.get("colors", []):
                            colors_to_upsert.append({
                                "productId": p_id,
                                "color": color
                            })

                if colors_to_upsert:
                    # INSERT IGNORE handles duplicates in the colors table automatically
                    color_stmt = insert(Productcolors).values(colors_to_upsert).prefix_with("IGNORE")
                    self.session.execute(color_stmt)

                # --- STAGE 5: FINAL COMMIT ---
                # This saves all 100 products and all their colors in one go
                self.session.commit()
                spider.logger.info(f"💾 Successfully bulk-saved {len(self.items_buffer)} items to DB.")
                self.items_buffer.clear()

            except Exception as e:
                # If ANY part of the 100-item batch fails, we undo the whole thing
                self.session.rollback()
                spider.logger.error(f"❌ Batch Failed: {e}")
                # Optional: clear buffer anyway to prevent infinite loops on bad data
                self.items_buffer.clear()

    def close_spider(self, spider):
        # Don't forget the last few items that didn't fill a full batch!
        if self.items_buffer:
            self.flush_to_db(spider)
        self.session.close()


# ------------------------
# Images pipeline
# ------------------------
# class MyImagesPipeline(ImagesPipeline):

#     def item_completed(self, results, item, info):
#         # results = list of tuples (success, image_info)
#         image_paths = [x['path'] for ok, x in results if ok]
#         if image_paths:
#             item['imageLink'] = image_paths[0]  # use first downloaded image
#         else:
#             item['imageLink'] = None
#         return item
