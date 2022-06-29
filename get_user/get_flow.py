import subprocess, time
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from DBControll.ConnectDatabase import ConnectDatabase
from DBControll.AppTable import AppTable
from DBControll.UserTable import UserTable
from sdn_controller.SetRule import SetRule

'''
擷取在map的live flow
'''
class Get_Live_Flow(QThread):
    user_table_fresh = pyqtSignal(list)
    stop_getflow = pyqtSignal(str)
    def __init__(self, node):
        super().__init__()
        self.node = node
        ConnectDatabase()
        self.ftimer = QTimer(self)
        self.ftimer.timeout.connect(self.store_user_flow)
        self.ftimer.start(20000)
        self.dict_user_to_server = dict()
    
    def run(self):
        print('\n\n===========\nstart getflow{} : {}\n===========\n\n'.format(self.node, time.ctime()))

    def row_data_proccess(self, raw_data):
        try:
            raw_data = raw_data.decode('utf-8')
            raw_data = raw_data.replace('true','"true"')
            raw_data = raw_data.replace('false','"false"')
            dict_data = eval(raw_data)
        except:
            return None
        if raw_data != '':
            all_live_flow = dict_data['rsp']['data']
            return all_live_flow
        else:
            return None

    def get_row_data(self):        
        #####get live flow
        cmd = 'curl -u admin:eelab210 "http://192.168.1.{}:3000/lua/rest/v2/get/flow/active.lua?ifid=1"'.format(self.node)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data, err = p.communicate()
        return self.row_data_proccess(raw_data)
  
    def store_user_flow(self):
        ap = 'map{}'.format(self.node)
        AppTable().delete_AP_app(ap)
        store_time = time.ctime()
        user_list = UserTable().pop_AP_user(ap)
        flow_list = self.get_row_data()
        check_user_list = set()
        if user_list and flow_list:
            for user in user_list:
                for flow in flow_list:
                    client_ip = flow['client']['ip']
                    Layer7 = flow['protocol']['l7']
                    server_ip = flow['server']['ip']
                    if user == client_ip:
                        AppTable().insert_a_app(ap ,store_time, user,flow['client']['port'],flow['server']['name'],
                                                server_ip,flow['server']['port'],flow['protocol']['l4'], 
                                                Layer7, flow['first_seen'], flow['last_seen'],flow['duration'], flow['bytes'])
                        check_user_list.add(user)
                        self.determin_service(server_ip=server_ip, client_ip=client_ip)
            self.delete_user(user_list, check_user_list)
        elif not user_list and flow_list:
            self.ftimer.stop()
            self.stop_getflow.emit('{} stop'.format(ap))
        elif user_list and not flow_list:
            print('\n\n\n==============\nntop出問題了 : {}\n==============\n\n\n'.format(store_time))
            self.ftimer.stop()
            self.stop_getflow.emit('{} stop'.format(ap))

    def delete_user(self, original_user_list, check_user_list):
        delete_user = list()
        for user in original_user_list:
            if user not in check_user_list:
                delete_user.append(user)
        if delete_user:
            self.user_table_fresh.emit(delete_user)

    def determin_service(self, server_ip, client_ip):
        if not self.dict_user_to_server.get(client_ip):
            self.dict_user_to_server[client_ip] = list()
        user_info = UserTable().pop_user_info(user_ip=client_ip)
        ap = user_info['user_ap']
        if server_ip == '10.10.3.100' and '10.10.3.100' not in self.dict_user_to_server[client_ip]:
            self.dict_user_to_server[client_ip].append(server_ip)
            app_type = 'Mission'
            SetRule().excute(user_ip=client_ip, ap=ap, app_type=app_type, server_ip=server_ip)
        elif server_ip == '192.168.1.143' and '192.168.1.143' not in self.dict_user_to_server[client_ip]:
            self.dict_user_to_server[client_ip].append(server_ip)
            app_type = 'Massive'
            SetRule().excute(user_ip=client_ip, ap=ap, app_type=app_type, server_ip=server_ip)
            