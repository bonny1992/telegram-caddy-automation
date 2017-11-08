import wmi
import win32serviceutil

def stop_service(servicename = 'Caddy'):
    try:
        win32serviceutil.StopService(servicename)
        return True
    except:
        return False

def restart_service(servicename = 'Caddy'):
    try:
        win32serviceutil.RestartService(servicename)
        return True
    except:
        return False

def start_service(servicename = 'Caddy'):
    try:
        win32serviceutil.StartService(servicename)
        return True
    except:
        return False

def get_service(servicename = 'Caddy'):
    try:
        service_handler = wmi.WMI()
        service = service_handler.Win32_Service(name=servicename)
        if srv != []:
            return service.Status
        return False
        # status = win32serviceutil.QueryServiceStatus(servicename)
        # return status
    except:
        return False
