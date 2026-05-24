---
title: "Tu?n 2 - Th?c hành và nghiên c?u các ki thu?t t?n công Kubernetes"
date: 2026-05-24 00:00:00 +0700
categories: ["Security Research"]
tags: ["Kubernetes", "Security"]
---


# Bu?i 1 : H?c trên KubernetesGoat

## D?ng cluster b?ng Kind

```
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.31.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
kind version
```


Cài kubectl
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


## Bài 1 : Gaining enviroment information

Bài d?u tiên là enum d? tìm ra các cred c?a h? th?ng

 H?u h?t các phiên b?n di?n toán khi ch?y ?ng d?ng d?u luu tr? thông tin nh?y c?m nhu secrets, api_keys, v.v. trong các bi?n môi tru?ng. Tuong t?, trong Kubernetes, h?u h?t m?i ngu?i luu tr? thông tin nh?y c?m nhu Kubernetes Secrets và các giá tr? Config trong các bi?n môi tru?ng và n?u k? t?n công có th? tìm th?y các l? h?ng ?ng d?ng nhu RCE (th?c thi mã t? xa) ho?c chèn l?nh thì bí m?t dó s? b? l?.


![](/assets/images/posts/Pasted%20image%2020260520152145.png)



Tru?c tiên thì t enum b?ng các l?nh co b?n

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


- Mình dang là root **trong container**, chua có nghia là root c?a node.
- Pod hi?n t?i: system-monitor-deployment-866f697c75-67qj4.
- Kubernetes API server: 10.96.0.1:443 ho?c DNS kubernetes.default.svc.
- Có nhi?u service n?i b?: build-code, internal-proxy, poor-registry, health-check.
- Có m?t secret l? ngay trong env:
    
    `K8S_GOAT_VAULT_KEY=k8s-goat-cd2da27224591da2b48ef83826a8a6c3`

![](/assets/images/posts/Pasted%20image%2020260520152824.png)

Ðây có v? là flag c?a bài
- Có thu m?c dáng nghi:
    
    `/host-system`
![](/assets/images/posts/Pasted%20image%2020260520153006.png)


Pod này có service account token du?c mount có namespace là default 

-> T? trong container này , ta có th? dùng identity c?a SA du?c g?n cho pod này. 


Chúng ta có th? khám phá container b?ng cách ch?y các l?nh khác nhau d? có th? enum d? có th? hi?u hon v? h? th?ng 

Chúng ta có th? get the container runtime b?ng cách ch?y nh?ng l?nh sau

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


 Access the environment variables, including Kubernetes secrets mounted and service names, ports, etc

```
printenv
```


Chúng ta qua bài ti?p theo là 

### K8s namespace bypass

![](/assets/images/posts/Pasted%20image%2020260520160125.png)

Ðây là m?t quan ni?m sai l?m l?n trong th? gi?i Kubernetes. H?u h?t m?i ngu?i cho r?ng khi có các namespace khác nhau trong Kubernetes và các tài nguyên du?c tri?n khai và qu?n lý, chúng s? an toàn và không th? truy c?p l?n nhau

Theo m?c d?nh K8S s? d?ng lu?c d? m?ng ph?ng , có nghia là các pod/service trong 1 cluster có th? nói chuy?n v?i nhau. Mà namespace ? trong cluster không có s? h?n ch? b?o m?t m?ng theo m?t d?nh. Anyone ? trong namespace d?u có th? nói chuy?n v?i namespacce khác . Trong tru?ng h?p sau dây thì chúng ta có th? bypass namespace d? có th? truy c?p tài nguyen c?a namespace khác


![](/assets/images/posts/Pasted%20image%2020260520164929.png)



![](/assets/images/posts/Pasted%20image%2020260520165306.png)


truy c?p vào bài lab 

![](/assets/images/posts/Pasted%20image%2020260520165313.png)

Ð?u tiên chúng ta c?n ph?i hi?u v? thông tin d?a ch? IP c?a cluster d? có th? ti?n hành recon quét các dãy m?ng c?a cluster

