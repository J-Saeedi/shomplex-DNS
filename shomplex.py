import http.client
from functools import partial
import subprocess
from time import sleep, time
# import wmi

from tqdm import tqdm


class Timer:
    last_time = 0
    @staticmethod
    def tic():
        result = time()-Timer.last_time
        Timer.last_time = time()
        return result

class DoH:
    def __init__(self, doh_server):
        self.DoH_domain = doh_server.split("/dns-query")[0]
        self.conn = partial(http.client.HTTPSConnection, self.DoH_domain)

    def is_dns_working(self, website="www.youtube.com", timeout=5):
        self.conn = self.conn(timeout=timeout)
    
        try:
            self.conn.request("GET", f"/dns-query?dns={website}",\
                        headers={"Accept": "application/dns-message"})                
            response = self.conn.getresponse()
            response.read()  # read and discard the response body
            self.conn.close()
            # print("DoH server is working")
            return True       
        except Exception as e:
            # print("DoH server is not working", e)
            return False

class FileIO:
    @staticmethod
    def load_text_data(filename="doh_list.txt"):
        result = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                pretty_line = line.strip().lstrip("https://")
                if pretty_line:
                    result.append(pretty_line)
        return result

    @staticmethod
    def save_text_data(filename="doh_test_result.txt", data={}):
        with open(filename, 'w') as f:
            for d in dict(sorted(data.items(), key=lambda item: item[1])):
                # print(f"https://{d}")
                f.write(f"https://{d}")

class GoodServers:
    data = {}
    @staticmethod
    def add(url, ping, add_this=True):
        if add_this == True:
            GoodServers.data[url] = ping
    
    @staticmethod
    def print_data():
        result = ""
        for d in GoodServers.data:
            ping = f"{GoodServers.data[d]:.3f}"
            result += f"\nping: {ping.zfill(6)} - https://{d}\t"
        return "\n" + result         

class GoodByeDPI:
    def __init__(self):
        self.path_to_exe = r"goodbyedpi-0.2.2\x86_64\goodbyedpi.exe"
    def run_command(self, custom_command=False):
            command = [f"{self.path_to_exe}", " -2", "--dns-addr", "127.0.0.1"]
            try:
                self.process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE)
            except Exception as e:
                print("Error:", e)

    def start(self):
        self.run_command()
        sleep(1)

    def stop(self):
        self.process.kill()
        self.process.wait()

# class WindowsInterface:
#     def __init__(self):
#         wmiService = wmi.WMI()
#         networkConfigs = wmiService.Win32_NetworkAdapterConfiguration(IPEnabled=True)
#         for i in networkConfigs:
#             print(i.Caption, i.IPAddress[0])
#         # Set the DNS server to 127.0.0.1 for the first network interface
#         # networkConfigs[0].SetDNSServerSearchOrder(['127.0.0.1'])
#     def tui_select_network(self): pass

class DNSProxy:
    def __init__(self, dns_url_list):
        self.path_to_exe = r"dnsproxy\dnsproxy.exe"
        self.dns_url_list = []
        for dns in dns_url_list:
            self.dns_url_list.append("-u")
            self.dns_url_list.append(dns)

    def run_command(self, custom_command=False):
            command = [f"{self.path_to_exe}", *self.dns_url_list]
            try:
                self.process = subprocess.Popen(command, shell=False,\
                                                 stdout=subprocess.DEVNULL,\
                                                    stderr=subprocess.DEVNULL)
            except Exception as e:
                print("Error:", e)
    def is_ping_successful(self, address="youtube.com", timeout=500):
        response = subprocess.Popen(["ping", "-n", "3", "-w", str(timeout), address], stdout=subprocess.PIPE)
        output = response.communicate()[0]
        # print(output)
        if "100% loss" in output.decode("utf-8"):
            print("Host is down")
            return False
        else:
            print("Host is up")
            return True

    def start(self):
        self.run_command()
        sleep(4)

    def stop(self):
        self.process.kill()
        self.process.wait()


def main():
    server_list = FileIO.load_text_data('doh_list_light.txt')
    for i in tqdm(server_list):
        # print(i)
        Timer.tic()
        doh = DoH(i)
        check_result = doh.is_dns_working()
        ping = Timer.tic()
        GoodServers.add(i, ping, check_result)

    print(GoodServers.print_data())
    FileIO.save_text_data(data=GoodServers.data)


if __name__ == "__main__":
    # wi = WindowsInterface()
    bb = GoodByeDPI()
    dns = DNSProxy(["https://galileo.math.unipd.it/dns-query", "https://dns.tls-data.de/dns-query",\
"https://dns.apigw.online/dns-query", "https://resolver.unstoppable.io/dns-query"])
    
    dns.start()
    sleep(4)
    bb.start()
    dns.is_ping_successful()
    input("ok?")
    bb.stop()
    dns.stop()
    # 
    # 
    # sleep(4)
    # 
    # main()

