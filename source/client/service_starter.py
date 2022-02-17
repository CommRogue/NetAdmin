import sys
import win32service
import win32serviceutil
import servicemanager
import main

class MainServiceImplementation:
    def run(self):
        main.main()

    def stop(self):
        main.process_status.set(False)


class MainServiceFramework(win32serviceutil.ServiceFramework):
    _svc_name_ = "NetAdmin_Service"
    _svc_display_name_ = "NetAdmin Background Service"

    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.service_impl.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        """Start the service; does not return until stopped"""
        print("STARTING NETADMIN SERVICE")
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.service_impl = MainServiceImplementation()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        # Run the service
        self.service_impl.run()

def init():
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MainServiceFramework)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MainServiceFramework)


if __name__ == '__main__':
    init()