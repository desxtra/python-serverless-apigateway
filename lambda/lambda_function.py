import json
import os
import pymysql
import logging

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Database configuration - diisi dari environment variables di Lambda
DB_HOST = os.environ.get('DB_HOST', '')
DB_USER = os.environ.get('DB_USER', '')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', '')

def get_db_connection():
    """Membuat koneksi ke database RDS"""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connect_timeout=5
        )
        return conn
    except pymysql.MySQLError as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return None

def create_table_if_not_exists(conn):
    """Membuat tabel items jika belum ada"""
    with conn.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

def handle_get(path_params, query_params):
    """Handle GET requests - Read data"""
    conn = get_db_connection()
    if not conn:
        return {"statusCode": 500, "body": json.dumps({"error": "Database connection failed"})}
    
    try:
        create_table_if_not_exists(conn)
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get specific item if id is provided
            if path_params and 'id' in path_params:
                item_id = path_params['id']
                cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
                item = cursor.fetchone()
                if item:
                    return {"statusCode": 200, "body": json.dumps(item, default=str)}
                else:
                    return {"statusCode": 404, "body": json.dumps({"error": "Item not found"})}
            # Get all items
            else:
                cursor.execute("SELECT * FROM items")
                items = cursor.fetchall()
                return {"statusCode": 200, "body": json.dumps(items, default=str)}
    except Exception as e:
        logger.error(f"Error in GET handler: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
    finally:
        conn.close()

def handle_post(body):
    """Handle POST requests - Create data"""
    if not body:
        return {"statusCode": 400, "body": json.dumps({"error": "Request body is required"})}
    
    conn = get_db_connection()
    if not conn:
        return {"statusCode": 500, "body": json.dumps({"error": "Database connection failed"})}
    
    try:
        create_table_if_not_exists(conn)
        data = json.loads(body)
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return {"statusCode": 400, "body": json.dumps({"error": "Name is required"})}
        
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO items (name, description) VALUES (%s, %s)",
                (name, description)
            )
            conn.commit()
            
            # Get the ID of the inserted item
            item_id = cursor.lastrowid
            
        return {
            "statusCode": 201, 
            "body": json.dumps({"id": item_id, "name": name, "description": description})
        }
    except Exception as e:
        logger.error(f"Error in POST handler: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
    finally:
        conn.close()

def handle_put(path_params, body):
    """Handle PUT requests - Update data"""
    if not path_params or 'id' not in path_params:
        return {"statusCode": 400, "body": json.dumps({"error": "Item ID is required"})}
    
    if not body:
        return {"statusCode": 400, "body": json.dumps({"error": "Request body is required"})}
    
    conn = get_db_connection()
    if not conn:
        return {"statusCode": 500, "body": json.dumps({"error": "Database connection failed"})}
    
    try:
        create_table_if_not_exists(conn)
        item_id = path_params['id']
        data = json.loads(body)
        
        # Check if the item exists
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
            if cursor.fetchone() is None:
                return {"statusCode": 404, "body": json.dumps({"error": "Item not found"})}
            
            # Update the item
            update_fields = []
            params = []
            
            if 'name' in data:
                update_fields.append("name = %s")
                params.append(data['name'])
            
            if 'description' in data:
                update_fields.append("description = %s")
                params.append(data['description'])
            
            if not update_fields:
                return {"statusCode": 400, "body": json.dumps({"error": "No fields to update"})}
            
            params.append(item_id)  # For the WHERE clause
            
            query = f"UPDATE items SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(query, params)
            conn.commit()
            
            # Get updated item
            cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
            updated_item = cursor.fetchone()
            
        return {"statusCode": 200, "body": json.dumps({"message": "Item updated", "id": item_id})}
    except Exception as e:
        logger.error(f"Error in PUT handler: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
    finally:
        conn.close()

def handle_delete(path_params):
    """Handle DELETE requests - Delete data"""
    if not path_params or 'id' not in path_params:
        return {"statusCode": 400, "body": json.dumps({"error": "Item ID is required"})}
    
    conn = get_db_connection()
    if not conn:
        return {"statusCode": 500, "body": json.dumps({"error": "Database connection failed"})}
    
    try:
        create_table_if_not_exists(conn)
        item_id = path_params['id']
        
        # Check if the item exists
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM items WHERE id = %s", (item_id,))
            if cursor.fetchone() is None:
                return {"statusCode": 404, "body": json.dumps({"error": "Item not found"})}
            
            # Delete the item
            cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
            conn.commit()
            
        return {"statusCode": 200, "body": json.dumps({"message": "Item deleted", "id": item_id})}
    except Exception as e:
        logger.error(f"Error in DELETE handler: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
    finally:
        conn.close()

def handle_patch(path_params, body):
    """Handle PATCH requests - Partial update"""
    # Implementasi sama dengan PUT tapi dengan konsep partial update
    return handle_put(path_params, body)

def lambda_handler(event, context):
    """Main Lambda handler function"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Extract HTTP method
    http_method = event.get('httpMethod', '').upper()
    
    # Extract path parameters
    path_params = event.get('pathParameters', {})
    
    # Extract query parameters
    query_params = event.get('queryStringParameters', {})
    
    # Extract request body
    body = event.get('body')
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,PATCH,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # Handle OPTIONS requests for CORS pre-flight
    if http_method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'CORS preflight request successful'})
        }
    
    # Route requests based on HTTP method
    handler_map = {
        'GET': handle_get,
        'POST': handle_post,
        'PUT': handle_put,
        'DELETE': handle_delete,
        'PATCH': handle_patch
    }
    
    if http_method in handler_map:
        # Call the appropriate handler
        if http_method == 'GET':
            result = handler_map[http_method](path_params, query_params)
        elif http_method in ['POST']:
            result = handler_map[http_method](body)
        elif http_method in ['PUT', 'PATCH']:
            result = handler_map[http_method](path_params, body)
        elif http_method == 'DELETE':
            result = handler_map[http_method](path_params)
        else:
            result = {"statusCode": 405, "body": json.dumps({"error": "Method not allowed"})}
    else:
        result = {"statusCode": 405, "body": json.dumps({"error": "Method not supported"})}
    
    # Add CORS headers to response
    result['headers'] = headers
    
    return result