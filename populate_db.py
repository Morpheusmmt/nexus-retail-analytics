import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

DB_CONFIG = {
    'dbname': 'nexus_dw',
    'user': 'admin',
    'password': 'admin_password',
    'host': 'localhost',
    'port': '5432'
}

fake = Faker('pt_BR') 

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_data():
    conn = get_connection()
    cur = conn.cursor()
    
    print("🚀 Iniciando a ingestão de dados...")

    # 1. Criar USUÁRIOS 
    print("👤 Gerando 100 clientes...")
    user_ids = []
    for _ in range(100):
        name = fake.name()
        email = fake.email()
        city = fake.city()
        state = fake.state_abbr()
        cur.execute(
            "INSERT INTO users (name, email, city, state) VALUES (%s, %s, %s, %s) RETURNING user_id",
            (name, email, city, state)
        )
        user_ids.append(cur.fetchone()[0])

    # 2. Criar PRODUTOS 
    print("📦 Gerando 50 produtos...")
    product_ids = []
    categories = ['Eletrônicos', 'Roupas', 'Casa', 'Esporte', 'Livros']
    for _ in range(50):
        prod_name = fake.word().capitalize() + " " + fake.word().capitalize()
        category = random.choice(categories)
        price = round(random.uniform(50.0, 5000.0), 2)
        cost = round(price * 0.6, 2)
        cur.execute(
            "INSERT INTO products (product_name, category, price, cost) VALUES (%s, %s, %s, %s) RETURNING product_id",
            (prod_name, category, price, cost)
        )
        product_ids.append(cur.fetchone()[0])

    # 3. Criar PEDIDOS e ITENS 
    print("�� Gerando 300 pedidos com histórico...")
    statuses = ['Completed', 'Pending', 'Cancelled', 'Shipped']
    
    for _ in range(300):
        user_id = random.choice(user_ids)
        order_date = fake.date_time_between(start_date='-6m', end_date='now')
        status = random.choice(statuses)
        
        cur.execute(
            "INSERT INTO orders (user_id, order_date, status, total_amount) VALUES (%s, %s, %s, 0) RETURNING order_id",
            (user_id, order_date, status)
        )
        order_id = cur.fetchone()[0]

        total_amount = 0
        num_items = random.randint(1, 5)
        
        for _ in range(num_items):
            prod_id = random.choice(product_ids)
            qty = random.randint(1, 3)
            cur.execute("SELECT price FROM products WHERE product_id = %s", (prod_id,))
            unit_price = cur.fetchone()[0]
            
            total = qty * unit_price
            total_amount += total
            
            cur.execute(
                (order_id, prod_id, qty, unit_price)
            )
        
        cur.execute("UPDATE orders SET total_amount = %s WHERE order_id = %s", (total_amount, order_id))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Sucesso! Banco de dados populado com dados fake.")

if __name__ == "__main__":
    create_data()
