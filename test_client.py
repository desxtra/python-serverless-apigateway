import requests
import json
import argparse

class HttpMethodsClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        
    def test_all_methods(self):
        """Test semua HTTP methods secara berurutan"""
        print("Memulai test semua HTTP methods...")
        
        # 1. OPTIONS request untuk CORS preflight
        print("\n===== TEST OPTIONS METHOD =====")
        self.test_options()
        
        # 2. POST untuk membuat item baru
        print("\n===== TEST POST METHOD =====")
        item_id = self.test_post()
        
        if item_id:
            # 3. GET untuk mendapatkan semua item
            print("\n===== TEST GET ALL METHOD =====")
            self.test_get_all()
            
            # 4. GET untuk mendapatkan item spesifik
            print(f"\n===== TEST GET ONE METHOD (ID: {item_id}) =====")
            self.test_get_one(item_id)
            
            # 5. PUT untuk update item
            print(f"\n===== TEST PUT METHOD (ID: {item_id}) =====")
            self.test_put(item_id)
            
            # 6. PATCH untuk update sebagian item
            print(f"\n===== TEST PATCH METHOD (ID: {item_id}) =====")
            self.test_patch(item_id)
            
            # 7. DELETE untuk menghapus item
            print(f"\n===== TEST DELETE METHOD (ID: {item_id}) =====")
            self.test_delete(item_id)
            
            # 8. GET lagi untuk memastikan item terhapus
            print(f"\n===== VERIFY DELETE (ID: {item_id}) =====")
            self.test_get_one(item_id)
        
        print("\nTest selesai!")
        
    def test_options(self):
        """Test OPTIONS method untuk CORS preflight"""
        url = f"{self.base_url}/items"
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
        return response.status_code == 200
        
    def test_post(self):
        """Test POST method - Create item"""
        url = f"{self.base_url}/items"
        data = {
            "name": "Test Item",
            "description": "This is a test item created by the Python client"
        }
        
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return result.get('id')
        else:
            print(f"Error: {response.text}")
            return None
            
    def test_get_all(self):
        """Test GET method - Get all items"""
        url = f"{self.base_url}/items"
        
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Found {len(result)} items")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
        
    def test_get_one(self, item_id):
        """Test GET method - Get specific item"""
        url = f"{self.base_url}/items/{item_id}"
        
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    def test_put(self, item_id):
        """Test PUT method - Update item"""
        url = f"{self.base_url}/items/{item_id}"
        data = {
            "name": "Updated Test Item",
            "description": "This item was updated with PUT method"
        }
        
        response = requests.put(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    def test_patch(self, item_id):
        """Test PATCH method - Partial update"""
        url = f"{self.base_url}/items/{item_id}"
        data = {
            "description": "This description was updated with PATCH method"
        }
        
        response = requests.patch(url, json=data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    def test_delete(self, item_id):
        """Test DELETE method - Delete item"""
        url = f"{self.base_url}/items/{item_id}"
        
        response = requests.delete(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test API dengan berbagai HTTP methods")
    parser.add_argument("--url", required=True, help="Base URL dari API Gateway endpoint")
    
    args = parser.parse_args()
    
    client = HttpMethodsClient(args.url)
    client.test_all_methods()