import sqlite3


class BookingsUtils:
    def __init__(self, database):
        self.database = database

        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS bookings
                    (booking_id VARCHAR PRIMARY KEY,
                    user_id VARCHAR,
                    hall_id VARCHAR,
                    requested_on DATE,
                    start_date DATE,
                    end_date DATE,
                    purpose VARCHAR,
                    status VARCHAR
                )''')

        print('Initialized bookings table')

        conn.commit()
        conn.close()


    def insert_records(self, input_records):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        # input_records = (booking_id, user_id, hall_id, requested_on, start_date, end_date, purpose, status)
        c.execute("INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?, ?, ?)", tuple(input_records))

        print("Inserted new record into bookings table")

        conn.commit()
        conn.close()


    def retrieve_records(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        # Fetch all bookings (adjust query for specific needs)
        c.execute('SELECT * FROM bookings')
        
        data = c.fetchall()

        conn.commit()
        conn.close()
        return data  # Returns a list of tuples
    

    def update_records(self, record_id, field, new_value):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        # Update booking
        c.execute(f"""
        UPDATE bookings
        SET {field} = ?
        WHERE booking_id = ?
        """, (new_value, record_id))

        print(f"Updated the value of {field} for booking_id {record_id} with {new_value}")

        conn.commit()
        conn.close()

    
    def delete_records(self, record_id):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        # Delete booking
        c.execute("DELETE FROM bookings WHERE booking_id = ?", (record_id,))

        print(f"Deleted the record for booking_id {record_id}")
        
        conn.commit()
        conn.close()



class HallsUtils:
    def __init__(self,database):
        self.database = database

        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS halls (
                    hall_id VARCHAR PRIMARY KEY,
                    hall_name VARCHAR,
                    capacity INT,
                    description VARCHAR,
                    img_url VARCHAR
                )''')

        print('Initialized halls table')

        conn.commit()
        conn.close()


    def insert_records(self, input_records):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        # input_records = (hall_id, hall_name, capacity, description, img_url)
        c.execute("INSERT INTO halls VALUES (?, ?, ?, ?, ?)", tuple(input_records))

        print("Inserted new record into halls table")

        conn.commit()
        conn.close()


    def retrieve_records(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()

       # Fetch all the halls(adjust query for specific needs)
        c.execute('SELECT * FROM halls')
        data = c.fetchall()

        conn.commit()
        conn.close()
        return data  # Returns a list of tuples
    

    def update_records(self, record_id, field, new_value):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        # Update halls
        c.execute(f"""
        UPDATE halls
        SET {field} = ?
        WHERE hall_id = ?
        """, (new_value, record_id))

        print(f"Updated the value of {field} for hall_id {record_id} with {new_value}")

        conn.commit()
        conn.close()

    
    def delete_records(self, record_id):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        # Delete booking
        c.execute("DELETE FROM halls WHERE hall_id = ?", (record_id,))

        print(f"Deleted the record for hall_id {record_id}")
        
        conn.commit()
        conn.close()


class CustomQuery:
    def __init__(self, database):
        self.database = database


    def fetch_available_halls_between_dates(self, start_date, end_date):
        conn = sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES)
        c = conn.cursor()

        c.execute("""
        SELECT DISTINCT halls.*
        FROM halls
        LEFT JOIN bookings
            ON halls.hall_id = bookings.hall_id
        WHERE (bookings.start_date IS NULL OR bookings.end_date IS NULL)
            OR (
                (
                    (bookings.start_date > ?) OR 
                    (bookings.end_date < ?)
                ) 
                OR (bookings.status != 'Approved')
            )
        ORDER BY halls.hall_name ASC;
        """, (end_date, start_date))

        data = c.fetchall()
        conn.close()

        return data


    def fetch_booking_requests_by_username(self, username, order_by="ASC"):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        c.execute(f"SELECT * FROM bookings WHERE user_id = ? ORDER BY requested_on {order_by}", (username,))

        data = c.fetchall()
        conn.close()

        return data

    
    def fetch_hall_name_and_image_by_hall_id(self, hall_id):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()

        c.execute("SELECT hall_name, img_url FROM halls WHERE hall_id = ?", (hall_id,))

        data = c.fetchall()
        conn.close()

        return data
    

    def fetch_booking_requests_by_booking_status(self, is_pending=True, sorted_in_asc=True):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        if is_pending:
            comparision_operator = "="
        else:
            comparision_operator = "!="

        if sorted_in_asc:
            sorting_order = "ASC"
        else: sorting_order = "DESC"

        cursor.execute(f"""
        SELECT *
        FROM bookings
        WHERE status {comparision_operator} 'Pending'
        ORDER BY requested_on {sorting_order}
        """)

        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return data

    
    def fetch_hall_details_by_hall_id(self, hall_id):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT *
        FROM halls
        WHERE hall_id = ?
        """, (hall_id,))

        data = cursor.fetchone()

        cursor.close()
        conn.close()

        return data
    

    def fetch_bookings_between_dates(self, hall_id, start_date, end_date):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT *
        FROM bookings
        WHERE hall_id = ? AND
            start_date <= ? AND
            end_date >= ? AND
            status != 'Rejected'
        ORDER BY requested_on ASC
        """, (hall_id, end_date, start_date))

        data = cursor.fetchall()

        cursor.close()
        conn.close()

        return data


