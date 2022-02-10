import subprocess
import re

def get_mac_addresses(ip_addresses):

            for ip_address in ip_addresses:
                subprocess.Popen(["ping", "-c 1", ip_address], stdout=subprocess.PIPE)

            proc = subprocess.Popen("arp -a", stdout=subprocess.PIPE)

            data = proc.communicate()[0]

            results = []

            ip_addresses_as_bytes = []
            for ip_addresse in ip_addresses:
                ip_addresses_as_bytes.append(str.encode(ip_addresses))

            ip_addresses_as_bytes = str.encode(ip_addresses)
            type(ip_addresses_as_bytes)

            for ip_address_as_bytes in ip_addresses_as_bytes[:]:
                if ip_address_as_bytes in data:

                    ip_data = data[data.find(ip_address_as_bytes):]

                    mac = re.search(r"(([a-f\d]{1,2}:){5}[a-f\d]{1,2})", ip_data)

                    if mac is None:
                        mac = re.search(r"(([a-f\d]{1,2}-){5}[a-f\d]{1,2})", ip_data)

                    if mac is not None:
                        mac = mac.groups()[0].replace('-', ':').upper()

                    else:
                        mac = '00:00:00:00:00:00'

                    ip_addresses = ip_addresses_as_bytes.decode()
                    type(ip_addresses)  # ensure it is string representation

                    ip_address = ip_address_as_bytes.decode()
                    type(ip_address)  # ensure it is string representation

                    ip_addresses.remove(ip_address)

                    results += [[ip_address, mac]]

                return results


if __name__ == '__main__':
    print(get_mac_addresses("192.168.4.96"))