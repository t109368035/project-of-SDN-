from DBControll.DBConnection import DBConnection


class AppTable:
    def insert_a_app(self, stime, user_ip, user_dhcp, user_port, server_name, 
                    server_ip, server_port, server_broadcast, protocol_L4, 
                    protocol_L7, first_seen, last_seen, duration, bytes):
        command = "INSERT INTO app_table (stime, user_ip, user_dhcp, user_port, server_name, server_ip, server_port, server_broadcast, protocol_L4, protocol_L7, first_seen, last_seen, duration, bytes) VALUES  ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(stime, user_ip, user_dhcp, user_port, server_name, server_ip, server_port, server_broadcast, protocol_L4, protocol_L7, first_seen, last_seen, duration, bytes)
            
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()

    def delete_user_app(self, user_ip):
        command = "DELETE FROM app_table WHERE user_ip='{}';".format(user_ip)

        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()

    def delete_all(self):
        command = "DELETE FROM app_table;"

        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()

"""
    def pop_user_rule(self, user_ip):
        command = "SELECT * FROM rule_table WHERE user_ip='{}';".format(user_ip)

        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()

        return [row['user_rule'] for row in record_from_db]

"""