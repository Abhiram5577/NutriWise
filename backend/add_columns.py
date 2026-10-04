from app.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    try:
        conn.execute(text('ALTER TABLE health_profiles ADD COLUMN medical_conditions VARCHAR(500)'))
        conn.execute(text('ALTER TABLE health_profiles ADD COLUMN health_goals VARCHAR(500)'))
        conn.commit()
        print('Columns added successfully.')
    except Exception as e:
        print('Error:', e)