if __name__ == "__main__":
    bookings = Bookings("test_database.db")

    booking_id = "BOOK123"
    user_id = "USER456"
    hall_id = "HALL789"  # Assuming hall already exists with this ID
    requested_on = "2024-02-07"
    start_date = "2024-02-10"
    end_date = "2024-02-12"
    purpose = "Meeting"
    status = "Pending"

    booking_data_1 = (booking_id, user_id, hall_id, requested_on, start_date, end_date, purpose, status)

    booking_id = "BOOK456"
    user_id = "USER123"
    hall_id = "HALL975"  # Assuming hall already exists with this ID
    requested_on = "2024-02-07"
    start_date = "2024-02-12"
    end_date = "2024-02-14"
    purpose = "Hackathon"
    status = "Approved"

    booking_data_2 = (booking_id, user_id, hall_id, requested_on, start_date, end_date, purpose, status)

    bookings.insert_records(booking_data_1)
    bookings.insert_records(booking_data_2)

    retrieved_data = bookings.retrieve_records()
    print(retrieved_data)

    bookings.update_records("BOOK123", 'status', 'Rejected')

    retrieved_data = bookings.retrieve_records()
    print(retrieved_data)

    #bookings.delete_records("BOOK456")

    #retrieved_data = bookings.retrieve_records()
    #print(retrieved_data)

    halls = Halls("test_database.db")

    hall_id = "seminar_hall_1"
    hall_name = "Seminar Hall 1"
    capacity = 220
    description = "Should be booked six days in adv"
    img_url = "assets/images/halls/seminar_hall_1.jpg"

    hall_name_1 = (hall_id, hall_name, capacity, description, img_url)

    hall_id = "seminar_hall_2"
    hall_name = "Seminar Hall 2"
    capacity = 220
    description = "Should be booked six days in adv"
    img_url = "assets/images/halls/seminar_hall_1.jpg"

    hall_name_2 = (hall_id, hall_name, capacity, description, img_url)

    halls.insert_records(hall_name_1)
    halls.insert_records(hall_name_2)

    retrieved_data = halls.retrieve_records()
    print(retrieved_data)

    halls.update_records("seminar_hall_2", 'capacity', '300')

    retrieved_data = halls.retrieve_records()
    print(retrieved_data)

    #halls.delete_records("seminar_hall_1")

    #retrieved_data = halls.retrieve_records()
    #print(retrieved_data)
