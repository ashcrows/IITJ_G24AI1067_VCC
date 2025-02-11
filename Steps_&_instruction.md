This guide covers the steps to set up three Fedora VMs using VirtualBox. VM1 and VM2 will host a Python microservice, while VM3 will act as a secure gateway for internet access.

---

## **Overview of the Setup**

### **Objective**

- **VM1 and VM2**: Host a Python microservice application that communicates to retrieve system hardware details from both VMs and displays them in styled web pages accessible via local web browsers.
- **VM3 (Gateway)**: Acts as a secure gateway for VM1 and VM2:
  - Provides internet access exclusively to VM1 and VM2.
  - Not accessible to any other VMs or third parties.
  - VM1 and VM2 cannot access the internet directly; they must go through VM3.

### **Network Topology**

```
________________________________________________
|                 (Firewall)                   |
| [VM1]  <--->  [VM3 (Gateway)]  <--->  [VM2]  |
|                   | |                        | 
|                   | |                        |
|___________________|_|________________________|
                    | |
         <------ Internet ------>
```

---

## **Step-by-Step Guide**

### **Step 1: Install VirtualBox and Download Fedora OS**

#### **1. Install VirtualBox**

- **Download**: Visit the [official VirtualBox website](https://www.virtualbox.org/wiki/Downloads) and download the appropriate version for your host operating system.
- **Install**: Follow the installation instructions provided on the website.

#### **2. Download Fedora ISO**

- **Download**: Go to the [Fedora Workstation download page](https://getfedora.org/en/workstation/download/) and download the latest Fedora Workstation ISO.

---

### **Step 2: Create the Virtual Machines**

We'll create three VMs: **VM1**, **VM2**, and **VM3 (Gateway)**.

#### **1. Create VM1**

- **Open VirtualBox** and click on **“New”**.
- **Name**: `VM_fedora_1`.
- **Type**: `Linux`.
- **Version**: `Fedora (64-bit)`.
- **Memory Size**: Allocate at least **2048 MB** (2 GB).
- **Hard Disk**: Create a virtual hard disk now.
  - **File Type**: VDI (VirtualBox Disk Image).
  - **Storage**: Dynamically allocated.
  - **Size**: **20 GB**.

#### **2. Create VM2**

- **Repeat the steps above**, naming this VM `VM_fedora_2`.

#### **3. Create VM3 (Gateway)**

- **Create a new VM** named `VM_Fedora_Gateway` following the same steps.

---

### **Step 3: Install Fedora on Each VM**

#### **1. Attach the Fedora ISO**

- For each VM:
  - **Right-click** on the VM → **Settings** → **Storage**.
  - Under **Controller: IDE**, select **Empty**.
  - Click on the **disk icon** on the right → **Choose a disk file...**.
  - Select the downloaded Fedora ISO.

#### **2. Start Each VM and Install Fedora**

- **Start** each VM.
- **Boot Menu**: Select **"Start Fedora-Workstation-Live"**.
- Once the live environment loads, click **"Install to Hard Drive"**.
- **Installation Steps**:
  - **Language Selection**: Choose your preferred language.
  - **Time & Date**, **Keyboard**, **Network & Hostname**: Configure if necessary.
  - **Installation Destination**: Use default settings unless you prefer custom partitioning.
- **User Creation**:
  - **Root Password**: Set a strong password.
  - **User Account**: Create a user (e.g., `vm_fedora_1`) with administrator privileges.
- **Complete Installation** and **Reboot**.

#### **3. Update Each VM**

- **Log in** to each VM.
- **Open Terminal** and run:

  ```bash
  sudo dnf update -y
  ```

---

### **Step 4: Configure Network Settings in VirtualBox**

#### **1. Network Configuration for VM1 and VM2**

- **Go to VM Settings** → **Network**.
- **Adapter 1**:
  - **Enable Network Adapter**: Checked.
  - **Attached to**: **Internal Network**.
  - **Name**: `intnet`.
- **Adapters 2-4**: Disabled.

#### **2. Network Configuration for VM3 (Gateway)**

- **Adapter 1** (Internal Network):
  - **Enable Network Adapter**: Checked.
  - **Attached to**: **Internal Network**.
  - **Name**: `intnet`.
- **Adapter 2** (NAT):
  - **Enable Network Adapter**: Checked.
  - **Attached to**: **NAT`.
- **Adapters 3-4**: Disabled.

---

### **Step 5: Configure Network Settings in Fedora**

We'll assign static IP addresses to each VM using `nmcli`.

#### **Note**: In Fedora 33 and later, the traditional network-scripts are deprecated. We'll use `nmcli` to configure network connections.

#### **1. Identify Network Interfaces and Connection Names**

- **On Each VM (VM1, VM2, VM3)**:
  - **Open Terminal**.
  - Run:

    ```bash
    nmcli device status
    ```

  - **Note**:
    - **DEVICE**: The interface name (e.g., `enp0s3`).
    - **TYPE**: Should be `ethernet` for wired connections.
    - **CONNECTION**: The name of the connection profile (e.g., `Wired connection 1`).

#### **2. Configure VM1**

- **Connection Name**: Assume it's `Wired connection 1` (adjust if different).
- **Set a Static IP**:

  ```bash
  sudo nmcli connection modify 'Wired connection 1' \
  ipv4.addresses 192.168.56.101/24 \
  ipv4.gateway 192.168.56.100 \
  ipv4.dns 8.8.8.8 \
  ipv4.method manual
  ```

- **Restart the Network Connection**:

  ```bash
  sudo nmcli connection down 'Wired connection 1'
  sudo nmcli connection up 'Wired connection 1'
  ```

- **Verify Configuration**:

  ```bash
  ip addr show
  ```

- **Check Connectivity**:

  ```bash
  ping -c 4 192.168.56.100
  ```

#### **3. Configure VM2**

- **Set a Static IP**:

  ```bash
  sudo nmcli connection modify 'Wired connection 1' \
  ipv4.addresses 192.168.56.102/24 \
  ipv4.gateway 192.168.56.100 \
  ipv4.dns 8.8.8.8 \
  ipv4.method manual
  ```

- **Restart the Network Connection**:

  ```bash
  sudo nmcli connection down 'Wired connection 1'
  sudo nmcli connection up 'Wired connection 1'
  ```

- **Verify Configuration**:

  ```bash
  ip addr show
  ```

- **Check Connectivity**:

  ```bash
  ping -c 4 192.168.56.100
  ```

#### **4. Configure VM3 (Gateway)**

- **Connection Name**: Use the one associated with the internal interface (`enp0s8`).
- **Set a Static IP**:

  ```bash
  sudo nmcli connection modify 'Wired connection 1' \
  ipv4.addresses 192.168.56.100/24 \
  ipv4.method manual
  ```

- **Restart the Network Connection**:

  ```bash
  sudo nmcli connection down 'Wired connection 1'
  sudo nmcli connection up 'Wired connection 1'
  ```

- **Ensure IP Forwarding is Enabled**:

  ```bash
  sudo sysctl -w net.ipv4.ip_forward=1
  ```

  - **Make Permanent**:

    ```bash
    echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf
    ```

---

### **Step 6: Configure Firewall and NAT on VM3**

We need VM3 to act as a router, forwarding traffic from VM1 and VM2 to the Internet.

#### **1. Install and Enable Firewalld**

- **Install Firewalld**:

  ```bash
  sudo dnf install firewalld -y
  ```

- **Start and Enable Firewalld**:

  ```bash
  sudo systemctl start firewalld
  sudo systemctl enable firewalld
  ```

#### **2. Configure Masquerading (NAT)**

- **Enable Masquerading**:

  ```bash
  sudo firewall-cmd --permanent --add-masquerade
  ```

- **Identify Network Interfaces**:

  ```bash
  ip addr
  ```

  - **External Interface**: Connected to NAT (e.g., `enp0s3`).
  - **Internal Interface**: Connected to `intnet` (e.g., `enp0s8`).

- **Add NAT Rules**:

  ```bash
  # Replace 'enp0s3' and 'enp0s8' with your actual interface names
  sudo firewall-cmd --permanent --direct --add-rule ipv4 nat POSTROUTING 0 -o enp0s3 -j MASQUERADE
  sudo firewall-cmd --permanent --direct --add-rule ipv4 filter FORWARD 0 -i enp0s8 -o enp0s3 -j ACCEPT
  sudo firewall-cmd --permanent --direct --add-rule ipv4 filter FORWARD 0 -i enp0s3 -o enp0s8 -m state --state RELATED,ESTABLISHED -j ACCEPT
  ```

- **Reload Firewall Configuration**:

  ```bash
  sudo firewall-cmd --reload
  ```

---

### **Step 7: Test Internet Connectivity from VM1 and VM2**

#### **1. Test Connectivity to VM3**

- **From VM1 and VM2**:

  ```bash
  ping -c 4 192.168.56.100
  ```

#### **2. Test Internet Access**

- **From VM1 and VM2**:

  ```bash
  ping -c 4 google.com
  ```

- If successful, the network is configured correctly.

---

### **Step 8: Deploy the Python Microservice**

We'll create a Flask application that displays system hardware details.

#### **1. Install Necessary Packages on VM1 and VM2**

```bash
sudo dnf install python3 python3-pip -y
pip3 install flask psutil
```

#### **2. Create the Application Directory**

```bash
mkdir ~/microservice
cd ~/microservice
```

#### **3. Create `app.py`**

```bash
nano app.py
```

- **Add the Following Code**:

  ```python
  from flask import Flask, render_template
  import platform
  import psutil

  app = Flask(__name__)

  @app.route('/')
  def index():
      info = {
          'Hostname': platform.node(),
          'System': platform.system(),
          'Release': platform.release(),
          'Version': platform.version(),
          'Machine': platform.machine(),
          'Processor': platform.processor(),
          'CPU Cores': psutil.cpu_count(logical=False),
          'Total RAM': f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
          'IP Address': psutil.net_if_addrs()['enp0s3'][0].address
      }
      return render_template('index.html', info=info)

  if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5000)
  ```

- **Note**: Replace `'enp0s3'` with your actual network interface name if different not the newtork name `'Wired Connection 1'` or `'Wired Connection 2'`.

#### **4. Create Templates Directory and `index.html`**

```bash
mkdir templates
nano templates/index.html
```

- **Add the Following HTML**:

  ```html
  <!DOCTYPE html>
  <html>
  <head>
      <title>System Information</title>
      <style>
          body {
              font-family: Arial, sans-serif;
              background-color: #f0f0f0;
              margin: 0;
              padding: 0;
          }
          .container {
              width: 80%;
              margin: auto;
              overflow: hidden;
          }
          header {
              background: #50b3a2;
              color: #ffffff;
              padding-top: 30px;
              min-height: 70px;
              border-bottom: #e8491d 3px solid;
          }
          header h1 {
              text-align: center;
              margin: 0;
              text-transform: uppercase;
              font-size: 24px;
          }
          table {
              width: 100%;
              margin: 20px 0;
              border-collapse: collapse;
          }
          table, th, td {
              border: 1px solid #dddddd;
          }
          th, td {
              padding: 8px;
              text-align: left;
          }
          tr:nth-child(even) {
              background-color: #f2f2f2;
          }
      </style>
  </head>
  <body>
      <header>
          <h1>System Information</h1>
      </header>
      <div class="container">
          <table>
              {% for key, value in info.items() %}
              <tr>
                  <th>{{ key }}</th>
                  <td>{{ value }}</td>
              </tr>
              {% endfor %}
          </table>
      </div>
  </body>
  </html>
  ```

#### **5. Run the Microservice**

```bash
python3 app.py
```

- The application will start and listen on port `5000`.

---

### **Step 9: Access the Microservice from Local Browsers**

#### **1. On VM1**

- **Open Firefox**.
- **Navigate to**: `http://localhost:5000` or `http://192.168.56.101:5000`.
- **View**: The styled web page displaying system information.

#### **2. On VM2**

- **Open Firefox**.
- **Navigate to**: `http://localhost:5000` or `http://192.168.56.100:5000`.
- **View**: The styled web page displaying system information.

#### **3. Access Each Other's Microservice**

- **From VM1**, access VM2:

  - **Navigate to**: `http://192.168.56.102:5000`.

- **From VM2**, access VM1:

  - **Navigate to**: `http://192.168.56.101:5000`.

---

### **Step 10: Secure Communication and Access Control**

#### **1. Ensure VM3 Is Not Accessible to Other VMs**

- **By default**, only VM1 and VM2 are connected to the internal network `intnet`.
- **Other VMs** will not have access unless connected to the same internal network.

#### **2. Restrict Access on VM3**

- **Configure Firewall on VM3** to accept traffic only from VM1 and VM2.

- **Add Rich Rules to Firewalld**:

  ```bash
  sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.56.101" accept'
  sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.56.102" accept'
  sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" drop'
  sudo firewall-cmd --reload
  ```

- **Explanation**:
  - **Accepts** traffic from VM1 and VM2.
  - **Drops** all other traffic.

#### **3. Ensure VM1 and VM2 Access the Internet Only via VM3**

- **From VM1**:

  ```bash
  traceroute -m 5 google.com
  ```

- **Expected Output**: The first hop should be `192.168.56.100` (VM3).

#### **4. Disable SSH Access if Not Needed**

- **On VM3**, if SSH access is not required, disable SSH to enhance security:

  ```bash
  sudo systemctl stop sshd
  sudo systemctl disable sshd
  ```

---

### **Step 11: Test the Secure Setup**

#### **1. From VM1 and VM2**

- **Verify Internet Access**:

  ```bash
  ping -c 4 google.com
  ```

- **Access the Microservice on Each Other**.

#### **2. From Other VMs or Host Machine**

- **Attempt to Ping VM3**:

  ```bash
  ping -c 4 192.168.56.100
  ```

- **Expected**: No response, confirming that VM3 is not accessible.

#### **3. Shut Down VM3**

- **On VM3**:

  ```bash
  sudo shutdown now
  ```

- **From VM1 and VM2**, try to access the internet:

  ```bash
  ping -c 4 google.com
  ```

- **Expected**: Requests should fail, confirming that VM1 and VM2 rely on VM3 for internet access.

---

## **Final Verification**

- **VM1 and VM2** should have:
  - Internet access only through VM3.
  - The microservice running and accessible from their own browsers and from each other.
- **VM3** should:
  - Act as a secure gateway.
  - Not be accessible from other VMs or external sources.
  - Provide internet access exclusively to VM1 and VM2.

---

## **Conclusion**

We've now successfully:

- Set up three Fedora VMs in VirtualBox with accurate and corrected network configurations.
- Deployed a Python microservice application on VM1 and VM2 that communicates and displays hardware details.
- Configured VM3 as a secure gateway that is not accessible to other VMs or third parties.
- Ensured VM1 and VM2 can only access the internet through VM3.

---

Feel free to reach out if you have any questions or suggestions or need further assistance with any of the steps. Enjoy exploring your setting up virtual environment!
