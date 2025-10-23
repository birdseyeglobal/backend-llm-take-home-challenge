"""
Database migration script to add background task support to content_analysis table
"""
from sqlmodel import create_engine, text
from app.database import DATABASE_URL
import sys

def run_migration():
    """Run the database migration"""
    print("Starting database migration...")
    print(f"Connecting to database...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.begin() as conn:
            # Check if columns already exist
            print("Checking if migration is needed...")
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'content_analysis' 
                AND column_name IN ('status', 'error_message')
            """)
            result = conn.execute(check_query)
            existing_columns = [row[0] for row in result]
            
            if 'status' in existing_columns and 'error_message' in existing_columns:
                print("✓ Migration already applied - columns exist")
                return
            
            print("Running migration...")
            
            # Add status column if it doesn't exist
            if 'status' not in existing_columns:
                print("Adding 'status' column...")
                conn.execute(text("""
                    ALTER TABLE content_analysis 
                    ADD COLUMN status VARCHAR(20) DEFAULT 'pending'
                """))
                print("✓ Added 'status' column")
            
            # Add error_message column if it doesn't exist
            if 'error_message' not in existing_columns:
                print("Adding 'error_message' column...")
                conn.execute(text("""
                    ALTER TABLE content_analysis 
                    ADD COLUMN error_message TEXT
                """))
                print("✓ Added 'error_message' column")
            
            # Make warmth_score nullable
            print("Making 'warmth_score' nullable...")
            conn.execute(text("""
                ALTER TABLE content_analysis 
                ALTER COLUMN warmth_score DROP NOT NULL
            """))
            print("✓ Made 'warmth_score' nullable")
            
            # Make target_demographic nullable
            print("Making 'target_demographic' nullable...")
            conn.execute(text("""
                ALTER TABLE content_analysis 
                ALTER COLUMN target_demographic DROP NOT NULL
            """))
            print("✓ Made 'target_demographic' nullable")
            
            # Update existing records to have status='completed'
            print("Updating existing records...")
            result = conn.execute(text("""
                UPDATE content_analysis 
                SET status = 'completed' 
                WHERE status IS NULL OR status = ''
            """))
            rows_updated = result.rowcount
            print(f"✓ Updated {rows_updated} existing records to status='completed'")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    run_migration()