M?t s? l?nh co b?n d? có th? xem là : ip route , ifconfig , printenv,...

![](/assets/images/posts/Pasted%20image%2020260520165627.png)

![](/assets/images/posts/Pasted%20image%2020260520170058.png)


Pod IP: 10.244.0.15
Pod CIDR route: 10.244.0.0/24
Kubernetes DNS: 10.96.0.10
Service network th?y qua env: 10.96.x.x
DNS search: default.svc.cluster.local svc.cluster.local cluster.local

![](/assets/images/posts/Pasted%20image%2020260520171048.png)


RBAC dã ch?n ko cho t d?c service r?i

 Vì bài g?i ý “Kubernetes-Goat loves cache”, ta nghi có cache service. Cache thu?ng là Redis ho?c Memcached. Redis dùng port 6379.

zmap m?c d?nh **blacklist private ranges**, trong dó có 10.0.0.0/8, nên nó t? ch?n không cho scan. Vì v?y b?n b? do?n dó và scan redis port d? tìm du?c dãy m?ng c?a redis
![](/assets/images/posts/Pasted%20image%2020260520175958.png)

![](/assets/images/posts/Pasted%20image%2020260520180054.png)



5. Ngoài scan IP, Kubernetes còn h? tr? DNS service theo d?ng:

`<service-name>.<namespace>.svc.cluster.local`

nên ta phân gi?i du?c tên mi?n ch?ng t? r?ng  t? pod namespace default, b?n có th? resolve du?c service ? namespace secure-middleware. Gi? test port Redis:

![](/assets/images/posts/Pasted%20image%2020260520175226.png)

- Namespace default và secure-middleware khác nhau.
- Nhung pod hacker-container v?n truy c?p du?c Redis service namespace khác.
- Lý do: Kubernetes m?c d?nh flat network, namespace không t? t?o network isolation.
- Cách phòng th?: dùng **NetworkPolicy**, auth cho Redis/cache, không tin “internal only”.



### RBAC least privileges misconfiguration

![](/assets/images/posts/Pasted%20image%2020260520182649.png)

Trong th?c t?, chúng ta thu?ng th?y các nhà phát tri?n và nhóm DevOps c?p quy?n d?a trên tu  duy m?c d?nh cho t?t c? vì nghi r?ng nó s? ti?n l?i , t?c là c?p quy?n  nhi?u hon m?c c?n thi?t. Ði?u này d?n d?n vi?c k? t?n công có du?c nhi?u quy?n ki?m soát và d?c quy?n vu?t ngoài ph?m v? mà h? d? d?nh.

M?c tiêu bài này là 
Dùng service account trong pod d? g?i Kubernetes API
L?i d?ng RBAC quá r?ng
Ð?c secret k8svaultapikey
L?y k8s_goat_flag

Tru?c khi vào bài thì tui mu?n nói so v? khái ni?m v? ServiceAccount cung nhu RBAC 



**1. Xác d?nh service account token**

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

Decode ra thì l?y du?c flag

![](/assets/images/posts/Pasted%20image%2020260520183947.png)

1. **Pod có Kubernetes identity riêng**  
    Pod thu?ng du?c g?n m?t **ServiceAccount**. Token c?a ServiceAccount n?m trong:

`/var/run/secrets/kubernetes.io/serviceaccount/`

2. **Có shell trong pod là có th? g?i Kubernetes API**  
    N?u attacker có RCE/shell trong container, h? có th? l?y token dó r?i g?i API server:

`https://${KUBERNETES_SERVICE_HOST}`

3. **RBAC quy?t d?nh pod du?c làm gì trong cluster**  
    Token không t? nguy hi?m n?u RBAC ch?t. Nhung n?u ServiceAccount du?c c?p quy?n quá r?ng, attacker có th? list/get tài nguyên nh?y c?m.
    
4. **Secret trong Kubernetes ch? an toàn n?u quy?n d?c du?c ki?m soát t?t**  
    Trong bài này, ServiceAccount dáng l? ch? c?n quy?n v?i webhookapikey, nhung l?i d?c du?c c? vaultapikey.
    
