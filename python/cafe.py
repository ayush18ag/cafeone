import mysql.connector
from datetime import datetime
import streamlit as st

def create_connection():
    return mysql.connector.connect(
        host= "localhost",
        user= "root",
        password= "AYUSH@2004",
        database = "cafe"
    )

conn = create_connection()
cursor = conn.cursor()

cursor.execute("""
    create table if not exists menu(
        item_id int PRIMARY key,
        itme_name varchar(255),
        price decimal (10,2)
    ) 

""")

cursor.execute("""
        create table if not exists customer(
            customer_id int auto_increment  primary key,
            customer_name varchar(200)
            
        )            
""")
cursor.execute("""
               CREATE TABLE IF NOT EXISTS orders (
                    order_id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_id INT,
                    item_id INT,
                    quantity INT,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
                    FOREIGN KEY (item_id) REFERENCES menu(item_id)
)
""")

# sample_menu_items = [
#     (1, "Espresso", 2.5), (2, "Cappuccino", 3.0), (3, "Latte", 3.5), (4, "Mocha", 4.0),
#     (5, "Americano", 2.75), (6, "Black Coffee", 2.0), (7, "Green Tea", 2.5), (8, "Herbal Tea", 3.0),
#     (9, "Hot Chocolate", 3.5), (10, "Iced Coffee", 3.25), (11, "Smoothie", 4.5), (12, "Scone", 2.0),
#     (13, "Muffin", 2.5), (14, "Croissant", 3.0), (15, "Bagel", 1.5), (16, "Sandwich", 5.0),
#     (17, "Pasta", 6.0), (18, "Salad", 4.5), (19, "Brownie", 2.25), (20,"Cheesecake", 4.0)]

# cursor.executemany("insert into menu (item_id, itme_name, price) values(%s,%s,%s)",sample_menu_items)
# # # it is for when the data is alrady loaded and you are wanted to store this then use this
# # cursor.executemany("insert ignore into menu (item_id,item_name,price) values(%s,%s,%s)",sample_menu_items)

conn.commit()

class menuitem():
    def __init__(self,item_id,itme_name, price,quantity = 1):
        self.item_id = item_id
        self.item_name= itme_name
        self.price= price 
        self.quantity= quantity

class orders():
   
    def __init__(self,customer,item):
        self.item_id = item
        self.customer = customer
        self.order_date = datetime.now()
   
    def calculate_total(self):
        return(item["price"]*item["quantity"] for item in self.items)
class customers: 
    def __init__(self,name, contact):
        self.name= name
        self.contact = contact

class management:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def veiw_menu(self):
        self.cursor.execute("select * from menu")
        return [menuitem(item_id,item_name,price) for item_id,item_name,price in self.cursor.fetchall()]
   
    def add_customer(self,customer):
        self.cursor.execute("select customer_id from customer where customer_name= %s and contact =%s ",(customer.name,customer.contact ))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        self.cursor.execute("insert into customer (customer_name,contact) values (%s,%s)",(customer.name,customer.contact))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def place_order(self,customer,items):
        customer = self.add_customer(customer)
        for item in items:
            self.cursor.execute("insert into orders(customer_id,item_id,quantity)values(%s%s%s)",(customer.name ,item["item_id"],item.quantity))
        
    def view_order(self):
        self.cursor.execute("""
            select o.order_id,c.customer_name,m.item_name,o.quantity,o.order_date,m.price
            from orders o
            join customer c on o.customer_id= c.customer_id
            joint menu m on o.item_id = m.item_id
            order by o.order_date desc    
        
     """)
        return self.cursor.fetchall()

def main():
    system = management()   

    menu_items = system.veiw_menu()

    st.title("cafeone")
    st.header("cafe menu")
    for item in menu_items:
        st.write(f"{item.item_id} : {item.item_name} →  {item.price}")
    st.header("customer details")
    customer_name = st.text_input("Enter your name")
    customer_contact = st.text_input("Enter you  contact")
    
    if customer_name and customer_contact:
        customer = customers(customer_name,customer_contact)

        selected_items = []
        for item in menu_items:
            quantity = st.number_input(f"quantity for{item.item_name}($(item.price))",min_value=0,step=1, key=item.item_id)
        if quantity>0:
            selected_items.append({"item_id":item.item_id,"item:name": item.item_name,"price": item.price,"quantity":quantity})
            st.write(selected_items)
        if st.button("place order"):
            if selected_items:
                system.place_order(customer_name,selected_items)
                st.write("order placed")

                # oredersummery
                st.header("oredrsummery")
                total_price= sum(item["price"]*item["quantity"]for item in selected_items)
                st.write(f"customer: {customer_name}")
                for item in selected_items:
                    st.write(f"{item["item_name"]}-{item["quantity"]} x ${item["price"]:.2f} = ${item["price"]*item["quantity"]:.2f}")
                st.write(f"total price: ${total_price:.2f}")
            else:
                    st.warning("plese select atleast one item")
                    

if __name__ == "__main__":
    main()