5. **Least privilege r?t quan tr?ng**  
    Ðây là l?i th?c t? hay g?p: DevOps c?p quy?n “cho ti?n”, ví d? get/list secrets, r?i m?t pod b? compromise có th? bi?n thành credential theft trong cluster.



##  Bu?i 2 : K8s Lan Party

![](/assets/images/posts/Pasted%20image%2020260523150131.png)


![](/assets/images/posts/Pasted%20image%2020260523150204.png)

Ð?n v?i bài d?u tiên thì t s? làm 1 chall v? Recon , thì nhu b?n nào dã t?ng làm các bài lab v? leo thang thì vi?c d?u tiên d? có th? leo thang du?c thì chúng ta c?n ph?i recon ho?c enum d? có thêm 1 vài attack surfaces , nó giúp ích cho chúng ta trong các bu?c nâng cao d?c quy?n ti?p theo . 

Trong bài lab này , khi mà t dã compomise vào 1 Pod trong K8s , và bu?c ti?p theo là mu?n khám phá thêm các internal service d? có  th? m? r?ng ph?m vi leo thang.

Thông thu?ng K8s , các service thu?ng liên l?c v?i nhau qua DNS n?i b?. 

Hai lo?i thành ph?n chính c?a Kubernetes mà b?n s? quan tâm nh?t khi mu?n t?n công các ?ng d?ng khác có th? truy c?p du?c trên m?ng trong c?m là [pod](https://kubernetes.io/docs/concepts/workloads/pods/) và [service](https://kubernetes.io/docs/concepts/services-networking/service/) .

Pod là các nhóm g?m m?t ho?c nhi?u container dang ch?y, và dây là noi các ?ng d?ng m?ng n?i b? mà b?n mu?n t?n công s? ho?t d?ng. M?i Pod có d?a ch? IP internal cluster du?c liên k?t v?i chúng, và có m?t ho?c nhi?u c?ng m?ng du?c công khai mà b?n có th? s? d?ng d? giao ti?p v?i các ?ng d?ng m?ng.

Các service là nh?ng cách th?c thân thi?n d? hi?n th? các ?ng d?ng dang ch?y trên m?t ho?c nhi?u pod. Chúng cung có d?a ch? IP c?a cluster và m?t ho?c nhi?u c?ng du?c hi?n th?, cung nhu nhi?u b?n ghi DNS liên k?t du?c c?u hình trong trình phân gi?i DNS c?a c?m. Vi?c truy c?p ?ng d?ng b?ng d?ch v? so v?i truy c?p tr?c ti?p vào pod thu?ng tuong t? nhau, tuy nhiên các service  có thêm các tính nang khám phá có th? h?u ích cho chúng ta.

Ð?a ch? IP du?c s? d?ng cho các pod thu?ng n?m trong m?t d?i m?ng riêng bi?t, khác v?i d?a ch? IP c?a các d?ch v?.

Gi? chúng ta dã xác d?nh du?c nh?ng gì mình c?n tìm, hãy cùng xem xét m?t s? phuong pháp có th? s? d?ng d? xác d?nh các thành ph?n này.


Ð?u tiên chúng ta s? ki?m tra các bi?n môi tru?ng , chúng thu?ng ch?a d?a  ch?  ip ,port c?a các  service khác trong cluster  . 


![](/assets/images/posts/Pasted%20image%2020260523152812.png)


Ngoài ra b?n có th? l?y d?a ch? IP c?a c?m là các t?p `/etc/hosts`(cung c?p d?a ch? IP c?c b? c?a pod, mà b?n cung có th? l?y t? các l?nh `ip`ho?c `ifconfig`) và `/etc/resolv.conf`(cung c?p d?a ch? máy ch? DNS c?a c?m và các mi?n tìm ki?m DNS, t? dó suy ra namespace c?a pod).

Ngoài ra b?n cung có th? l?y các SA token c?a pod ho?c ra tìm các namespace c?a pod dang ch?y . https://thegreycorner.com/2023/12/13/kubernetes-internal-service-discovery.html#kubernetes-dns-to-the-partial-rescue


Ti?p t?c v?i bài này thì chúng ta có th? s? d?ng 1 cái tool dnscan https://gist.github.com/nirohfeld/c596898673ead369cb8992d97a1c764e d? có th? quét 

![](/assets/images/posts/Pasted%20image%2020260523153737.png)

Khi chúng ta ki?m tra b?ng env thì có th? th?y r?ng  IP c?a API server c?a K8s là 10.100.0.1 port là 443 

![](/assets/images/posts/Pasted%20image%2020260523154220.png)

k?t qu? **Hostname:** `getflag-service.k8s-lan-party.svc.cluster.local.`

Cái tên **"getflag-service"** chính là noi ch?a Flag ho?c mã d? vu?t qua th? thách này.

![](/assets/images/posts/Pasted%20image%2020260523154415.png)




![](/assets/images/posts/Pasted%20image%2020260523154614.png)


T?i ph?n ti?p theo là ph?n finding neighbour 

 Thì theo nhu mình tìm hi?u sidecar container là m?t container ch?y "kèm" theo container chính trong cùng m?t Pod.
- **M?c dích:** Nó không th?c hi?n logic chính c?a ?ng d?ng mà cung c?p các d?ch v? h? tr? nhu: ghi log, giám sát, ho?c **b?o m?t**

Vì các container n?m trong cùng m?t **Kubernetes Pod** s? dùng chung m?t **network namespace**, chúng s? chia s? hoàn toàn giao di?n m?ng (network interfaces), loopback adapter (localhost) và d?a ch? IP v?i nhau.

N?u có m?t container khác dang ch?y ng?m ngay bên c?nh b?n trong Pod này, m?i d? li?u m?ng mà nó g?i ho?c nh?n v?i các d?ch v? n?i b? d?u có th? xem t? chính container c?a b?n.


```
tcpdump -A
```

![](/assets/images/posts/Pasted%20image%2020260523155633.png)

Và dây là flag

Hãy d?m b?o r?ng giao ti?p gi?a các Pod luôn du?c mã hóa. Cách don gi?n nh?t d? b?t d?u mã hóa giao ti?p gi?a các Pod là s? d?ng [service mesh](https://www.techtarget.com/searchitoperations/definition/service-mesh) .


![](/assets/images/posts/Pasted%20image%2020260523155755.png)


giao th?c này ra d?i t? th?i k? mà ki?m soát truy c?p (access control) ch? d?a vào m?ng ,nghia l à mình ko c?n xác th?c b?ng thông tin  dang nh?p . Tui tham kh?o trên m?ng thì nghi ngay t?i NFS , ho?c AWS EFS

![](/assets/images/posts/Pasted%20image%2020260523160134.png)


![](/assets/images/posts/Pasted%20image%2020260523160237.png)

Dùng công c? NFS Client d? "bypass" quy?n

Trong môi tru?ng này có s?n công c? `nfs-ls` và `nfs-cat` (thu?c b? `libnfs`). Giao th?c NFSv4 cho phép chúng ta truy?n tham s? `uid=0` (Root) và `gid=0` tr?c ti?p qua chu?i k?t n?i d? ép server nh?n di?n mình là Root

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

Phuong pháp b? qua này cho phép b?t k? ngu?i dùng nào có userID 1337 d?u có th? bypass b? l?c proxy c?a Istio, t? dó kích ho?t chính sách ?y quy?n. May m?n thay, l?n này chúng ta là ngu?i dùng root trong h? th?ng, nghia là chúng ta có th? t?o m?t ngu?i dùng khác và d?t userID là 1337.


![](/assets/images/posts/Pasted%20image%2020260523161337.png)



![](/assets/images/posts/Pasted%20image%2020260523161517.png)


Ð?u tiên ch?y dns scan 

![](/assets/images/posts/Pasted%20image%2020260523161701.png)

Kyverno là công c? qu?n lý chính sách (Policy Engine) dành riêng cho Kubernetes, giúp b?n xác th?c, ch?nh s?a và kh?i t?o tài nguyên b?ng ngôn ng? **YAML** quen thu?c. Thay vì h?c ngôn ng? ph?c t?p, Kyverno cho phép d?i ngu DevOps t? d?ng hóa vi?c b?o m?t và chu?n hóa c?u hình cluster m?t cách don gi?n, hi?u qu? và c?c k? g?n nh?.

D?a trên chall chính sách này dang th?c hi?n tính nang **Mutation**: t? d?ng chèn giá tr? bí m?t (secret) vào bi?n môi tru?ng `FLAG` cho b?t k? Pod nào du?c t?o trong namespac

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


Vì tôi mình bi?t v? admission controllers and mutating webhooks, nên mình ngay l?p t?c hi?u du?c k? v?ng. Du?i dây là so d? mô t? cách th?c ho?t d?ng.

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

Bây gi? c?u trúc dã chu?n hóa, b?n ch?y l?nh `curl` này d? ép Kyverno tr? flag

```
curl -X POST -H "Content-Type: application/json" --data @pod.json https://kyverno-svc.kyverno/mutate -k
```

![](/assets/images/posts/Pasted%20image%2020260523162910.png)



![](/assets/images/posts/Pasted%20image%2020260523162740.png)


Trong c?m Kubernetes này, qu?n tr? viên dùng **Kyverno** d? t? d?ng hóa m?t vi?c:

- H? cài m?t chính sách (Policy) quy d?nh: _"B?t k? ai t?o m?t Pod (vùng ch?a ?ng d?ng) n?m trong namespace tên là `sensitive-ns`, Kyverno s? t? d?ng chèn thêm m?t bi?n môi tru?ng ch?a Flag bí m?t vào Pod dó"_.
    

Thông thu?ng, ngu?i dùng mu?n l?y Flag thì ph?i có quy?n dùng l?nh `kubectl` d? t?o m?t Pod th?t trong namespace `sensitive-ns`, sau dó vào Pod dó d? d?c bi?n môi tru?ng. Nhung ? dây, b?n **không có quy?n** t?o Pod th?t.


Kyverno ho?t d?ng d?a trên co ch? **Mutating Webhook** (m?t d?ch v? m?ng ch?y ng?m). Khi có yêu c?u t?o Pod, Kubernetes API Server s? g?i m?t gói tin d? li?u c?u hình (d?ng JSON) d?n Webhook này c?a Kyverno d? nó ch?nh s?a.

Cái sai nghiêm tr?ng c?a ngu?i qu?n tr? ? dây là: **H? m?  d?ch v? Webhook này (`https://kyverno-svc.kyverno/mutate`) cho t?t c? các Pod n?i b? truy c?p** mà không h? c?u hình tu?ng l?a m?ng (Network Policy) hay xác th?c mTLS d? ch?n l?i.


1. **G?i c?u hình nháp:** B?n dùng l?nh `curl` d? g?i m?t file JSON c?u hình nháp (`pod.json`) gi? v? nhu dang mu?n t?o m?t Pod trong namespace `sensitive-ns` th?ng t?i c?ng d?ch v? c?a Kyverno.
    
2. **Kyverno b? l?a:** Kyverno nh?n du?c gói tin, không h? ki?m tra xem ai g?i, c? th?y có yêu c?u t?o Pod ? `sensitive-ns` là nó t? d?ng làm theo l?p trình: **Chèn ngay do?n mã ch?a Flag vào c?u hình** r?i g?i tr? ngu?c l?i cho b?n.
    
3. **L?y Flag:** Ðo?n mã ch?a Flag tr? v? du?c mã hóa du?i d?ng Base64 d? b?o toàn c?u trúc d? li?u, b?n ch? c?n mang chu?i dó di gi?i mã (`base64 -d`) là nhìn th?y Flag l? ra rõ m?m m?t.




